variable "sender" {
  type        = string
  description = "Sender name and/or address, e.g.: Lorem <lorem@ipsum.dolor>"
}

variable "codebuild_github_repo" {
  type        = string
  description = "URL of the source GitHub repository for AWS CodeBuild. It should end with `.git`."
}

variable "codebuild_github_branch" {
  type        = string
  description = "Repository branch that should be used by CodeBuild."
}

variable "github_org" {
  description = "GitHub organization name"
  type        = string
  default     = "dydxopsdao"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "signotifier"
}
