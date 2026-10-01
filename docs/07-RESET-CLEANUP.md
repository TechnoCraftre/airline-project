# 07 — Cleanup / cost control

When you finish a session, the safest cost-control option is to destroy the lab when you no longer need it.

From CloudShell:

```bash
terraform -chdir=terraform plan -destroy
```

Review the plan carefully, then:

```bash
terraform -chdir=terraform destroy
```

Confirm all AWS resources are gone:

```bash
aws eks list-clusters --region ap-south-1
aws rds describe-db-instances --region ap-south-1 --query 'DBInstances[].DBInstanceIdentifier'
aws ecr describe-repositories --region ap-south-1 --query 'repositories[].repositoryName'
```

If you keep the environment running, remember that EKS, NAT Gateway and RDS can incur ongoing charges.
