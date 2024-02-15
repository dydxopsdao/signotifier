# Signotifier

An AWS Lambda function that signs the input message with an asymmetric key and then sends it via email to a predefined set of recipients.

The dYdX Operations Subdao utilizes this tool to inform validators of critical events. This tool is designed to be universally applicable; interested parties can fork this repository, modify the sender information, and adapt it to their requirements. For details on licensing, please consult the LICENSE file.

The input should be a JSON with the following format:

```
{
    "subject": "The world on you depends",
    "content": "Please lorem your ipsums by tomorrow."
}
```

The outgoing emails will include the required message, along with its signature.

The signing key is RSA 4096 and the algorithm used is SHA-256 with the padding scheme PSS.

## Assumptions

* AWS account
* Terraform Cloud
* Terraform CLI installed locally

## Usage

The lambda function has to be invoked by an IAM user with the `lambda:InvokeFunctionUrl` permission in the project.
This could be done via CLI, SDK, or the bare API. A convenient tool for CLI calls is `awscurl`. 
An example call (change the URL and region accordingly):

```
 export AWS_ACCESS_KEY_ID=...
 export AWS_SECRET_ACCESS_KEY=...
awscurl https://x7x7ulg4w7mjnnwi7u4vj5ox7u0kyuvo.lambda-url.ap-northeast-1.on.aws/ \
--region ap-northeast-1 --service lambda \
-d '{"subject": "Signotifier test", "content": "Please lorem your ipsums."}'
```

For details about Lambda invocation and authentication methods see:

* https://docs.aws.amazon.com/lambda/latest/dg/urls-invocation.html#urls-invocation-basics
* https://docs.aws.amazon.com/lambda/latest/dg/urls-auth.html.


The Lambda endpoint can be obtained from the Terraform output item: `lambda_endpoint`.

The combined length of subject and content must not exceed 4096 bytes due to RSA limitations.

To verify the signature created by the Lambda function run:

```
openssl dgst -sha256 -verify dydxops-pubkey.pem -signature signature.sig -sigopt rsa_padding_mode:pss message.txt
```

## Setup

### AWS account

It is recommended to created a dedicated AWS account for the project. This is a good practice for the sake of security and maintainability.

### SES

Set up Amazon SES by following their guide at: https://docs.aws.amazon.com/ses/latest/dg/setting-up.html#quick-start-verify-email-addresses .

### IAM users

#### User for Terraform Cloud

Manually create an AWS IAM user that Terraform Cloud will impersonate to deploy the solution. Preferably use a dedicated AWS account.
Call it e.g.: `terraformer`. Go to:
`IAM -> Users -> [your new user] -> Permissions -> Add permissions -> Attach policies directly`
and add the following managed policies:

* AmazonEC2ContainerRegistryFullAccess
* AWSLambda_FullAccess
* IAMFullAccess
* AWSCodeBuildAdminAccess
* AWSKeyManagementServicePowerUser

#### Invoker user

To authenticate to the Lambda function you need an IAM user with appropriate permissions.
Create this user manually in the account where the function lives.
A simple IAM inline policy could look like this:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunctionUrl"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

### Terraform project

Set up a Terraform project in Terraform Cloud called `signotifier`. Configure the source repository.
Make sure to point the VCS trigger to the `/terraform` directory.

Add the following variables (note that some of them need to be of type `env` and some of type `terraform`):

Env vars:

* `AWS_ACCESS_KEY_ID` - your IAM user (e.g. terraformer)'s ID
* `AWS_SECRET_ACCESS_KEY` - your IAM user (e.g. terraformer)'s secret key
* `AWS_REGION` - where you want the Lambda function deployed

Terraform vars:

* `sender` - Sender name and/or address, e.g.: `Lorem <lorem@ipsum.dolor>`
* `recipients` - comma-separated list of emails
* `codebuild_github_repo` - URL of the source GitHub repository for AWS CodeBuild. It should end with `.git`
* `codebuild_github_branch` - Repository branch that should be used by CodeBuild

Create a _run_.

## Obtaining the public key

After the signing key is created in KMS, you can obtain its public key by inspecting
the Terraform Cloud's output entry `kms_key_id`.

For manual steps using CLI see:
https://aws.amazon.com/blogs/security/how-to-verify-aws-kms-asymmetric-key-signatures-locally-with-openssl/

## Testing

Prepare environment

```
python3 -m venv .python_venv
. ./.python_venv/bin/activate
pip install --upgrade pip
pip install -r ./src/requirements.txt
pip install pytest
```

Run tests

```
# . ./.python_venv/bin/activate
pytest
```
