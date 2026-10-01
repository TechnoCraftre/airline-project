output "vpc_id" {
  value = module.vpc.vpc_id
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "database_secret_name" {
  value = aws_secretsmanager_secret.database.name
}

output "external_secrets_role_arn" {
  value = aws_iam_role.external_secrets.arn
}

output "load_balancer_controller_role_arn" {
  value = aws_iam_role.load_balancer_controller.arn
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}
