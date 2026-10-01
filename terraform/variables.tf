variable "aws_region" {
  description = "AWS region for the lab"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  type    = string
  default = "airline-devops-lab"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "kubernetes_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.35"
}

variable "github_repository" {
  description = "GitHub repository in owner/name form for OIDC deployment trust"
  type        = string
}

variable "db_name" {
  type    = string
  default = "airline"
}

variable "db_username" {
  type    = string
  default = "airlineapp"
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}
