# 02 - Target architecture (Option A: shared Timescale)

This is the intended V3 behavior for a full benchmark run.

## 1. Option A in one sentence

Timeseries is stored once in a single TimescaleDB instance, loaded once per dataset run, and reused by P1, P2, M2, O2 without duplication.

## 2. Invariants (must always hold)

### 2.1 Data invariants
- The Parquet dataset is the unique source of truth.
- Timeseries in Timescale is identical for all paradigms that use Timescale.
- Structural data (nodes/edges/documents/triples) is reloaded per paradigm and can be dropped between paradigms.

### 2.2 Measurement invariants
- Load time is not part of reported performance metrics.
- Query execution metrics are collected under the RAM gradient protocol.
- For hybrid paradigms (M2/O2) the RAM allocation is split between graph engine and Timescale, deterministically.

### 2.3 Orchestration invariants
- Timescale volume is preserved across paradigms during a dataset run.
- Timescale is cleared (TRUNCATE) only when switching dataset profile or duration, or when explicitly requested.

## 3. Execution flow (one profile, one duration)

Pseudo-flow:

1) Generate Parquet dataset
2) Start Timescale (RAM max or baseline for load)
3) Export TS common once (timeseries.csv or equivalent)
4) Load TS common once into Timescale

Then for each paradigm:

- P1 (Postgres relational + Timescale)
  - Export P1 structural files (no timeseries file)
  - Clear P1 structural tables only (keep timeseries)
  - Load P1 structural tables
  - For each RAM level:
    - Apply RAM limit to Timescale container
    - Run query workload and record metrics

- P2 (Postgres JSONB + Timescale)
  - Export P2 structural files (no timeseries file)
  - Drop P1 structural tables, then load P2 documents (keep timeseries)
  - For each RAM level:
    - Apply RAM limit to Timescale container
    - Run query workload and record metrics

- M1 (Memgraph only, chunked TS in graph)
  - Export M1 nodes/edges + chunk file(s)
  - Start Memgraph (no Timescale dependency)
  - For each RAM level:
    - Apply RAM limit to Memgraph
    - Run query workload and record metrics
  - Stop Memgraph (volume can be removed or DB cleared)

- M2 (Memgraph + Timescale federated)
  - Export M2 nodes/edges (no timeseries file)
  - Ensure Timescale already loaded (skip TS load)
  - Start Memgraph in parallel with Timescale
  - For each RAM level:
    - Split RAM between Memgraph and Timescale (ratio fixed, eg 60/40)
    - Run hybrid workload:
      - Graph phase returns point_ids
      - TS phase queries Timescale with point_ids
      - Record timing breakdown + resource metrics

- O2 (Oxigraph + Timescale federated)
  - Export RDF graph/triples (no timeseries file)
  - Ensure Timescale already loaded (skip TS load)
  - Start Oxigraph in parallel with Timescale
  - For each RAM level:
    - Split RAM between Oxigraph and Timescale (ratio fixed, eg 60/40)
    - Run hybrid workload (SPARQL then SQL)
    - Record timing breakdown + resource metrics

Finally:
- Stop all containers, optionally remove volumes, and store results.

## 4. RAM split for hybrid paradigms

To avoid bias:
- Use a fixed ratio for the split (document it in the paper).
- Apply the same ratio for M2 and O2.
- Keep the sum equal to the target RAM level.

Example:
- Total 32 GB, ratio graph 0.6, ts 0.4:
  - Graph container: 19.2 GB (rounded)
  - Timescale container: 12.8 GB

Rounding rule should be deterministic and documented (eg MB granularity).

## 5. What "reset" means under Option A

Reset must clear caches and metric peaks without destroying shared Timescale data.

Recommended reset primitives:
- OS page cache drop (optional, platform dependent)
- Clear per-query peak trackers
- For DB state:
  - Structural tables: drop/truncate per paradigm
  - Timeseries: keep, unless changing dataset

Avoid:
- docker compose down -v in the middle of a dataset run (it destroys shared state)

