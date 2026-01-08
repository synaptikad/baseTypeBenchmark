# 03 - Implementation playbook (precise, actionable)

Goal: make V3 execute end-to-end with Option A (shared Timescale), correct alignment, and a reproducible RAM gradient.

Order matters. Implement in the sequence below.

## Phase 0 - Sanity and environment

### 0.1 Confirm Docker compose names match the code
Repo file: `docker/docker-compose.yml`

Expected by code (`src/basetype_benchmark/runner/ram/isolation.py`):
- Timescale service: `timescale`
- Timescale container name: `benchmark-timescale`
- Memgraph container name: `benchmark-memgraph`
- Oxigraph container name: `benchmark-oxigraph`

Action:
- If any of these do not match, align them (either code or compose, but prefer aligning compose to code).
- Then run:
  - `docker compose -f docker/docker-compose.yml up -d timescale`
  - `docker ps --format '{{.Names}}' | grep benchmark-timescale`

Acceptance:
- The container exists and is healthy.

## Phase 1 - Fix query file alignment (hybrid TS files + categories)

### 1.1 Rename hybrid Timescale query files (recommended)
Problem:
- Files exist as `Q06.sql`, `Q07.sql`, ... but the runner expects `Q6.sql`, `Q7.sql`, ...

Action (rename in git):
- `queries/m2/ts/Q06.sql` -> `queries/m2/ts/Q6.sql`
- `queries/m2/ts/Q07.sql` -> `queries/m2/ts/Q7.sql`
- `queries/m2/ts/Q08.sql` -> `queries/m2/ts/Q8.sql`
- `queries/m2/ts/Q09.sql` -> `queries/m2/ts/Q9.sql`
- `queries/m2/ts/Q12.sql` -> `queries/m2/ts/Q12.sql` (keep as is)
- `queries/m2/ts/Q13.sql` -> `queries/m2/ts/Q13.sql` (keep as is)

Do the same for O2:
- `queries/o2/ts/Q06.sql` -> `queries/o2/ts/Q6.sql`
- `queries/o2/ts/Q07.sql` -> `queries/o2/ts/Q7.sql`
- `queries/o2/ts/Q08.sql` -> `queries/o2/ts/Q8.sql`
- `queries/o2/ts/Q09.sql` -> `queries/o2/ts/Q9.sql`

Alternative (if you do not want renames):
- Update the query loader to search both `Q7.sql` and `Q07.sql`.

Acceptance:
- For M2 and O2, `RamGradient._get_ts_query_text("Q7")` finds a file.

### 1.2 Fix catalog categories for Q10 and Q11
Problem:
- Q10 and Q11 are declared category `hybrid` in `queries/catalog.yaml` but they are graph-only queries.

Action:
- In `queries/catalog.yaml`, change:
  - `Q10.category: hybrid` -> `graph_only`
  - `Q11.category: hybrid` -> `graph_only`

Acceptance:
- For M2/O2, Q10 and Q11 execute only the graph phase (no TS file required).

## Phase 2 - Fix Postgres execution percent escaping (P1/P2)

### 2.1 Escape literal percent signs in SQL
Problem:
- psycopg treats raw `%` as format placeholders.
- Queries using LIKE patterns need `%%` for literal `%`.

File: `src/basetype_benchmark/runner/runners/postgres.py`
Function: `_convert_params()`

Action:
- Before executing any query (both `$1` style and `%(name)s` style), transform:
  - any `%` not part of `%s`, `%(name)s`, or `%%` into `%%`.

Recommended regex:
- Replace `%` with `%%` when it is NOT followed by `s`, `(`, or `%`.

Acceptance:
- A query containing `LIKE 'office%'` executes without formatting errors.

### 2.2 Fix warmup parameter ordering (optional but recommended)
File: `src/basetype_benchmark/runner/ram/gradient.py`
Function: `_warmup()`

Action:
- Use the same ordered tuple logic as timed runs for P1/P2 (based on `query_def.parameter_order`).

Acceptance:
- Warmup does not silently fail due to incorrect positional bindings.

## Phase 3 - Implement Option A persistence (shared Timescale)

This phase makes "load timeseries once" actually true.

### 3.1 Preserve volumes in IsolationManager
Problem:
- `docker compose down -v` deletes volumes, losing Timescale data.

File: `src/basetype_benchmark/runner/ram/isolation.py`
Function: `_compose_down()`

Action:
- Remove the `-v` flag.
- Keep `down` (or replace with `stop`) to reset runtime state between RAM levels, but do not delete volumes.

Acceptance:
- After a restart, `SELECT count(*) FROM timeseries` remains non-zero.

### 3.2 PostgresLoader: keep_timeseries option
Problem:
- `PostgresLoader.clear_database()` truncates timeseries unconditionally.

File: `src/basetype_benchmark/runner/loaders/postgres.py`

Action:
- Change signature to `clear_database(self, keep_timeseries: bool = False)`
- If `keep_timeseries=True`, do not `TRUNCATE timeseries`.

Acceptance:
- Running P1 then P2 does not wipe timeseries when Option A is enabled.

### 3.3 Scenario orchestration: mark timeseries as loaded
Problem:
- M2 and O2 loaders re-load timeseries into Timescale, duplicating rows.

File: `src/basetype_benchmark/runner/benchmark/scenario.py`
Method: `_load_data()`

Action:
- Maintain a scenario-level boolean flag, eg `self._timeseries_loaded`.
- When paradigm needs Timescale (P1/P2/M2/O2):
  - If `_timeseries_loaded` is False:
    - load timeseries, set it True
  - Else:
    - skip timeseries load

Implementation hint:
- For P1/P2, use `PostgresLoader.ensure_timeseries_schema()` then load timeseries.
- For M2/O2, either:
  - add a `skip_timeseries` param to their loaders, or
  - short-circuit `_load_timeseries_*` based on a passed flag.

Acceptance:
- For a full run (P1 -> P2 -> M2 -> O2), timeseries row count is stable (no doubling).

### 3.4 Keep TS while clearing per-paradigm structure
When reloading structure for P1/P2:
- call `clear_database(keep_timeseries=True)`.

When starting a fresh dataset profile:
- call `clear_database(keep_timeseries=False)` or a dedicated `clear_timeseries()`.

Acceptance:
- Switching from one dataset profile to another yields correct TS content for the new dataset.

## Phase 4 - Fix RDF/SPARQL alignment for O2

You must choose a stable RDF vocabulary and align exporter and queries.

Recommended choice:
- Use a single namespace `btb:` for types, predicates, and literal properties.
- Encode equipment type as a literal property `btb:equipment_type "Thermostat"` rather than Brick classes.

### 4.1 Fix SPARQL queries that refer to Brick predicates or mismatched casing
Typical fixes:
- Replace `brick:` vocabulary with `btb:` vocabulary.
- Ensure predicates match the exporter output (snake_case vs camelCase).

Acceptance:
- Golden dataset returns non-zero rows for O2 on queries that are expected to work (Q1-Q13 status matrix).

## Phase 5 - Run acceptance tests in increasing scope

1) Single-service smoke test
- Start timescale only, run a simple SQL `SELECT 1`.

2) P1 end-to-end on small profile
- Export P1, load P1 structure + shared timeseries, run Q1, Q6.

3) P2 end-to-end on small profile
- Ensure timeseries stays, run Q14-Q19 where applicable.

4) M1 end-to-end on small profile
- Export memgraph + chunks, run Q1, Q6 (chunked).

5) M2 and O2 hybrid smoke
- Run one hybrid query that definitely requires TS (eg Q8 or Q9) and validate two-phase behavior.

6) Full run (small profile) at one RAM level only
- Avoid gradient until functional correctness is stable.

7) Enable RAM gradient
- Run 2-3 RAM levels only at first.

