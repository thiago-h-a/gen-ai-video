
#!/usr/bin/env python3
"""Patch fair-scheduler AWS overlay ConfigMap to set REDIS_URL from TF outputs.

Usage:
  terraform output -json > /tmp/tf_out.json
  python ops/scripts/set_redis_url.py /tmp/tf_out.json
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CM = ROOT / 'deploy' / 'k8s' / 'overlays' / 'aws' / 'fair-scheduler' / 'kustomization.yaml'
CM_BASE = ROOT / 'deploy' / 'k8s' / 'base' / 'fair-scheduler' / 'configmap.yaml'

PATCH_PATH = ROOT / 'deploy' / 'k8s' / 'overlays' / 'aws' / 'fair-scheduler' / 'patch-configmap.yaml'

PATCH_TMPL = """apiVersion: v1
kind: ConfigMap
metadata:
  name: fair-scheduler-config
  namespace: ai-microgen
data:
  REDIS_URL: {url}
"""

def main():
    if len(sys.argv) != 2:
        print('usage: set_redis_url.py <terraform_output_json>')
        sys.exit(1)
    data = json.load(open(sys.argv[1]))
    host = data.get('redis_endpoint', {}).get('value')
    port = data.get('redis_port', {}).get('value', 6379)
    url = f'redis://{host}:{port}/0'
    PATCH_PATH.write_text(PATCH_TMPL.format(url=url), encoding='utf-8')
    # Ensure kustomization references the patch (idempotent)
    kz = CM.read_text(encoding='utf-8') if CM.exists() else 'apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: ai-microgen
resources:
  - ../../base/fair-scheduler
patches: []
'
    if 'patch-configmap.yaml' not in kz:
        kz = kz.rstrip() + '
patches:
  - path: patch-configmap.yaml
'
        CM.write_text(kz + '
', encoding='utf-8')
    print(f'[ok] REDIS_URL -> {url}')

if __name__ == '__main__':
    main()
