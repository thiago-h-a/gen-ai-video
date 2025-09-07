
# Runbook — Infra & Ops consolidation (Step 17)

1. **Terraform init/apply**
   ```bash
   cd infra/terraform
   cat > terraform.tfvars <<EOF
   project = "ai-microgen"
   region  = "us-east-1"
   vpc_id  = "vpc-xxxxxxxx"
   private_subnet_ids = ["subnet-aaaa", "subnet-bbbb"]
   eks_cluster_name = "your-eks"
   eks_oidc_provider_arn = "arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/ABC"
   eks_oidc_provider_url = "https://oidc.eks.us-east-1.amazonaws.com/id/ABC"
   EOF
   terraform init && terraform apply -auto-approve
   ```

2. **Sync IRSA patches**
   ```bash
   terraform output -json > /tmp/tf_out.json
   python ops/scripts/sync_irsa_patches.py /tmp/tf_out.json
   ```

3. **Set Redis URL for fair-scheduler (AWS overlay)**
   ```bash
   python ops/scripts/set_redis_url.py /tmp/tf_out.json
   ```

4. **Deploy** (example with kustomize)
   ```bash
   kubectl apply -k deploy/k8s/overlays/aws/model-catalog
   kubectl apply -k deploy/k8s/overlays/aws/fair-scheduler
   kubectl apply -k deploy/k8s/overlays/aws/video-worker
   kubectl apply -k deploy/k8s/overlays/aws/gpu-worker
   kubectl apply -k deploy/k8s/overlays/aws/prompt-service
   kubectl apply -k deploy/k8s/overlays/aws/webapi
   ```

5. **Verify**
   - `kubectl -n ai-microgen get sa | grep -E 'webapi|prompt|catalog|gpu|video|fair'`
   - `kubectl -n ai-microgen get deploy,pods,svc | grep -E 'gpu|video|fair|catalog|webapi|prompt'`
   - Fair-scheduler `/metrics` should expose `fair_queue_depth_total{type}`.

6. **Artifacts**
   - Bucket: output `artifacts_bucket`; set Web/API env for signing if needed.

7. **Rollbacks**
   - HPAs can be disabled by deleting the HPA objects.
   - IRSA annotation patches can be reverted by re‑running `sync_irsa_patches.py` with previous outputs.
