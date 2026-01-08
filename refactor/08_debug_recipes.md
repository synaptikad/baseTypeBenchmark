# 08 - Debug recipes (fast iteration)

These recipes are designed for an agent running code locally with Docker.

## 1. Validate query catalog and paradigm matrix (no DB needed)

Show matrix:
- `btb-runner dry-run --all --matrix`

Validate one query across all engines:
- `btb-runner dry-run --query Q7 --verbose`

This does not check query file presence. It checks catalog consistency and golden params.

## 2. Check query file presence quickly (repo-level)

From repo root:

- SQL:
  - `ls queries/p1/Q*.sql | wc -l`
  - `ls queries/p2/Q*.sql | wc -l`

- Memgraph:
  - `ls queries/m1/Q*.cypher | wc -l`

- Hybrid:
  - `ls queries/m2/graph/Q*.cypher | wc -l`
  - `ls queries/m2/ts/Q*.sql | wc -l`
  - `ls queries/o2/graph/Q*.sparql | wc -l`
  - `ls queries/o2/ts/Q*.sql | wc -l`

If counts are not 23 for graph-only directories, check missing files.
For TS directories, the expected set is based on catalog category.

## 3. Start containers manually (before involving the benchmark runner)

- `docker compose -f docker/docker-compose.yml up -d timescale`
- `docker compose -f docker/docker-compose.yml up -d memgraph`
- `docker compose -f docker/docker-compose.yml up -d oxigraph`

Health checks:
- `docker ps --format '{{.Names}} {{.Status}}' | grep benchmark-`
- Timescale: `psql` inside container or via host port.

## 4. Minimal DB connectivity tests

P1/P2 connectivity:
- Use the Postgres DSN from V3 config (see `src/basetype_benchmark/runner/config.py`).
- Confirm `SELECT 1`.

Memgraph connectivity:
- Bolt at `localhost:7687`.

Oxigraph connectivity:
- HTTP at `localhost:7878`.

## 5. Fast end-to-end correctness smoke test (small profile, 1 query)

Goal: validate exporter -> loader -> query execution.

Suggested sequence:

1) Generate dataset (small, short duration)
2) Export P1 structural + TS common
3) Load TS common once
4) Load P1 structural
5) Run Q1 and Q6 on P1

Then:
- switch to P2 structural without truncating timeseries
- run Q14 (JSONB) and Q6 again

## 6. Debug hybrid queries (M2/O2)

Pick a query that must touch TS, eg Q8 (tenant energy).
- Run graph phase only and print returned `point_ids`.
- Ensure TS phase query accepts point_ids correctly.

Key check:
- If point_ids list is empty, TS phase must be skipped and this must be recorded in results.

## 7. Timeseries duplication check

After any load step, run:
- `SELECT count(*) FROM timeseries;`

Expected under Option A:
- The count stays constant when switching paradigms (P1 -> P2 -> M2 -> O2).
- It changes only when switching dataset profile or duration.

## 8. Reproduce and confirm the percent escaping fix

Run a SQL query containing:
- `LIKE 'office%'`

If it fails with formatting errors, the percent escaping fix is missing or incomplete.

