
.PHONY: help up down seed fmt lint test clean

PYTHON := python3
PIP := pip3

help:
	@echo "Targets:"
	@echo "  up      - docker compose up (infra only in this half-step)"
	@echo "  down    - docker compose down -v"
	@echo "  seed    - seed local MinIO buckets (requires mc client installed)"
	@echo "  fmt     - run black + isort (if installed)"
	@echo "  lint    - run ruff/mypy (if installed)"
	@echo "  test    - run pytest (if installed)"
	@echo "  clean   - remove caches"

up:
	docker compose up --build

down:
	docker compose down -v

seed:
	@echo "Seeding MinIO buckets artifacts/ and models/ (requires 'mc' CLI)..."
	@echo "  1) mc alias set local http://localhost:9000 minioadmin minioadmin"
	@echo "  2) mc mb -p local/artifacts || true"
	@echo "  3) mc mb -p local/models || true"
	@echo "  4) mc ls local"

fmt:
	black services/**/src || true
	isort services/**/src || true

lint:
	ruff check services || true
	mypy services || true

test:
	pytest -q || true

clean:
	rm -rf .mypy_cache .pytest_cache **/__pycache__ || true
