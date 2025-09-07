
    SHELL := /bin/bash

    SERVICES := webapi prompt-service notify-service orchestrator gpu-worker model-registry

    .PHONY: help fmt lint test build push tag smoke load watch

    help:
    	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS=":.*?##"}; {printf "[36m%-18s[0m %s
", $$1, $$2}'

    fmt: ## Format code (python)
    	@echo "[fmt] (placeholder) — add ruff/black/ruff-format in real project"

    lint: ## Lint (python)
    	@echo "[lint] (placeholder) — add ruff/mypy in real project"

    test: ## Run smoke tests
    	python scripts/smoke.sh || true

    build: ## Build all service images
    	for s in $(SERVICES); do     		echo "[build] $$s";     		docker build -t $$s:latest ../services/$$s;     	done

    push: ## Push all images to registry (set REG)
    	@if [ -z "$(REG)" ]; then echo "REG not set (e.g. REG=123456789012.dkr.ecr.us-east-1.amazonaws.com)"; exit 1; fi
    	for s in $(SERVICES); do     		docker tag $$s:latest $(REG)/$$s:latest;     		docker push $(REG)/$$s:latest;     	done

    tag: ## Tag repo (usage: make tag RELEASE=v0.1.0)
    	@if [ -z "$(RELEASE)" ]; then echo "RELEASE not set"; exit 1; fi
    	git tag -a $(RELEASE) -m "release $(RELEASE)" && git push origin $(RELEASE)

    smoke: ## Quick curl-based smoke test
    	bash scripts/smoke.sh

    load: ## Lightweight asyncio load test
    	python scripts/load_test.py --concurrency 5 --seconds 30

    watch: ## Watch queue stats
    	python scripts/watch_queue.py
