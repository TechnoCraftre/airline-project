# 04 — Failure drills and RCA practice

These drills are the part that turns the project into interview preparation.

## Drill 1 — CrashLoopBackOff

Change the deployment to intentionally crash:

```bash
helm upgrade airline-api ./helm/airline-api \
  -n airline \
  --reuse-values \
  --set env.APP_MODE=crash
```

Observe:

```bash
kubectl get pods -n airline
kubectl describe pod -n airline <pod-name>
kubectl logs -n airline <pod-name> --previous
```

Expected reasoning:

- Pod starts and application exits.
- Kubernetes restarts it.
- Restart count increases.
- Logs show `Intentional startup failure for incident drill`.

Recover:

```bash
helm upgrade airline-api ./helm/airline-api \
  -n airline \
  --reuse-values \
  --set env.APP_MODE=normal \
  --wait
```

Interview answer pattern:

> I first confirmed whether the failure was scheduling, image pull, or process-level. `describe` showed the pod was scheduled successfully, and `logs --previous` showed the application was exiting during startup. I corrected the configuration and watched the rollout before declaring recovery.

## Drill 2 — Readiness failure / simulated database outage

Scale the database connectivity failure by temporarily changing the secret to an invalid endpoint through a separate test secret, then observe `/ready` returning 503 and the pod becoming NotReady.

Commands:

```bash
kubectl get pods -n airline
kubectl describe pod -n airline <pod-name>
kubectl logs -n airline <pod-name>
curl http://<ALB>/ready
```

Reasoning:

- Liveness answers “is the process alive?”
- Readiness answers “should traffic be sent here?”
- A database failure should normally remove the pod from service rather than restart a healthy process.

## Drill 3 — Rollout regression

Deploy a bad image tag:

```bash
helm upgrade airline-api ./helm/airline-api \
  -n airline \
  --reuse-values \
  --set image.tag=does-not-exist
```

Observe:

```bash
kubectl get pods -n airline
kubectl describe pod -n airline <pod-name>
kubectl get events -n airline --sort-by=.lastTimestamp | tail -30
```

Look for `ErrImagePull` / `ImagePullBackOff`.

Recover using Helm history:

```bash
helm history airline-api -n airline
helm rollback airline-api <REVISION> -n airline --wait
kubectl rollout status deployment/airline-api -n airline --timeout=5m
```

## Drill 4 — High CPU and HPA

Generate requests from CloudShell:

```bash
ALB=$(kubectl get ingress airline-api -n airline -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

for i in {1..1000}; do
  curl -s "http://$ALB/health" >/dev/null &
done
wait
```

Watch:

```bash
kubectl top pods -n airline
kubectl get hpa -n airline -w
kubectl get pods -n airline -w
```

Explain:

- CPU requests define the HPA utilization baseline.
- HPA changes desired replica count.
- Deployment creates pods.
- Kubernetes scheduler places pods on available nodes.
- If nodes lack capacity, cluster autoscaling would be the next scaling layer; this lab deliberately keeps node autoscaling simple.

## Drill 5 — ALB returns 503

Check in this order:

```bash
kubectl get ingress -n airline
kubectl describe ingress airline-api -n airline
kubectl get targetgroupbindings -n airline
kubectl get endpoints -n airline
kubectl get pods -n airline
kubectl get events -A --sort-by=.lastTimestamp | tail -50
```

Reasoning chain:

ALB → Target Group → Service → Endpoint/Pod → readiness probe → application.

Do not start by restarting the ALB controller.

## Drill 6 — Security finding

Run locally/CI:

```bash
trivy fs --severity HIGH,CRITICAL --ignore-unfixed .
```

Then scan the image:

```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed airline-api:local
```

Interview reasoning:

1. Identify package and fixed version.
2. Determine whether the vulnerable component is actually reachable/exploitable.
3. Upgrade dependency/base image.
4. Rebuild and retest.
5. Rescan.
6. Record an exception only when remediation is not immediately possible and the risk is accepted.

## Drill 7 — Terraform drift

Make a harmless console change, then:

```bash
terraform -chdir=terraform plan
```

Explain the difference between:

- desired state
- actual infrastructure
- Terraform state
- drift

Never blindly apply a plan you do not understand.

## RCA template

**Incident:**

**Impact:**

**Detection:**

**Timeline:**

**Symptoms:**

**Evidence:**

**Root cause:**

**Contributing factors:**

**Immediate mitigation:**

**Permanent fix:**

**Validation:**

**Prevention:**

**Action items:**

**Owner / due date:**
