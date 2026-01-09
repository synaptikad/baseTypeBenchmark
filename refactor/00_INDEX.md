# BaseTypeBenchmark V3 - Work Docs Pack (Option A: shared Timescale)

Generated: 2026-01-08

This pack is meant to be dropped into the V3 repo (the agent only has V3 code).
It summarizes what worked in V2, why V3 currently breaks, and gives precise, step-by-step implementation tasks.

Scope:
- Paradigms: P1, P2, M1, M2, O2
- 23 queries (Q1-Q23) with explicit behavior for IMPOSSIBLE/DEGRADED
- Dataset produced once in Parquet, exports generated on demand per engine
- Measurement focus: resource impact during query execution (not load time)
- Option A: timeseries lives in a single TimescaleDB instance and is loaded once per dataset run, then reused.

Important notes:
- File `scalable-sniffing-adleman.md` was explicitly excluded from analysis.
- This pack assumes Linux + Docker, but commands are easy to translate.

## Contents

- `docs/00_INDEX.md` (this file)
- `docs/01_V2_vs_V3_logic_chain.md` - end-to-end pipeline comparison and root causes
- `docs/02_target_architecture_option_A.md` - the desired execution model and invariants
- `docs/03_implementation_playbook.md` - concrete edits, in order, with acceptance tests
- `docs/04_alignment_audit_and_matrix.md` - alignment matrix: generator -> exporters -> loaders -> queries -> golden answers
- `docs/05_loader_exporter_bulk_load_notes.md` - practical bulk load strategies per engine (xlarge friendly)
- `docs/06_ram_gradient_protocol.md` - RAM gradient, hybrid RAM split, plateau/OOM rules
- `docs/07_todo_tracker.md` - ready-to-use checklist
- `docs/08_debug_recipes.md` - fast debugging commands and minimal reproductions
- `docs/09_patch_snippets.md` - copy-paste patches and rename lists
- `docs/10_hotfix_applied.md` - applied hotfixes for critical runner bugs
- `docs/11_option_a_critical_bug.md` - CRITICAL BUG: containers stopped between paradigms (BLOCKER)
- `docs/option_a_validation_report.md` - e2e validation test results showing Option A failure

## How to use (suggested workflow)

1. Read `01_V2_vs_V3_logic_chain.md` to understand why V3 fails.
2. Follow `03_implementation_playbook.md` in order.
3. Use `07_todo_tracker.md` as the single source of truth for progress.
4. Validate alignment using `04_alignment_audit_and_matrix.md`.
5. Use `08_debug_recipes.md` for iterative testing.

