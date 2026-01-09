# Option A End-to-End Validation Report

**Timestamp:** 2026-01-08 12:42:24

## Test Configuration
- **Paradigms tested:** P1 → P2 → M2 → O2
- **Dataset:** small-2d (freshly generated)
- **Objective:** Validate timeseries is loaded once and reused

## Results Summary

### ❌ VALIDATION FAILED

Found 1 error(s) during validation.

## Timeseries Row Counts

| Paradigm | Row Count | Change from P1 |
|----------|-----------|----------------|
| P1 | N/A | N/A |
| P2 | N/A | N/A |
| M2 | N/A | N/A |
| O2 | N/A | N/A |


## Skip Messages Detection

| Paradigm | Expected Message | Found? |
|----------|------------------|--------|
| P2 | `⏭️  Timeseries already loaded, skipping (Option A)` | ✅ YES |
| M2 | `⏭️  Timeseries already loaded for M2, skipping` | ✅ YES |
| O2 | `⏭️  Timeseries already loaded for O2, skipping` | ✅ YES |


## ✅ Successes

- Fresh dataset generated successfully
- Skip message detected for P2
- Skip message detected for M2
- Skip message detected for O2
- Benchmark completed without fatal errors


## ❌ Errors

- Timeseries table is empty or doesn't exist


## Benchmark Output

```
╭──────────────────────────────────────────────────────────────────────────────╮
│ Benchmark Configuration                                                      │
│                                                                              │
│ Source: /home/ubuntu/baseTypeBenchmark/data/generated/small-2d               │
│ Paradigms: P1, P2, M2, O2                                                    │
│ Queries: all                                                                 │
│ RAM levels: 16GB                                                             │
│ Runs: 1, Variants: 3                                                         │
│ Disk mode: persistant                                                        │
│ Output: /home/ubuntu/baseTypeBenchmark/data/results/option_a_validation.json │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─── Starting Benchmark ────╮
│ Benchmark Runner V3       │
│                           │
│ Paradigms: P1, P2, M2, O2 │
│ Queries: 23               │
│ RAM levels: 1             │
│ Data profile: small       │
│ Disk mode: persistant     │
╰───────────────────────────╯

===== P1 (1/4) =====
  Exporting P1...
  Starting containers...
  Loading data...
  Running RAM gradient...
    RAM 16384MB (1/1)
      Warmup (3 runs)...
      Running 23 queries (3 variants × 1 runs)...
      Q1 (1/23) OK avg=4.1ms rows=0
      Q2 (2/23) OK avg=1.7ms rows=0
      Q3 (3/23) OK avg=0.4ms rows=0
      Q4 (4/23) ERROR: ProgrammingError: the query has 4 placeholders but
      Q5 (5/23) OK avg=1.0ms rows=1
      Q6 (6/23) OK avg=3.2ms rows=0
      Q7 (7/23) OK avg=2.9ms rows=20
      Q8 (8/23) ERROR: ProgrammingError: the query has 4 placeholders but
      Q9 (9/23) ERROR: ProgrammingError: the query has 5 placeholders but
      Q10 (10/23) OK avg=1.4ms rows=2
      Q11 (11/23) OK avg=0.6ms rows=0
      Q12 (12/23) ERROR: ProgrammingError: the query has 4 placeholders but
      Q13 (13/23) OK avg=46.8ms rows=32
      Q14 (14/23) ERROR: ProgrammingError: the query has 0 placeholders but
      Q15 (15/23) ERROR: ProgrammingError: the query has 0 placeholders but
      Q16 (16/23) ERROR: ProgrammingError: the query has 0 placeholders but
      Q17 (17/23) ERROR: ProgrammingError: the query has 0 placeholders but
      Q18 (18/23) OK avg=0.7ms rows=0
      Q19 (19/23) OK avg=0.7ms rows=0
      Q20 (20/23) ERROR: DatatypeMismatch: recursive query "paths" column 4
      Q21 (21/23) ERROR: DatatypeMismatch: recursive query "all_paths" colu
      Q22 (22/23) ERROR: ProgrammingError: the query has 2 placeholders but
      Q23 (23/23) OK avg=0.7ms rows=0
  Keeping containers running for Option A...
  RAM viable: 16384 MB

===== P2 (2/4) =====
  Exporting P2...
  Starting containers...
  Loading data...
⏭️  Timeseries already loaded, skipping (Option A)
  Running RAM gradient...
    RAM 16384MB (1/1)
      Warmup (3 runs)...
      Running 23 queries (3 variants × 1 runs)...
      Q1 (1/23) OK avg=4.3ms rows=0
      Q2 (2/23) OK avg=0.7ms rows=0
      Q3 (3/23) OK avg=0.5ms rows=0
      Q4 (4/23) ERROR: ProgrammingError: the query has 4 placeholders but
      Q5 (5/23) OK avg=1.3ms rows=1
      Q6 (6/23) OK avg=1.1ms rows=0
      Q7 (7/23) OK avg=3.0ms rows=20
      Q8 (8/23) ERROR: ProgrammingError: the query has 4 placeholders but
      Q9 (9/23) ERROR: ProgrammingError: the query has 5 placeholders but
      Q10 (10/23) OK avg=1.7ms rows=2
      Q11 (11/23) OK avg=0.8ms rows=0
      Q12 (12/23) ERROR: ProgrammingError: the query has 4 placeholders but
      Q13 (13/23) OK avg=53.0ms rows=32
      Q14 (14/23) OK avg=0.9ms rows=0
      Q15 (15/23) ERROR: ProgrammingError: the query has 4 placeholders but
      Q16 (16/23) ERROR: ProgrammingError: the query has 3 placeholders but
      Q17 (17/23) OK avg=0.7ms rows=1
      Q18 (18/23) ERROR: ProgrammingError: the query has 3 placeholders but
      Q19 (19/23) OK avg=0.6ms rows=0
      Q20 (20/23) ERROR: DatatypeMismatch: recursive query "paths" column 4
      Q21 (21/23) ERROR: DatatypeMismatch: recursive query "all_paths" colu
      Q22 (22/23) ERROR: ProgrammingError: the query has 2 placeholders but
      Q23 (23/23) OK avg=0.7ms rows=0
  Keeping containers running for Option A...
  RAM viable: 16384 MB

===== M2 (3/4) =====
  Exporting M2...
  Starting containers...
  Loading data...
⏭️  Timeseries already loaded for M2, skipping
  Running RAM gradient...
    RAM 16384MB (1/1)
      Warmup (3 runs)...
      Running 23 queries (3 variants × 1 runs)...
      Q1 (1/23) OK avg=0.9ms rows=0
      Q2 (2/23) OK avg=0.6ms rows=0
      Q3 (3/23) OK avg=0.4ms rows=0
      Q4 (4/23) ERROR: ClientError: {neo4j_code: Memgraph.ClientError.Mem
      Q5 (5/23) ERROR: ClientError: {neo4j_code: Memgraph.ClientError.Mem
      Q6 (6/23) OK avg=7.3ms rows=0
      Q7 (7/23) ERROR: InvalidTextRepresentation: malformed array literal
      Q8 (8/23) ERROR: InvalidTextRepresentation: malformed array literal
      Q9 (9/23) ERROR: CannotCo

... (truncated)
```

## Conclusions

❌ Option A implementation has **ISSUES**.
- Found 1 error(s)
- Found 0 warning(s)

**Recommendation:** Review errors and fix before marking G2 as completed.