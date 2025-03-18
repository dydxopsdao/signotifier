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

There are several ways to invoke the Lambda function.

For details about Lambda invocation and authentication methods see:

* https://docs.aws.amazon.com/lambda/latest/dg/urls-invocation.html#urls-invocation-basics
* https://docs.aws.amazon.com/lambda/latest/dg/urls-auth.html.

### GitHub Actions

This is the preferred method.

To send a message to the default recipients (i.e. the ones defined in the `RECIPIENTS` variable), go to the [Send to Default Recipients](https://github.com/dydxopsdao/signotifier/actions/workflows/send-default.yml) action, press `Run workflow`, and fill in the `subject` and `content` fields.

To send a message to custom recipients, go to the [Send to Custom Recipients](https://github.com/dydxopsdao/signotifier/actions/workflows/send-custom.yml) action, press `Run workflow`, and fill in the `subject`, `content`, and `recipients` (comma-separated list of emails) fields.

Note: in order to include newlines in the `content` field, you need to type `\n` instead of a newline. For example:

```
subject:Test
content: This is a test\nSecond line
```

In order to edit the list of recipients, edit the `RECIPIENTS` variable in the [repository's variables](https://github.com/dydxopsdao/signotifier/settings/variables/actions). Use comma-separated values.

### CLI

The Lambda function can be also invoked via CLI using `awscurl`.

Set up `~/.aws/config` in the following way:

```
[profile dydxopsdao]
region = ap-northeast-1
sso_start_url = https://dydxopsservices.awsapps.com/start/
sso_region = ap-northeast-1
sso_session = dydxopsdao
sso_account_id = <root account id>
sso_role_name = AdministratorAccess

[profile signotifier]
region = ap-northeast-1
role_arn = arn:aws:iam::<signotifier account id>:role/OrganizationAccountAccessRole
source_profile = dydxopsdao
```

Then a test call with `awscurl` could look like this:

```
AWS_PROFILE=signotifier awscurl https://x7x7ulg4w7mjnnwi7u4vj5ox7u0kyuvo.lambda-url.ap-northeast-1.on.aws/ \
--region ap-northeast-1 --service lambda \
-d '{"subject": "Signotifier test", "content": "Please lorem your ipsums.", "recipients": "test1@test.com,test2@test.com"}'
```

## Setup

### AWS account

It is recommended to created a dedicated AWS account for the project. This is a good practice for the sake of security and maintainability.

### SES

Set up Amazon SES by following their guide at: https://docs.aws.amazon.com/ses/latest/dg/setting-up.html#quick-start-verify-email-addresses .

### Lambda function

The Lambda function is deployed via Terraform.

The Lambda endpoint can be obtained from the Terraform output item: `lambda_endpoint`.

The combined length of subject and content must not exceed 4096 bytes due to RSA limitations.

To verify the signature created by the Lambda function run:

```
openssl dgst -sha256 -verify dydxops-pubkey.pem -signature signature.sig -sigopt rsa_padding_mode:pss message.txt
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
