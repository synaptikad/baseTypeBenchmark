# 04 - Alignment audit and matrix (generator -> exporters -> loaders -> queries -> answers)

V3 is designed to have one primary spec for queries: `queries/catalog.yaml`.
That file defines:
- query categories (graph_only, timeseries_pure, hybrid, jsonb_specific, graph_native)
- parameter list and ordering
- per-paradigm status (NATIVE / DEGRADED / IMPOSSIBLE)
- intended semantics and result schema

Everything else must align with it.

## 1. Alignment layers in V3

1) Query catalog
- `queries/catalog.yaml`

2) Parameter generation
- `src/basetype_benchmark/runner/params/*`
- Produces variants compatible with SQL/Cypher/SPARQL idioms.

3) Dataset and exporters
- Generator outputs Parquet with canonical columns.
- Exporters convert Parquet to per-engine ingest files.
- Key folder: `src/basetype_benchmark/dataset/exporters/`

4) Loaders and schemas
- `src/basetype_benchmark/runner/loaders/*`
- They define DB schema, bulk load method, and clearing behavior.

5) Query files
- `queries/p1/*.sql`, `queries/p2/*.sql`
- `queries/m1/*.cypher`
- `queries/m2/graph/*.cypher`, `queries/m2/ts/*.sql`
- `queries/o2/graph/*.sparql`, `queries/o2/ts/*.sql`

6) Golden answers
- `queries/golden_answers.yaml` defines expected row counts and sample rows for the golden dataset.

If any of these layers drift, you get:
- runtime errors (missing file, placeholder mismatch)
- 0 rows (semantic mismatch)
- biased results (duplicated timeseries, wrong joins)

## 2. Critical alignment rules

### 2.1 Query id and filename rules
- Graph-only queries: one file per paradigm, named `Qn.*` (no leading zeros)
- Timeseries-only (Q6): one SQL file per paradigm that uses Timescale
- Hybrid queries: two files for M2 and O2:
  - Graph phase: `queries/m2/graph/Qn.cypher` or `queries/o2/graph/Qn.sparql`
  - TS phase: `queries/m2/ts/Qn.sql` or `queries/o2/ts/Qn.sql`

### 2.2 Parameter naming rules
Catalog parameters are uppercase (METER_ID, FLOOR_ID, ...).
Execution rules:
- SQL: positional placeholders `$1, $2, ...` bind by the catalog parameter order.
- Cypher: placeholders are usually lowercase (eg `$meter_id`), runner must accept lowercase keys.
- SPARQL: variables are `?meterId` etc, substitution layer must handle mapping.

Therefore:
- Convert param dict keys to lowercase for Cypher and SPARQL execution.
- Keep ordered tuple binding for SQL.

### 2.3 Timeseries uniqueness rule (Option A)
- The hypertable `timeseries` has no uniqueness constraint.
- Therefore: the same dataset must never be loaded twice without an explicit TRUNCATE.

Rule:
- Load TS once per dataset run.
- Never reload TS for M2/O2 if already present.

### 2.4 Status rule (academic correctness)
- If catalog marks a query as IMPOSSIBLE for a paradigm:
  - The runner must not crash.
  - It should record a structured result with status IMPOSSIBLE/UNIMPLEMENTED and a clear note.

Recommendation:
- When a query file is missing, treat it as UNIMPLEMENTED and record it.
- Do not silently skip NATIVE queries.

## 3. Quick matrix: files expected per paradigm

This is the minimum set of files that must exist for "full coverage":

### P1 (SQL)
- `queries/p1/Q1.sql` ... `Q23.sql`

### P2 (SQL + JSONB)
- `queries/p2/Q1.sql` ... `Q23.sql`
- Q14-Q19 are JSONB-specific, but other queries still exist.

### M1 (Cypher)
- `queries/m1/Q1.cypher` ... `Q23.cypher`
- Q6 and Q13 are chunk-based timeseries stress tests.

### M2 (Hybrid)
Graph:
- `queries/m2/graph/Q1.cypher` ... `Q23.cypher`
TS:
- `queries/m2/ts/Q6.sql`, `Q7.sql`, `Q8.sql`, `Q9.sql`, `Q12.sql`, `Q13.sql`
Note:
- If Q10/Q11 are graph-only, they must not require TS files.

### O2 (Hybrid)
Graph:
- `queries/o2/graph/Q1.sparql` ... `Q23.sparql`
TS:
- `queries/o2/ts/Q6.sql`, `Q7.sql`, `Q8.sql`, `Q9.sql`, `Q12.sql`, `Q13.sql`

## 4. High-risk queries (known mismatch zones)

1) SQL queries with LIKE patterns
- Must escape literal `%` for psycopg.

2) Q10 / Q11 category
- Must be graph_only in catalog if there is no TS phase.

3) RDF/SPARQL vocabulary
- Must match exporter output exactly (namespace and predicate spelling).
- Typical mismatches: Brick vs BTB, camelCase vs snake_case.

4) Timeseries duplication
- Any re-load of timeseries without TRUNCATE invalidates results.

## 5. Alignment checklist before running large profiles

- A. Query files present and correctly named (no leading zeros for Qn.*)
- B. Catalog categories consistent with files (hybrid means graph+ts)
- C. Exporters generate files expected by loaders (column names)
- D. Loaders clear the correct subset of data (keep TS in Option A)
- E. Golden dataset: row counts match for P2 (baseline), and other paradigms are either coherent or explicitly marked DEGRADED/IMPOSSIBLE.

