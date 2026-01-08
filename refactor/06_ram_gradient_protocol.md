# 06 - RAM gradient protocol (validity + implementation notes)

This protocol defines how RAM is treated as an independent variable and how runs are structured to remain academically defensible.

## 1. What we measure

We measure, during query execution:
- latency distributions (p50/p95/p99)
- RAM peak (container and/or cgroup)
- CPU usage and IO (as implemented in V3 collectors)

We do not report load time. We still track load success/failure (including OOM) because it bounds feasibility.

## 2. RAM levels and rounding

RAM levels are configured in MB in code but discussed in GB in the paper.

Rule:
- Convert GB to MB using 1024 MB per GB (binary).
- When splitting RAM for hybrid, apply deterministic rounding:
  - compute ts_mb = round(total_mb * ts_ratio)
  - graph_mb = total_mb - ts_mb

Keep the ratio constant for M2 and O2.

## 3. Reset semantics between RAM levels

You need to avoid cross-RAM contamination from:
- OS page cache
- database internal caches
- previously accumulated peak metrics

Recommended reset between RAM levels:
- restart the relevant containers (Timescale + graph if used) but preserve volumes
- reset peak trackers in the metrics collector
- optionally drop OS caches (if you can do it safely on your platform)

Do not delete volumes when using Option A.

Implementation implications:
- In `IsolationManager`, use `docker compose down` without `-v`.
- This restarts runtime but keeps the database data.

## 4. Reset semantics between paradigms

Between paradigms, you must avoid reusing structural data:
- For P1/P2, drop/truncate their structure tables between paradigms, but keep shared timeseries.
- For M1, clear the graph store or recreate it.
- For M2/O2, clear graph store between paradigms, but keep shared timeseries.

Recommendation:
- Use loader.clear_database() for the graph engine.
- For PostgresLoader, add `keep_timeseries=True` when switching P1 <-> P2.

## 5. OOM and plateau rules

Feasibility at a RAM level is determined by:
- Container killed by OOM (docker exit code, logs, or driver disconnect)
- Query timeouts that repeat consistently at that RAM level

Plateau detection:
- If increasing RAM beyond X yields less than epsilon improvement on p95 for most queries, record plateau.
- The plateau heuristic should be applied on aggregated results after the run, not as a stop condition during the run (unless you want early stopping).

## 6. Hybrid paradigms (M2, O2) and fairness

Hybrid paradigms have two engines.
To avoid bias:
- report the RAM split and keep it fixed
- restart both engines between RAM levels to reset caches
- ensure Timescale has the same indexes and schema as in P1/P2

For hybrid query execution:
- record per-phase timings (graph_ms, ts_ms) and total_ms
- if graph phase returns empty point_ids, TS phase should be skipped and marked as such

## 7. Minimal recommended run plan for validation

To validate correctness before long runs:
- Use small dataset profile
- Use only 1 RAM level
- Use only Q1-Q13 first
Then:
- Enable 2 RAM levels (eg 8 GB and 16 GB)
Then:
- Scale up to medium

This reduces iteration time without changing the measurement design.

