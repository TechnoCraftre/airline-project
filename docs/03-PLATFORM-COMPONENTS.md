# 03 — EKS platform components

Run these commands in AWS CloudShell after Terraform creates EKS.

## A. AWS Load Balancer Controller

The controller converts Kubernetes Ingress resources into AWS Application Load Balancers. The current upstream project is v3.5.0.

Add the chart repository:

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update
```

Install the CRDs:

```bash
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller/crds?ref=master"
```

Install the controller using the IRSA role created by Terraform:

```bash
LBC_ROLE=$(terraform -chdir=terraform output -raw load_balancer_controller_role_arn)

helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --namespace kube-system \
  --set clusterName=airline-devops-lab-eks \
  --set serviceAccount.create=true \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"="$LBC_ROLE" \
  --set region=ap-south-1 \
  --set vpcId="$(terraform -chdir=terraform output -raw vpc_id 2>/dev/null || true)"
```

If the last `vpcId` value is empty, rerun without it; the controller can discover VPC information from the cluster:

```bash
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --namespace kube-system \
  --set clusterName=airline-devops-lab-eks \
  --set serviceAccount.create=true \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"="$LBC_ROLE" \
  --set region=ap-south-1
```

Verify:

```bash
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
```

## B. External Secrets Operator

The lab uses AWS Secrets Manager as the source of truth for database credentials.

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm repo update
```

Install the current chart line:

```bash
ESO_ROLE=$(terraform -chdir=terraform output -raw external_secrets_role_arn)

helm upgrade --install external-secrets external-secrets/external-secrets \
  --namespace external-secrets \
  --create-namespace \
  --set installCRDs=true \
  --set serviceAccount.create=true \
  --set serviceAccount.name=external-secrets \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"="$ESO_ROLE" \
  --wait \
  --timeout 10m
```

Verify:

```bash
kubectl get pods -n external-secrets
kubectl get crd | grep external-secrets
```

## C. Metrics Server

Metrics Server supplies the Kubernetes Metrics API used by HPA and `kubectl top`.

The current Metrics Server project documents 0.9.x as compatible with Kubernetes 1.34+, which covers this EKS 1.35 lab.

```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update

helm upgrade --install metrics-server metrics-server/metrics-server \
  --namespace kube-system \
  --set replicas=2 \
  --wait \
  --timeout 10m
```

Verify:

```bash
kubectl top nodes
kubectl top pods -n airline
```

## D. Prometheus + Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --version 91.8.2 \
  --set grafana.adminPassword='ChangeMe-Interview-Lab-123!' \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --wait \
  --timeout 15m
```

For a real production account, use a secret manager rather than placing a Grafana password in shell history.

Verify:

```bash
kubectl get pods -n monitoring
kubectl get servicemonitors -n airline
```

## Grafana access

```bash
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80
```

Open `http://localhost:3000` in your local browser while the CloudShell port-forward is active. Login:

- user: `admin`
- password: the password supplied during Helm installation

## Important troubleshooting principle

Do not immediately reinstall controllers. First inspect:

```bash
kubectl get pods -A
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace> --previous
kubectl get events -A --sort-by=.lastTimestamp | tail -50
```
