output "lambda_endpoint" {
  value = aws_lambda_function_url.notify_validators_url.function_url
}

output "signing_key_public" {
  value = data.aws_kms_public_key.signing_key.public_key_pem
}

