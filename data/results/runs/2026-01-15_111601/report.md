# Benchmark Report: 2026-01-15_111601

## Executive Summary

**Hypothesis**: Graph databases (M1, M2) do not provide significant advantages over 
SQL+JSONB (P2) for building management workloads, especially considering resource costs.

### Resource Efficiency

| Paradigm | RAM Baseline (MB) | vs P2 | RAM Viable | Verdict |
|----------|-------------------|-------|------------|---------|
| P1 | 801 | 0.9x | 512 GB | Equivalent |
| P2 | 893 | 1.0x | 512 GB | Equivalent |
| M1 | 5502 | 6.2x | 4096 GB | **Costly** |
| M2 | 2070 | 2.3x | 512 GB | Acceptable |

### Latency Acceptability

| Paradigm | Acceptable | Degraded | Slow | Score |
|----------|------------|----------|------|-------|
| P1 | 50 | 1 | 2 | 94% |
| P2 | 49 | 3 | 1 | 92% |
| M1 | 49 | 3 | 1 | 92% |
| M2 | 50 | 3 | 0 | 94% |

### Critical Findings: P2 vs M1 (In-Memory Graph)

*Comparing P2 (SQL+JSONB) vs M1 (Memgraph standalone) - the 'in-memory graph kernel' architecture.*
*M2 uses TimescaleDB for timeseries, so M1 is the fair comparison for SpinalCom-style claims.*

**P2 significantly faster** (>500ms difference):

| Query | P2 | M1 | Difference | Ratio |
|-------|---:|---:|----------:|------:|
| Q13 | 2397ms | 70952ms | **+68555ms** | M1 30x slower |
| Q30 | 5ms | 1175ms | **+1170ms** | M1 253x slower |

**M1 significantly faster** (>500ms difference):

| Query | P2 | M1 | Difference | Ratio |
|-------|---:|---:|----------:|------:|
| Q31 | 18516ms | 3729ms | **-14787ms** | P2 5x slower |
| Q12 | 1556ms | 648ms | **-908ms** | P2 2x slower |

### Conclusion

- **Latency**: Mixed results: P2 wins on 2 queries, M1 wins on 2.
- **Memory**: M1 consumes **6.2x more RAM** than P2.

**Verdict**: Results are **MIXED**.

P2 excels on timeseries/analytics, M1 excels on graph-native queries. 
Architecture choice depends on workload distribution.

### Scalability Reference

| Stack | Read QPS | Write QPS | Notes |
|-------|----------|-----------|-------|
| postgresql | 50,000 | 10,000 | PostgreSQL with connection pooling (pgbouncer) and... |
| memgraph | 100,000 | 50,000 | Memgraph in-memory graph database... |

*Source: TechEmpower benchmarks, vendor documentation*

---

## Detailed Results

### Dataset

| Property | Value |
|----------|-------|
| Profile | medium-1w |
| Queries | 53 |
| Runs/Query | 1 |
| Variants | 1 |

### RAM Footprint (MB)

| Paradigm | Baseline | Viable |
|----------|----------|--------|
| P1 | 801 | 512 |
| P2 | 893 | 512 |
| M1 | 5502 | 4096 |
| M2 | 2070 | 512 |

### Query Latency p50 (ms)

*Legend: acceptable | degraded | slow*

| Query | Category | P1 | P2 | M1 | M2 |
|-------|----------|-----:|-----:|-----:|-----:|
| Q1 | realtime | 45.2 | 82.2 | 11.8 | 23.5 |
| Q10 | realtime | 2.0 | 1.9 | 11.3 | 5.1 |
| Q11 | realtime | 0.9 | 1.1 | 2.2 | 2.1 |
| Q12 | analytic | 613.4 | *1556.4* | 647.9 | 632.7 |
| Q13 | analytic | **5186.2** | *2397.4* | **70952.4** | *1169.7* |
| Q14 | navigati | 0.0 | 9.9 | 13.2 | 5.3 |
| Q15 | navigati | 0.0 | 6.7 | 25.5 | 11.8 |
| Q16 | navigati | 0.0 | 22.4 | 74.3 | 69.9 |
| Q17 | navigati | 0.0 | 1.4 | 2.5 | 2.4 |
| Q18 | navigati | 19.0 | 16.4 | 8.5 | 8.1 |
| Q19 | navigati | 1.5 | 1.1 | 0.0 | 4.0 |
| Q2 | realtime | 6.0 | 3.4 | 28.6 | 11.2 |
| Q20 | navigati | 2.1 | 1.5 | 12.6 | 12.6 |
| Q21 | navigati | 2.8 | 2.4 | 15.1 | 13.3 |
| Q22 | navigati | 1.2 | 1.2 | 2.9 | 1.8 |
| Q23 | navigati | 1.4 | 1.3 | 4.5 | 3.2 |
| Q24 | default | 0.0 | 1.3 | 12.9 | 12.4 |
| Q25 | default | 0.0 | 1.1 | 22.9 | 17.5 |
| Q26 | default | 0.0 | 4.0 | 9.2 | 9.3 |
| Q27 | navigati | 1.6 | 1.6 | 35.7 | 34.9 |
| Q28 | navigati | 5.7 | 6.9 | 2.6 | 2.8 |
| Q29 | navigati | 2.0 | 2.4 | 6.0 | 4.7 |
| Q3 | realtime | 1.4 | 2.1 | 2.0 | 1.8 |
| Q30 | navigati | 4.2 | 4.7 | *1174.7* | *1166.4* |
| Q31 | analytic | **20740.3** | **18516.4** | *3729.4* | 15.3 |
| Q32 | backgrou | 0.0 | 3.6 | 22.4 | 19.1 |
| Q33 | backgrou | 31.8 | 27.9 | 0.0 | 21.6 |
| Q34 | backgrou | 67.0 | 36.2 | 0.0 | 1.2 |
| Q35 | default | 0.9 | 0.8 | 2.8 | 3.8 |
| Q36 | default | 0.0 | 0.5 | 21.9 | 5.6 |
| Q37 | default | 0.8 | 0.7 | 21.6 | 5.5 |
| Q38 | default | 0.0 | 0.7 | 35.0 | 4.2 |
| Q39 | default | 0.8 | 0.8 | 0.9 | 1.0 |
| Q4 | realtime | 12.0 | 41.4 | 6.8 | 5.7 |
| Q40 | default | 0.8 | 0.7 | 0.7 | 0.8 |
| Q41 | default | 0.7 | 0.6 | 1.1 | 1.2 |
| Q5 | realtime | 26.2 | 38.9 | 17.8 | 5.8 |
| Q6 | analytic | 22.4 | 20.9 | 13.9 | 49.0 |
| Q7 | analytic | *1243.0* | *1256.2* | *1545.9* | *1179.6* |
| Q8 | analytic | 9.1 | 7.9 | 5.4 | 11.8 |
| Q9 | analytic | 1.9 | 2.2 | 3.1 | 2.6 |
| QW1 | write | 3.7 | 3.0 | 6.7 | 6.0 |
| QW10 | default | 1.4 | 0.9 | 1.2 | 1.3 |
| QW11 | default | 1.0 | 0.9 | 1.9 | 2.1 |
| QW12 | default | 1.4 | 1.4 | 9.1 | 9.9 |
| QW2 | write | 0.0 | 2.8 | 24.5 | 6.6 |
| QW3 | write | 1.1 | 0.9 | 42.8 | 7.5 |
| QW4 | write | 0.0 | 0.9 | 4.3 | 3.9 |
| QW5 | write | 0.0 | 2.2 | 3.7 | 1.7 |
| QW6 | write | 0.0 | 0.9 | 1.1 | 0.9 |
| QW7 | write | 0.0 | 1.4 | 3.6 | 3.9 |
| QW8 | write | 0.0 | 1.3 | 28.9 | 5.4 |
| QW9 | default | 1.0 | 1.0 | 3.0 | 3.0 |

### Query Coverage

| Paradigm | Answered | Impossible |
|----------|----------|------------|
| P1 | 53 | 0 |
| P2 | 53 | 0 |
| M1 | 53 | 0 |
| M2 | 53 | 0 |

### Environment

| Property | Value |
|----------|-------|
| Git | v3@d3cf412 |
| Host | b3-128-sbg5 |
| Duration | 1363s |
