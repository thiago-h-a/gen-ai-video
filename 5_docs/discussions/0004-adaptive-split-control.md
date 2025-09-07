
# 0004 — Adaptive split control (image vs video)

**Goal:** allocate replicas between image and video workers according to
observed demand and service time. We approximate the optimal share using
\(ho_t = rac{\lambda_t S_t}{\sum_u \lambda_u S_u}\), where \(t\in\{image,video\}\),
\(\lambda\) is the arrival rate (jobs/s) and \(S\) is mean service time.

In practice we avoid direct controller loops by using **HPAs** driven by:
- **External metric** `fair_queue_depth_total{type}` → targets backlog per pod
- **CPU utilization** as a secondary safety signal

The fair-scheduler exports the following Prometheus metrics:
- `arrival_rate_per_sec{type}` — EMA of arrivals
- `service_time_ms_ema{type}` — EMA of service times
- `fair_queue_depth_total{type}` — backlog

You can turn these into Grafana panels and, if desired later, a custom
controller that computes desired splits from `lambda` and `S` directly.
