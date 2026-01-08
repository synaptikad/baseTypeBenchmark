# 07 - TODO tracker (single source of truth for implementation)

How to use:
- Keep this file updated with checkmarks and short notes.
- Do not create parallel TODO lists elsewhere.

Legend:
- [ ] not started
- [~] in progress
- [x] done

## A. Boot and orchestration

- [x] A1. Docker compose health: `timescale`, `memgraph`, `oxigraph` start and are healthy (Phase 0)
- [x] A2. `IsolationManager` does not delete volumes (remove `down -v`) (Phase 3.1: 986858f)
- [ ] A3. RAM limit updates apply correctly to container(s) at runtime
- [ ] A4. Hybrid RAM split applied deterministically (document ratio and rounding)

## B. Option A shared Timescale

- [x] B1. Load timeseries once per dataset run (scenario-level flag) (Phase 3.6: 986858f)
- [x] B2. PostgresLoader.clear_database supports `keep_timeseries=True` (Phase 3.2: 0255089)
- [x] B3. P1/P2 do not truncate timeseries when switching paradigms (Phase 3.2+3.6)
- [x] B4. M2/O2 loaders skip timeseries load when already present (Phase 3.5: 058615c)
- [x] B5. Regression: timeseries row count does not increase across paradigms (Phase 3.5: detection logic)

## C. Query catalog and file alignment

- [x] C1. Rename hybrid TS files (Q06 -> Q6 etc) or implement tolerant lookup (Phase 1.2: bc729a6 - tolerant lookup)
- [x] C2. Fix catalog categories: Q10/Q11 to graph_only (Phase 1.1: 290630e)
- [ ] C3. Ensure every NATIVE query has a file for the paradigm
- [ ] C4. Ensure every hybrid query has both graph+ts files

## D. Runner correctness fixes

- [ ] D1. Escape literal `%` in PostgresRunner (LIKE patterns)
- [x] D2. Warmup uses ordered params for SQL (optional) (Phase 2.1: dc448da - catalog-based ordering)
- [ ] D3. Hybrid runner behavior correct when graph returns empty point_ids
- [ ] D4. UNIMPLEMENTED/IMPOSSIBLE queries are recorded, not fatal
- [x] D5. Support jsonb_specific/graph_native categories for M2/O2 (commit 914b421)
- [x] D6. Fix Turtle syntax in O2 exporter ontology (commit 4356334)
- [x] D7. O2 loader targets default graph with ?default param (commit ff0a0ae)
- [x] D8. O2 param substitution breaks SPARQL syntax (CRITICAL - FIXED commit 96a38ea)
  - **Fix applied**: Replaced naive `query.replace("?key", value)` with VALUES injection
  - **Method**: Injects `VALUES (?var) { (val) }` after WHERE { clause
  - **Benefits**: SPARQL 1.1 compliant, preserves query variables, type-safe
  - See: [15_values_injection_solution.md](15_values_injection_solution.md) for full documentation

## E. RDF/SPARQL alignment (O2)

- [x] E1. Freeze RDF namespace and predicate naming (btb:) - Already correct (btb: used throughout)
- [x] E2. Fix SPARQL queries that reference Brick or wrong predicate names - Q15 fixed (btb:metadataWarrantyEnd)
- [x] E3. Ensure exporter emits predicates used by SPARQL queries (or vice-versa) - Audit complete (Q14-Q19 correct)
- [~] E4. Golden dataset: O2 returns expected non-zero rows for working queries - Blocked by runner bug (jsonb_specific category not supported for O2)

## F. Bulk load robustness (large / xlarge)

- [ ] F1. Timescale load succeeds for 1 month duration (no duplication)
- [ ] F2. Memgraph load strategy acceptable for medium; note improvement plan for xlarge
- [ ] F3. Oxigraph chunked load succeeds for large graphs

## G. End-to-end acceptance tests

- [x] G1. Unit tests for Option A mechanisms (test_option_a.py: 868f448) - 5/5 PASS
- [x] G2. Small profile, 1 RAM level, all paradigms run without crash **(COMPLETED 2026-01-08)**
  - **STATUS:** ✅ COMPLETED - Option A fully functional with schema isolation
  - Container lifecycle fix: commit 8f98537 (keeps containers running for shared paradigms)
  - Schema isolation fix: commit 8442546 (PostgreSQL schemas: ts/p1/p2)
  - E2E validation: P1→P2→M2→O2 all paradigms PASS
  - Results:
    - ✅ P1: Loaded successfully (p1 schema created)
    - ✅ P2: "⏭️ Timeseries already loaded, skipping (Option A)"
    - ✅ M2: "⏭️ Timeseries already loaded for M2, skipping"
    - ✅ O2: "⏭️ Timeseries already loaded for O2, skipping"
  - See: [13_schema_isolation_applied.md](13_schema_isolation_applied.md) for full report
  - See: [12_schema_isolation_implementation_plan.md](12_schema_isolation_implementation_plan.md) for implementation details
- [ ] G3. Small profile, 2 RAM levels, plateau/OOM behavior recorded
- [ ] G4. Medium profile, 1 RAM level, correctness smoke test (Q1, Q6, Q8, Q13)
- [ ] G5. Full run produces results JSON with all queries and statuses

## H. Write queries extension (usage workloads)

- [ ] H1. Extend `queries/catalog.yaml` with QW1-QW3 (+ statuses per paradigm)
- [ ] H2. Implement QW1 (timeseries append) and report rows_written + throughput
- [ ] H3. Implement QW2 (metadata update) with P2 JSONB as NATIVE (P1 optional)
- [ ] H4. Implement QW3 (relation mutation) for P1/P2 + M2 (O2 SPARQL UPDATE or mark IMPOSSIBLE)
- [ ] H5. Runner supports `write_workload` category path resolution and write reporting fields
- [ ] H6. Extended acceptance: small profile, 1 RAM level, READ+WRITE

## Notes / decisions log

- **Option A Implementation**: ✅ COMPLETE (2026-01-08)
  - **Phase 1**: Container lifecycle fix (commit 8f98537) - keeps containers running
  - **Phase 2**: Schema isolation (commit 8442546) - PostgreSQL schemas ts/p1/p2
  - **Unit tests**: 5/5 passing (test_option_a.py)
  - **E2E validation**: PASS - P1→P2→M2→O2 all skip messages detected
  - **Performance**: Zero overhead (namespace resolution only)
  - **Status**: Production ready, all 4 paradigms sharing TimescaleDB
  - See: [13_schema_isolation_applied.md](13_schema_isolation_applied.md) for full implementation report
  - See: [12_schema_isolation_implementation_plan.md](12_schema_isolation_implementation_plan.md) for implementation plan
  - See: [11_option_a_critical_bug.md](11_option_a_critical_bug.md) for original bug analysis
- **Query file lookup**: Tolerant naming (Q6 ↔ Q06) implemented in Phase 1.2
- **Parameter ordering**: Uses catalog-defined order (Phase 2.1)
- **HOTFIX Applied** (2026-01-08): 3 critical runner bugs fixed
  - Bug #1: RunStatus.OK → RunStatus.SUCCESS (gradient.py)
  - Bug #2: MultiContainerSampler type handling (gradient.py)
  - Bug #3: ERROR vs OOM message distinction (scenario.py)
  - See: `refactor/10_hotfix_applied.md` and `HOTFIX_RUNNER_BUGS.md`
- **Phase 4 - RDF/SPARQL Alignment**: ✅ COMPLETE (2026-01-08)
  - Vocabulary: btb: namespace already correct (no Brick confusion)
  - Fix applied: Q15 warranty predicate (btb:warrantyEnd → btb:metadataWarrantyEnd)
  - Audit complete: Q14-Q19 other properties correct
  - Runner category support: jsonb_specific/graph_native now working (commit 914b421)
- **Bug #4 - O2 SPARQL Parameter Binding**: ✅ FIXED & VALIDATED (2026-01-08)
  - **Problem**: Naive string replacement corrupted SPARQL variables (HTTP 400 errors on Q1/Q15)
  - **Solution**: VALUES injection mechanism (`VALUES ?meterId { "value" }` after WHERE {)
  - **Implementation**: commit 96a38ea (oxigraph.py +147/-35, Q1.sparql -2, Q15.sparql -3)
  - **Validation**: commit fecf8a3 (tested on live Oxigraph, 23,570 triples)
    * Q1 (single param): 73 results, 34.23ms ✅
    * Q15 (multi params): SUCCESS, 44.89ms ✅
    * Q16 (no params): 159 results, 37.68ms ✅
  - **Documentation**: [15_values_injection_solution.md](15_values_injection_solution.md), [16_bug4_validation_report.md](16_bug4_validation_report.md)
  - **Status**: PRODUCTION READY
- Hybrid RAM split ratio: TODO (future work)
- Rounding rule: TODO (future work)
- Any deviations from the paper/spec: None yet

