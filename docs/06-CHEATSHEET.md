# 06 — One-page operations cheatsheet

## Pods

```bash
kubectl get pods -n airline
kubectl describe pod -n airline <pod>
kubectl logs -n airline <pod>
kubectl logs -n airline <pod> --previous
kubectl exec -it -n airline <pod> -- sh
```

## Deployment

```bash
kubectl get deploy -n airline
kubectl rollout status deployment/airline-api -n airline
kubectl rollout history deployment/airline-api -n airline
kubectl rollout undo deployment/airline-api -n airline
```

## Service/networking

```bash
kubectl get svc,endpoints -n airline
kubectl get ingress -n airline
kubectl describe ingress airline-api -n airline
kubectl get targetgroupbindings -n airline
```

## Resources

```bash
kubectl top nodes
kubectl top pods -n airline
kubectl get hpa -n airline
```

## Events

```bash
kubectl get events -A --sort-by=.lastTimestamp | tail -50
```

## Helm

```bash
helm list -A
helm status airline-api -n airline
helm history airline-api -n airline
helm rollback airline-api <REVISION> -n airline
```

## Terraform

```bash
terraform -chdir=terraform fmt -recursive
terraform -chdir=terraform validate
terraform -chdir=terraform plan
terraform -chdir=terraform apply
terraform -chdir=terraform output
```

## AWS

```bash
aws sts get-caller-identity
aws eks describe-cluster --name airline-devops-lab-eks --region ap-south-1
aws ecr describe-repositories --region ap-south-1
aws rds describe-db-instances --region ap-south-1
```

## Troubleshooting order

**User issue:** ALB → Ingress → Service → Endpoints → Pod → Readiness → Logs → DB.

**Pod issue:** status → events → current logs → previous logs → image → config → resources → probes.

**CI issue:** workflow step → dependency → build context → credentials → registry → artifact.

**Terraform issue:** validate → plan → identify exact resource → understand dependency/change → apply.
