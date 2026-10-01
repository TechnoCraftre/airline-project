# 01 — Quickstart: Windows + GitHub + AWS CloudShell

## What you install locally

Nothing beyond what you already have:

- VS Code
- Git
- GitHub access

Do **not** install Docker Desktop, Terraform, AWS CLI, kubectl or Helm on Windows for this lab.

## What runs in AWS CloudShell

- AWS CLI
- Docker
- Terraform
- kubectl
- Helm
- Git

## Phase 0 — Push the repository

In the VS Code terminal:

```powershell
git add .
git commit -m "Build production-style airline DevOps lab"
git push
```

Then open GitHub → Actions. The `airline-api-ci` workflow should run.

The CI workflow deliberately does not push to ECR yet. This prevents an ECR credential/configuration problem from blocking basic CI.

## Phase 1 — Open AWS CloudShell

AWS Console → CloudShell.

Run:

```bash
aws sts get-caller-identity
git --version
docker --version
kubectl version --client
```

If Terraform or Helm are missing, follow `02-CLOUDSHELL-TOOLS.md`.

## Phase 2 — Clone the repository

In CloudShell:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Verify:

```bash
ls
```

You should see `app`, `helm`, `terraform`, `k8s`, `docs` and `.github`.

## Phase 3 — Validate the application before AWS

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r app/requirements.txt
pytest -q
```

Expected result:

```text
3 passed
```

## Phase 4 — Build the image in CloudShell

```bash
docker build --pull -f app/Dockerfile -t airline-api:local app
docker run --rm -d --name airline-api-test -p 8000:8000 airline-api:local
curl http://127.0.0.1:8000/health
docker rm -f airline-api-test
```

Expected health response contains `"status":"ok"`.

## Phase 5 — Terraform

Copy the example variables file:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit it:

```bash
nano terraform.tfvars
```

Replace:

```hcl
github_repository = "YOUR_GITHUB_USERNAME/YOUR_REPOSITORY"
```

Then:

```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
```

Read the plan before applying it.

Apply:

```bash
terraform apply tfplan
```

This creates:

- VPC with public/private subnets
- one NAT gateway
- ECR
- EKS 1.35
- two-node managed node group
- private RDS PostgreSQL
- Secrets Manager secret
- IRSA roles
- GitHub OIDC provider and ECR push role

## Phase 6 — Connect kubectl to EKS

```bash
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name airline-devops-lab-eks

kubectl get nodes
kubectl get pods -A
```

Expected: two worker nodes in `Ready` state.

## Phase 7 — Push the first image to ECR

Get the repository URL:

```bash
terraform output -raw ecr_repository_url
```

Login:

```bash
REGISTRY=$(terraform output -raw ecr_repository_url | cut -d/ -f1)
REPOSITORY=$(terraform output -raw ecr_repository_url | cut -d/ -f2-)
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin "$REGISTRY"
```

Build and push:

```bash
IMAGE_TAG=$(git rev-parse --short HEAD)
docker build --pull -f ../app/Dockerfile -t "$REGISTRY/$REPOSITORY:$IMAGE_TAG" ../app
docker push "$REGISTRY/$REPOSITORY:$IMAGE_TAG"
```

## Phase 8 — Install platform controllers

Follow `03-PLATFORM-COMPONENTS.md` in this order:

1. AWS Load Balancer Controller
2. External Secrets Operator
3. Metrics Server
4. Prometheus/Grafana

Do not deploy the application before External Secrets Operator is ready.

## Phase 9 — Deploy application

Create the namespace:

```bash
kubectl create namespace airline --dry-run=client -o yaml | kubectl apply -f -
```

Apply the secret integration:

```bash
kubectl apply -f k8s/secret-store.yaml
kubectl apply -f k8s/external-secret.yaml
```

Wait for the secret:

```bash
kubectl get externalsecret -n airline
kubectl get secret airline-database -n airline
```

Deploy Helm:

```bash
ECR_URL=$(terraform -chdir=terraform output -raw ecr_repository_url)
IMAGE_TAG=$(git rev-parse --short HEAD)

helm upgrade --install airline-api ./helm/airline-api \
  --namespace airline \
  --create-namespace \
  --set image.repository="$ECR_URL" \
  --set image.tag="$IMAGE_TAG" \
  --wait \
  --timeout 10m
```

## Phase 10 — Validate production path

```bash
kubectl get pods -n airline
kubectl get svc -n airline
kubectl get ingress -n airline
kubectl get hpa -n airline
```

Wait for the ALB hostname:

```bash
kubectl get ingress -n airline -w
```

When the ADDRESS appears:

```bash
ALB=$(kubectl get ingress airline-api -n airline -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "$ALB"
curl "http://$ALB/health"
curl "http://$ALB/ready"
curl "http://$ALB/metrics | head"
```

The final command should be:

```bash
curl "http://$ALB/metrics" | head
```

## Phase 11 — Test a real booking

```bash
curl -X POST "http://$ALB/bookings" \
  -H 'Content-Type: application/json' \
  -d '{"passenger_name":"Riya Sharma","flight_number":"AI101","seat":"12A"}'
```

Expected status: `201` and `CONFIRMED`.

## Phase 12 — Interview practice

Do not stop at “it works”. Perform every drill in `04-FAILURE-DRILLS.md` and record:

1. Symptom
2. First command
3. Evidence
4. Root cause
5. Fix
6. Prevention
7. Rollback decision

That is the material you use for real-time DevOps interview questions.
