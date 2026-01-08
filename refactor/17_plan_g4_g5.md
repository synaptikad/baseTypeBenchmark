# Plan: G4 + G5 - Medium Profile & Full Run Testing

**Date**: 2026-01-08
**Branch**: `v3`
**Reference**: `refactor/07_todo_tracker.md` sections G4-G5

---

## Objective

Complete acceptance testing by:
1. **G4**: Medium profile correctness smoke test (Q1, Q6, Q8, Q13)
2. **G5**: Full run producing results JSON with all queries and statuses

---

## Prerequisites

### Current State
- G1-G3 complete (unit tests + small-2d + RAM gradient)
- Option A production ready
- 4 runner bugs fixed (including SPARQL parameter binding)
- Only `small-2d` dataset exists in `data/generated/`

### Required Before G4
1. Generate `medium-2d` dataset

---

## Implementation Steps

### Step 1: Generate Medium Dataset

```bash
source .venv/bin/activate
python -m src.basetype_benchmark.dataset.generator \
  --profile medium \
  --duration 2d \
  --output data/generated \
  --format parquet
```

**Expected output**: `data/generated/medium-2d/` with ~40k points, 3 buildings

---

### Step 2: Export Data for All Paradigms

```bash
python -m src.basetype_benchmark.runner export \
  -s data/generated/medium-2d \
  -e data/exports \
  -p P1,P2,M1,M2,O2
```

**Creates**: Export files in `data/exports/medium-2d/{p1,p2,m1,m2,o2}/`

---

### Step 3: G4 - Medium Profile Smoke Test

**Command**:
```bash
python -m src.basetype_benchmark.runner benchmark \
  -s data/generated/medium-2d \
  -e data/exports \
  -p P1,P2 \
  -q Q1,Q6,Q8,Q13 \
  --ram 16 \
  --runs 1 \
  -o results_g4.json
```

**Queries selected**:
| Query | Category | Why |
|-------|----------|-----|
| Q1 | graph_only | Energy chain traversal |
| Q6 | timeseries_pure | Hourly aggregation |
| Q8 | hybrid | Tenant energy (graph + TS) |
| Q13 | hybrid | Office hours comfort (complex) |

**Acceptance criteria**:
- All 4 queries return results (non-empty for Q1, Q6, Q8)
- No crashes or timeouts
- Results JSON includes status SUCCESS for P1/P2

---

### Step 4: G5 - Full Run (All Queries)

**Command**:
```bash
python -m src.basetype_benchmark.runner benchmark \
  -s data/generated/medium-2d \
  -e data/exports \
  -p P1,P2,M2,O2 \
  -q Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10,Q11,Q12,Q13,Q14,Q15,Q16,Q17,Q18,Q19,Q20,Q21,Q22,Q23 \
  --ram 16 \
  --runs 1 \
  -o results_g5_full.json
```

**Note**: M1 excluded (no TimescaleDB, only chunked TS - separate test)

**Acceptance criteria**:
- Results JSON contains entries for all 23 queries
- Status matrix matches catalog `paradigm_status`:
  - NATIVE queries → SUCCESS
  - IMPOSSIBLE queries → recorded as IMPOSSIBLE (not fatal)
  - DEGRADED queries → SUCCESS or recorded appropriately
- No crashes

---

### Step 5: Validate Results

1. **Check results structure**:
```bash
python -c "
import json
with open('results_g5_full.json') as f:
    data = json.load(f)
print(f'Total entries: {len(data)}')
for entry in data[:5]:
    print(f'{entry[\"paradigm\"]} {entry[\"query_id\"]}: {entry[\"status\"]}')"
```

2. **Cross-reference with catalog status matrix**

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Medium dataset generation fails | Use small-2d fallback, investigate generator |
| Export takes too long | Monitor progress, use subset if needed |
| Query file missing for paradigm | Task C3/C4 becomes priority |
| IMPOSSIBLE query crashes runner | Task D4 becomes priority |
| Memory issues with medium | Increase RAM limit or use smaller subset |

---

## Estimated Effort

| Step | Complexity |
|------|------------|
| 1. Generate dataset | Simple (CLI command) |
| 2. Export | Simple (CLI command, ~5-10 min) |
| 3. G4 smoke test | Simple (run + verify) |
| 4. G5 full run | Medium (may reveal missing files/bugs) |
| 5. Validate | Simple (JSON analysis) |

---

## Success Criteria

- [ ] `medium-2d` dataset generated successfully
- [ ] All paradigm exports complete
- [ ] G4: Q1, Q6, Q8, Q13 return results for P1/P2
- [ ] G5: results_g5_full.json contains all 23 queries
- [ ] Status matrix matches catalog expectations
- [ ] Update `refactor/07_todo_tracker.md` with G4/G5 ✅

---

## Next Steps After G4/G5

If G4/G5 pass:
1. **H1-H6**: Write queries extension (Phase 6)

If G4/G5 reveal issues:
1. **C3/C4**: Fix missing query files
2. **D4**: Fix IMPOSSIBLE query handling
3. **Other**: Address specific failures
