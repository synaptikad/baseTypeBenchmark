# 01 - V2 vs V3 logic chain (what worked, what broke)

This document compares the end-to-end execution chain in V2 (archive) and V3 (current), and pinpoints the specific logical and programmatic breaks.

## 1. The benchmark chain (shared across both versions)

The benchmark is a pipeline of five stages:

1) Dataset generator
- Produces a common dataset in Parquet (nodes, edges, points, timeseries, optionally chunks)
- Scale and duration control dataset size (small/medium/large, 2d/1m/6m, etc.)

2) Exporters (engine-aware)
- Read Parquet and generate engine-specific ingest files on demand
- Goal: minimize disk by exporting only what is required per engine and per run

3) Container orchestration
- Bring up the required database container(s) for the target paradigm
- Apply RAM limit(s) per the gradient protocol (including split for hybrid paradigms)

4) Loaders
- Bulk load exported files into the database(s)
- Loading is not part of the measured workload, but must be correct and reproducible

5) Workload runner
- Execute 23 queries (with variants and repetitions)
- Collect resource metrics during query execution (RAM peak, CPU, IO) and latencies

The critical requirement is ALIGNMENT across all 5 stages.

## 2. What V2 did that was correct (and should be ported conceptually)

V2 implemented three ideas that made the pipeline coherent:

### 2.1 Shared timeseries export and load (Option A)

In V2:
- `timeseries.csv` was generated ONCE at export root, reused by P1/P2/M2/O2.
- Scenario exports (P1/P2/M2/O2) were produced with `skip_timeseries=True`.

This ensured:
- No duplicate timeseries rows.
- No wasted disk duplicating the same timeseries file in each scenario directory.
- Clear separation: "TS common" vs "graph/document/relational structure per paradigm".

### 2.2 Query loading with tolerant file naming

V2 query loader tried multiple naming patterns (case, suffixes).
This reduced failures due to minor naming differences.

### 2.3 Explicit "scenario files" contract

V2 centralised:
- which files each scenario requires (nodes, edges, timeseries, chunks, triples)
- where they live on disk
- which ones are shared

This prevented exporters and loaders from drifting apart.

## 3. Why V3 currently fails (root causes you must fix)

V3 is more modular and closer to the final architecture, but the chain breaks in several places.

### 3.1 Timescale data is not actually shared due to orchestration reset

In V3:
- `IsolationManager.reset_all()` calls `docker compose down -v`.
- `-v` removes volumes, which deletes Timescale data.

Consequence:
- Even if you want Option A (shared TS loaded once), the orchestration step destroys it between paradigms and between RAM levels.

Required fix:
- Replace global `down -v` with a selective stop/remove strategy.
- Preserve Timescale volume across paradigms for the duration of one dataset benchmark run.
- Only clear Timescale logically (SQL TRUNCATE) when starting a new dataset profile or when you explicitly want a fresh TS.

### 3.2 PostgresLoader.clear_database() truncates timeseries unconditionally

File: `src/basetype_benchmark/runner/loaders/postgres.py`

Current behavior:
- `clear_database()` truncates `timeseries` and all P1/P2 structural tables.

Consequence:
- P1 and P2 cannot reuse a shared Timescale dataset because P2 will wipe it.
- Any attempt to "load TS once, then run P1 and P2" breaks.

Required fix:
- Add a flag `keep_timeseries` (default False to keep current behavior).
- For Option A, call `clear_database(keep_timeseries=True)` for P1 and P2.

### 3.3 M2/O2 loaders re-load timeseries and will duplicate rows

File: `src/basetype_benchmark/runner/loaders/memgraph.py`, method `_load_timeseries_m2()`
- It loads timeseries into Timescale via a `PostgresLoader(paradigm="P1")` instance.

File: `src/basetype_benchmark/runner/loaders/oxigraph.py` also loads timeseries for O2.

Consequence:
- If Timescale already contains the timeseries, loading again duplicates rows (there is no unique constraint on the hypertable).

Required fix:
- Introduce a "TS already loaded" marker in the scenario orchestration.
- If shared TS is present, M2/O2 loaders must skip the timeseries load step.

### 3.4 Query file naming mismatch for hybrid Timescale queries (M2/O2)

V3 expects (from catalog and loader conventions):
- query id `Q6` -> file `Q6.sql`
- hybrid query id `Q7` -> files:
  - `queries/m2/graph/Q7.cypher`
  - `queries/m2/ts/Q7.sql`

But in the current repo:
- Timescale hybrid files are named `Q06.sql`, `Q07.sql`, etc in:
  - `queries/m2/ts/`
  - `queries/o2/ts/`

Consequence:
- V3 does not find the TS file for hybrid queries, causing errors or "UNIMPLEMENTED".

Required fix (choose one):
- Rename `Q06.sql` -> `Q6.sql` etc (recommended, simplest).
- Or extend the loader to accept both patterns.

### 3.5 Catalog category mismatch: Q10/Q11 are declared "hybrid" but are graph-only

In `queries/catalog.yaml`:
- Q10 and Q11 have `category: hybrid`.

But in the query directories:
- There is no TS query file for Q10/Q11 (because these queries do not use timeseries).

Consequence:
- For M2/O2 the runner tries to do two-phase execution and fails because ts query is missing.

Required fix:
- Change Q10 and Q11 category to `graph_only` (or introduce a new category like `graph_native`).
- Keep their paradigm_status as "NATIVE" where appropriate, but remove the "hybrid orchestration" expectation.

### 3.6 SQL percent escaping for psycopg placeholders (P1/P2)

Some SQL queries contain literal percent signs (LIKE patterns).
psycopg uses `%s` placeholders, and a raw `%` in the query text must be escaped as `%%`.

Consequence:
- Queries like `LIKE 'office%'` will error at execution time.

Required fix:
- In `PostgresRunner._convert_params()` escape literal `%` to `%%` before executing.
- Do this without double-escaping existing `%%`, `%s`, or `%(name)s`.

### 3.7 SPARQL ontology / predicate mapping drift (O2)

Some SPARQL queries use Brick-like predicates or camelCase predicates that do not match the exported RDF vocabulary.
Typical symptoms: correct query, but 0 rows.

Required fix (two options, pick one and freeze it):
- Fix exporter mapping so it emits the predicate names used by the queries, or
- Fix SPARQL queries to match the exporter vocabulary (recommended, because it makes the RDF model explicit).

### 3.8 Warmup uses unordered params for SQL

In `ram/gradient.py`, warmup currently calls runner.execute with dict params for P1/P2, not ordered tuples.
If a query uses `$1` placeholders, this can bind incorrectly (even if warmup errors are ignored).

Required fix:
- Apply the same ordered-params conversion in warmup as in timed runs.

## 4. Decision: start from V3, port proven V2 invariants

V3 is closer to the target architecture and already contains:
- on-demand export with cleanup
- a richer query catalog and golden answers
- a federated hybrid runner

The recommended approach is:
- keep V3 structure
- port V2's proven invariants (shared timeseries export, tolerant query file lookup)
- fix orchestration so Timescale persistence works and RAM gradient remains academically valid

