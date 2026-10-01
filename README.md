# Airline Booking Platform — Cloud DevOps Lab

A production-style DevOps lab designed for hands-on interview preparation around an airline/travel technology workload.

> This is a personal lab, not Accelya production infrastructure. In interviews, describe it as a production-style project you built to practice the full software delivery and operations lifecycle.

## Architecture

GitHub → GitHub Actions → Test/Ruff → Docker build → Trivy → ECR → EKS → AWS Load Balancer Controller → ALB → FastAPI → RDS PostgreSQL

Supporting services: Terraform, Helm, AWS Secrets Manager, External Secrets Operator, Prometheus/Grafana, CloudWatch, HPA, IAM/OIDC.

## Cloud-first constraint

Windows only needs VS Code + Git/GitHub. Docker, AWS CLI, Terraform, kubectl and Helm are run in AWS CloudShell.

## Build order

1. Push this repository to GitHub.
2. Use AWS CloudShell for all cloud tooling.
3. Validate the application and Docker image.
4. Create ECR/VPC/EKS/RDS/IAM with Terraform.
5. Push the image to ECR.
6. Install AWS Load Balancer Controller and External Secrets Operator.
7. Deploy the application with Helm.
8. Validate ALB, RDS, readiness/liveness and HPA.
9. Add GitHub Actions OIDC deployment.
10. Perform failure drills and write RCAs.

See `docs/01-QUICKSTART.md` and `docs/02-INTERVIEW-GUIDE.md`.
