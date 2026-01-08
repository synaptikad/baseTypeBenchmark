# 05 - Loader/exporter bulk-load notes (xlarge friendly)

This document focuses on ingestion robustness and throughput for large datasets, without contaminating the measured query workload.

Principle:
- Loading is not measured as a benchmark metric.
- But loading must be correct, reproducible, and feasible up to large/xlarge datasets.

## 1. Parquet as canonical interchange

Parquet is a good choice for the generator output:
- columnar
- compressible
- fast to filter and scan

Exporters should:
- stream from parquet to the target ingest format (CSV/NT)
- avoid building huge in-memory lists
- support on-demand export (already present in V3 scenario)

## 2. Timescale / Postgres (P1, P2, shared TS)

### 2.1 Current good practice in V3
- Use `COPY ... FROM STDIN WITH CSV HEADER` via psycopg.
- Create tables before COPY.
- Ensure Timescale hypertable exists before loading timeseries.

### 2.2 Practical settings for faster load (optional)
These change only load performance, not query workload:
- `SET synchronous_commit = off;` during load
- `SET maintenance_work_mem` higher during index creation
- Delay index creation until after COPY (if you create indexes)

If you do this, document it and keep it consistent across paradigms.

### 2.3 Avoid timeseries duplication (Option A)
- Timeseries table has no unique constraint.
- Never load timeseries twice without TRUNCATE.
- Prefer: load once and keep.

## 3. Memgraph (M1, M2)

### 3.1 Current V3 approach
Memgraph loader currently:
- reads CSV client-side
- uses UNWIND batches (`CREATE` per row)
This is functional but will not scale well to xlarge.

### 3.2 Recommended bulk approach for xlarge
Prefer server-side CSV import:
- Mount the export directory into the Memgraph container, eg:
  - add to docker-compose memgraph service:
    - `volumes: - ./export:/data:ro` (path adapted)
- Then use Memgraph `LOAD CSV`:
  - `LOAD CSV FROM "/data/m1/nodes.csv" WITH HEADER AS row ...`
- Split files by node type and by edge type to improve parallelism.

Alternative:
- Use Memgraph import tooling (if available in your chosen Memgraph image/version).

### 3.3 Chunked timeseries (M1)
M1 stores timeseries in chunk structures.
For large durations:
- ensure chunk size is configurable
- ensure chunk generation/export is streaming (avoid giant arrays)
- prefer a "one chunk per point per day/week" design so queries can UNWIND bounded data

## 4. Oxigraph (O2)

### 4.1 Current V3 approach
- Stream N-Triples to Oxigraph via HTTP in chunks.
This is correct and scalable as long as chunk size is controlled.

### 4.2 Tuning
- Increase chunk size cautiously (line-based) to reduce HTTP overhead.
- Ensure HTTP client uses keep-alive (httpx does).
- If Oxigraph supports bulk load from file, consider mounting and server-side load for very large graphs.

## 5. Export strategy for disk minimization

Given 1 month / 6 months durations, timeseries can dominate disk.

Recommended:
- Export timeseries only once to a shared folder, reused by all paradigms that rely on Timescale.
- Export per-paradigm structure only on demand.
- After each paradigm run, delete per-paradigm export files if `--cleanup-exports` is enabled (already in V3).

## 6. Loader/exporter interface contract (recommendation)

Make the contract explicit in code and docs:

- Exporter produces:
  - structure files for paradigm
  - optional shared `timeseries.csv` (Option A)

- Loader consumes:
  - structure files
  - optionally timeseries.csv, but only when a scenario-level flag says "TS not loaded yet"

This avoids hidden duplication and makes correctness testable.

