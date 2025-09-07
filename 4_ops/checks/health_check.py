
from __future__ import annotations
import os, sys, json
import urllib.request

def fetch(url: str):
    with urllib.request.urlopen(url, timeout=3) as r:
        return r.read().decode("utf-8")

def main():
    base = os.getenv("BASE", "http://localhost:8080")
    try:
        print(fetch(f"{base}/healthz"))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
