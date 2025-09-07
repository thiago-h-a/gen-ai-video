
#!/usr/bin/env python3
"""Sync IRSA role ARNs from `terraform output -json` to K8s AWS overlays.

Usage:
  terraform output -json > /tmp/tf_out.json
  python ops/scripts/sync_irsa_patches.py /tmp/tf_out.json

It rewrites each overlays/aws/*/patch-sa-annotations.yaml with the actual role ARN.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AWS_OVERLAYS = ROOT / 'deploy' / 'k8s' / 'overlays' / 'aws'

MAP = {
  'webapi': 'irsa_webapi',
  'prompt-service': 'irsa_prompt',
  'model-catalog': 'irsa_model_catalog',
  'gpu-worker': 'irsa_gpu_worker',
  'video-worker': 'irsa_video_worker',
  'fair-scheduler': 'irsa_fair_scheduler',
}

def main():
    if len(sys.argv) != 2:
        print('usage: sync_irsa_patches.py <terraform_output_json>')
        sys.exit(1)
    data = json.load(open(sys.argv[1]))
    for svc, tf_key in MAP.items():
        arn = data.get(tf_key, {}).get('value')
        if not arn:
            print(f'[skip] missing {tf_key} in outputs')
            continue
        target = AWS_OVERLAYS / svc / 'patch-sa-annotations.yaml'
        if not target.exists():
            print(f'[skip] {target} not found')
            continue
        text = target.read_text(encoding='utf-8')
        text = text.replace('<IRSA-ROLE-NAME>', arn.split('/')[-1]).replace('<ACCOUNT_ID>', arn.split(':')[4])
        text = text.replace('arn:aws:iam::<ACCOUNT_ID>:role/<IRSA-ROLE-NAME>', arn)
        target.write_text(text, encoding='utf-8')
        print(f'[ok]  {svc} -> {arn}')

if __name__ == '__main__':
    main()
