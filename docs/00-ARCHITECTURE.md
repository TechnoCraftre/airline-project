# 00 — Architecture and why each component exists

| Layer | Component | Purpose | Interview concept |
|---|---|---|---|
| Source | GitHub | Version control and pull requests | Git workflow |
| CI | GitHub Actions | Test, lint, build, security scan | CI/CD |
| Artifact | ECR | Immutable container registry | artifact promotion |
| IaC | Terraform | AWS infrastructure | desired state |
| Network | VPC | Public/private network separation | networking |
| Compute | EKS | Kubernetes control plane + workers | orchestration |
| Database | RDS PostgreSQL | Managed relational persistence | HA/backup/scaling |
| Secrets | Secrets Manager + ESO | Secret source and sync | secret hygiene |
| Ingress | AWS Load Balancer Controller | Kubernetes Ingress → ALB | cloud integration |
| Packaging | Helm | Kubernetes release management | deployment lifecycle |
| Scaling | HPA + Metrics Server | pod autoscaling | NFR/reliability |
| Monitoring | Prometheus/Grafana | metrics and dashboards | observability |
| Security | Trivy + IAM/OIDC | image and identity security | DevSecOps |

## Traffic flow

```text
Internet
   |
   v
AWS ALB
   |
   v
Kubernetes Ingress
   |
   v
ClusterIP Service
   |
   +----> Pod 1 ----+
   |                |
   +----> Pod 2 ----+----> RDS PostgreSQL
   |                |
   +----> Pod N ----+

Pod startup:
  Kubernetes -> readiness probe -> /ready -> PostgreSQL

Metrics:
  Pod /metrics -> ServiceMonitor -> Prometheus -> Grafana

Secrets:
  Terraform -> AWS Secrets Manager -> External Secrets Operator -> Kubernetes Secret -> Pod
```

## Reliability controls

- 2 application replicas
- rolling update with `maxUnavailable: 0`
- readiness probe
- liveness probe
- resource requests/limits
- HPA
- PDB
- private RDS
- ECR image scanning
- Trivy CI gate

## Deliberate lab trade-offs

This is intentionally small enough to run and understand. It uses one NAT gateway, small instances, non-Multi-AZ RDS and public EKS API access. These are learning-environment choices, not universal production recommendations.
