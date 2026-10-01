# 02 — AWS CloudShell tool setup

Run everything in **AWS CloudShell**, not Windows.

## 1. Check what is already installed

```bash
aws --version
git --version
docker --version
kubectl version --client
terraform version
helm version
```

## 2. Terraform

Use the current stable Terraform 1.16.x line for this lab. The repository requires Terraform >=1.9 and <2.0.

```bash
cd /tmp
curl -LO https://releases.hashicorp.com/terraform/1.16.4/terraform_1.16.4_linux_amd64.zip
unzip -o terraform_1.16.4_linux_amd64.zip
sudo mv terraform /usr/local/bin/terraform
terraform version
```

## 3. Helm

Use Helm 3.21.3 for maximum compatibility with the Kubernetes ecosystem used in this lab.

```bash
cd /tmp
curl -LO https://get.helm.sh/helm-v3.21.3-linux-amd64.tar.gz
tar -zxvf helm-v3.21.3-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
helm version
```

## 4. kubectl

If this works, do not reinstall it:

```bash
kubectl version --client
```

If it is missing, AWS CloudShell documentation/AMI tooling should be preferred over manually installing a random binary.

## 5. Docker sanity check

```bash
docker version
docker info >/dev/null && echo "Docker daemon available"
```

## 6. AWS identity

```bash
aws sts get-caller-identity
aws configure get region || true
```

For this lab, use `ap-south-1` unless you intentionally choose another region and update `terraform.tfvars` and `k8s/secret-store.yaml`.
