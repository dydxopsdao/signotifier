resource "aws_kms_key" "signing_key" {
  description              = "RSA 4096 key for message signing"
  customer_master_key_spec = "RSA_4096"
  key_usage                = "SIGN_VERIFY"
}

data "aws_kms_public_key" "signing_key" {
  key_id = aws_kms_key.signing_key.key_id
}
