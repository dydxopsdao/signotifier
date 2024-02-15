# === IAM role ===

data "aws_iam_policy_document" "lambda_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "lambda-runner"
  assume_role_policy = data.aws_iam_policy_document.lambda_role.json
}

# === Permissions ===

data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "kms:Sign",
      "ses:SendRawEmail",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "lambda_permissions" {
  name        = "lambda-permissions"
  path        = "/"
  description = "Permissions for lambda"
  policy      = data.aws_iam_policy_document.lambda_permissions.json
}

resource "aws_iam_role_policy_attachment" "lambda_permissions" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_permissions.arn
}

# === Lambda function ===

locals {
  lambda_function_name = "signotifier"
}

resource "aws_lambda_function" "signotifier" {
  function_name    = local.lambda_function_name
  package_type     = "Image"
  image_uri        = "${aws_ecr_repository.signotifier.repository_url}:latest"
  role             = aws_iam_role.iam_for_lambda.arn
  timeout          = 90
  source_code_hash = timestamp() # Force update on every apply

  environment {
    variables = {
      EMAIL_AWS_REGION    = data.aws_region.current.name
      SENDER              = var.sender
      RECIPIENTS          = var.recipients
      KMS_SIGNING_KEY_ID  = aws_kms_key.signing_key.key_id
    }
  }

  depends_on = [data.external.build_image_with_codebuild]
}

resource "aws_lambda_function_url" "signotifier_url" {
  function_name      = aws_lambda_function.signotifier.function_name
  authorization_type = "AWS_IAM"
}
