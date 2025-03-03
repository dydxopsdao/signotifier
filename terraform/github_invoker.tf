
# IAM role for Github Actions to invoke Lambda function
resource "aws_iam_role" "github_invoker" {
  name = "github_invoker"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Custom policy for additional Lambda permissions
resource "aws_iam_role_policy" "github_invoker_policy" {
  name = "github_invoker_policy"
  role = aws_iam_role.github_invoker.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
          "lambda:InvokeAsync"
        ]
        Resource = [
          aws_lambda_function.signotifier.arn
        ]
      }
    ]
  })
}
