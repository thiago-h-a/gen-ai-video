
# Testing

## Levels
- Unit (pure funcs, validators)
- Component (FastAPI routes)
- Integration (Compose: orchestrator + worker + Redis)
- Load (ops/scripts/load_test.py)

## Patterns
- Seeded randomness for deterministic image bytes in tests
- Use httpx.AsyncClient + uvicorn in-process where practical
- Contract tests between services using recorded fixtures
