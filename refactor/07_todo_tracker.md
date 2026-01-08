# 07 - TODO tracker (single source of truth for implementation)

How to use:
- Keep this file updated with checkmarks and short notes.
- Do not create parallel TODO lists elsewhere.

Legend:
- [ ] not started
- [~] in progress
- [x] done

## A. Boot and orchestration

- [ ] A1. Docker compose health: `timescale`, `memgraph`, `oxigraph` start and are healthy
- [ ] A2. `IsolationManager` does not delete volumes (remove `down -v`)
- [ ] A3. RAM limit updates apply correctly to container(s) at runtime
- [ ] A4. Hybrid RAM split applied deterministically (document ratio and rounding)

## B. Option A shared Timescale

- [ ] B1. Load timeseries once per dataset run (scenario-level flag)
- [ ] B2. PostgresLoader.clear_database supports `keep_timeseries=True`
- [ ] B3. P1/P2 do not truncate timeseries when switching paradigms
- [ ] B4. M2/O2 loaders skip timeseries load when already present
- [ ] B5. Regression: timeseries row count does not increase across paradigms

## C. Query catalog and file alignment

- [ ] C1. Rename hybrid TS files (Q06 -> Q6 etc) or implement tolerant lookup
- [ ] C2. Fix catalog categories: Q10/Q11 to graph_only
- [ ] C3. Ensure every NATIVE query has a file for the paradigm
- [ ] C4. Ensure every hybrid query has both graph+ts files

## D. Runner correctness fixes

- [ ] D1. Escape literal `%` in PostgresRunner (LIKE patterns)
- [ ] D2. Warmup uses ordered params for SQL (optional)
- [ ] D3. Hybrid runner behavior correct when graph returns empty point_ids
- [ ] D4. UNIMPLEMENTED/IMPOSSIBLE queries are recorded, not fatal

## E. RDF/SPARQL alignment (O2)

- [ ] E1. Freeze RDF namespace and predicate naming (btb:)
- [ ] E2. Fix SPARQL queries that reference Brick or wrong predicate names
- [ ] E3. Ensure exporter emits predicates used by SPARQL queries (or vice-versa)
- [ ] E4. Golden dataset: O2 returns expected non-zero rows for working queries

## F. Bulk load robustness (large / xlarge)

- [ ] F1. Timescale load succeeds for 1 month duration (no duplication)
- [ ] F2. Memgraph load strategy acceptable for medium; note improvement plan for xlarge
- [ ] F3. Oxigraph chunked load succeeds for large graphs

## G. End-to-end acceptance tests

- [ ] G1. Small profile, 1 RAM level, all paradigms run without crash
- [ ] G2. Small profile, 2 RAM levels, plateau/OOM behavior recorded
- [ ] G3. Medium profile, 1 RAM level, correctness smoke test (Q1, Q6, Q8, Q13)
- [ ] G4. Full run produces results JSON with all queries and statuses

## Notes / decisions log

- Hybrid RAM split ratio:
- Rounding rule:
- RDF vocabulary decision:
- Any deviations from the paper/spec:

