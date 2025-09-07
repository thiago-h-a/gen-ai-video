
# Capacity Planning

## Back-of-the-envelope

- Average job takes ~250ms of CPU time (synthetic). Real models: profile.
- If 10 workers x 2 concurrency → ~80 jobs/sec peak (synthetic).
- With 20 creatives at 0.2 req/sec each → 4 req/sec avg → ample headroom.

## Worksheets

- Arrival rate (λ), service time (S), utilization ρ = λS / m
- Keep ρ < 0.6 for comfortable headroom.
