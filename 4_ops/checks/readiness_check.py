
from __future__ import annotations
import os, sys, json
import urllib.request

def fetch(url: str):
    with urllib.request.urlopen(url, timeout=3) as r:
        return r.read().decode("utf-8")

def main():
    ok = True
    errors = []
    try:
        print(fetch(os.getenv("PROMPT", "http://localhost:8082/healthz")))
    except Exception as e:
        ok = False; errors.append(str(e))
    try:
        print(fetch(os.getenv("NOTIFY", "http://localhost:8083/healthz")))
    except Exception as e:
        ok = False; errors.append(str(e))
    try:
        print(fetch(os.getenv("ORCH", "http://localhost:8084/healthz")))
    except Exception as e:
        ok = False; errors.append(str(e))
    try:
        print(fetch(os.getenv("GPU", "http://localhost:8090/healthz")))
    except Exception as e:
        ok = False; errors.append(str(e))
    obj = {"ok": ok, "errors": errors}
    print(json.dumps(obj))
    if not ok:
        sys.exit(2)

if __name__ == "__main__":
    main()
