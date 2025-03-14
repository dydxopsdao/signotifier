output "lambda_endpoint" {
  value = aws_lambda_function_url.signotifier_url.function_url
}

output "signing_key_public" {
  value = data.aws_kms_public_key.signing_key.public_key_pem
}

output "github_invoker_role_arn" {
  value = aws_iam_role.github_invoker.arn
}
