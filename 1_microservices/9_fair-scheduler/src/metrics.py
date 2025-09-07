
from __future__ import annotations
import asyncio, time
from typing import Dict
from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest

from .store import Store

registry = CollectorRegistry()

jobs_enqueued_total = Counter(
    "jobs_enqueued_total",
    "Jobs enqueued by type",
    labelnames=("type",),
    registry=registry,
)
jobs_completed_total = Counter(
    "jobs_completed_total",
    "Jobs completed by type and status",
    labelnames=("type","status"),
    registry=registry,
)

fair_queue_depth_total = Gauge(
    "fair_queue_depth_total",
    "Sum of queued jobs per type",
    labelnames=("type",),
    registry=registry,
)
fair_ring_size = Gauge(
    "fair_ring_size",
    "Creators in DRR ring per type",
    labelnames=("type",),
    registry=registry,
)
fair_deficit_gauge = Gauge(
    "fair_deficit",
    "Per-creator deficit",
    labelnames=("type","creator"),
    registry=registry,
)
arrival_rate_per_sec = Gauge(
    "arrival_rate_per_sec",
    "EMA of arrival rate (lambda) per type",
    labelnames=("type",),
    registry=registry,
)
service_time_ms_ema = Gauge(
    "service_time_ms_ema",
    "EMA of service time per type",
    labelnames=("type",),
    registry=registry,
)

# Basic exponential moving averages held in-memory per pod
_ema_lambda: Dict[str, float] = {"image": 0.0, "video": 0.0}
_ema_service_ms: Dict[str, float] = {"image": 1000.0, "video": 2000.0}
_last_tick: Dict[str, float] = {"image": time.time(), "video": time.time()}

def note_enqueue(t: str) -> None:
    jobs_enqueued_total.labels(t).inc()
    # Treat each enqueue as 1 event for EMA of arrival rate
    now = time.time()
    dt = max(1e-6, now - _last_tick[t])
    # Instantaneous rate 1/dt, EMA with alpha=0.2
    inst = 1.0 / dt
    _ema_lambda[t] = 0.8 * _ema_lambda[t] + 0.2 * inst
    arrival_rate_per_sec.labels(t).set(_ema_lambda[t])
    _last_tick[t] = now

def note_complete(t: str, success: bool, duration_ms: int | None) -> None:
    jobs_completed_total.labels(t, "success" if success else "failed").inc()
    if duration_ms is not None:
        # EMA alpha=0.2
        _ema_service_ms[t] = 0.8 * _ema_service_ms[t] + 0.2 * float(duration_ms)
        service_time_ms_ema.labels(t).set(_ema_service_ms[t])

async def refresher_task(store: Store, interval_s: int = 5) -> None:
    while True:
        try:
            for t in ("image","video"):
                ring = await store.get_ring(t)
                fair_ring_size.labels(t).set(len(ring))
                # sum queue depths and export per-creator deficits (top N)
                total_q = 0
                deficits = await store.get_deficits(t)
                # reset prior creator label series to avoid cardinality blowup
                # (prom-client doesn't easily allow delete; we just overwrite for existing creators)
                for c, d in deficits.items():
                    fair_deficit_gauge.labels(t, c).set(d)
                for c in ring:
                    total_q += await store.qlen(t, c)
                fair_queue_depth_total.labels(t).set(total_q)
        except Exception:
            # best-effort metrics; never crash
            pass
        await asyncio.sleep(interval_s)

def render_latest() -> bytes:
    return generate_latest(registry)
