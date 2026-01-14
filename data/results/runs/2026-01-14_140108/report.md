# Benchmark Report: 2026-01-14_140108

## Executive Summary

**Hypothesis**: Graph databases (M1, M2) do not provide significant advantages over 
SQL+JSONB (P2) for building management workloads, especially considering resource costs.

### Resource Efficiency

| Paradigm | RAM Baseline (MB) | vs P2 | RAM Viable | Verdict |
|----------|-------------------|-------|------------|---------|
| P1 | 8192 | 1.0x | 65536 GB | Equivalent |
| P2 | 8192 | 1.0x | 65536 GB | Equivalent |
| M1 | 5668 | 0.7x | 65536 GB | Equivalent |
| M2 | 3067 | 0.4x | 65536 GB | Equivalent |

### Latency Acceptability

| Paradigm | Acceptable | Degraded | Slow | Score |
|----------|------------|----------|------|-------|
| P1 | 62 | 2 | 1 | 95% |
| P2 | 62 | 1 | 2 | 95% |
| M1 | 61 | 2 | 2 | 94% |
| M2 | 62 | 2 | 1 | 95% |

### Critical Findings: P2 vs M1 (In-Memory Graph)

*Comparing P2 (SQL+JSONB) vs M1 (Memgraph standalone) - the 'in-memory graph kernel' architecture.*
*M2 uses TimescaleDB for timeseries, so M1 is the fair comparison for SpinalCom-style claims.*

**P2 significantly faster** (>500ms difference):

| Query | P2 | M1 | Difference | Ratio |
|-------|---:|---:|----------:|------:|
| Q13 | 2187ms | 69909ms | **+67721ms** | M1 32x slower |
| Q30 | 6ms | 2177ms | **+2171ms** | M1 365x slower |

**M1 significantly faster** (>500ms difference):

| Query | P2 | M1 | Difference | Ratio |
|-------|---:|---:|----------:|------:|
| Q7 | 21740ms | 1510ms | **-20230ms** | P2 14x slower |
| Q31 | 5017ms | 3750ms | **-1267ms** | P2 1x slower |

### Conclusion

- **Latency**: Mixed results: P2 wins on 2 queries, M1 wins on 2.
- **Memory**: Memory consumption is comparable.

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
| Queries | 65 |
| Runs/Query | 1 |
| Variants | 1 |

### RAM Footprint (MB)

| Paradigm | Baseline | Viable |
|----------|----------|--------|
| P1 | 8192 | 65536 |
| P2 | 8192 | 65536 |
| M1 | 5668 | 65536 |
| M2 | 3067 | 65536 |

### Query Latency p50 (ms)

*Legend: acceptable | degraded | slow*

| Query | Category | P1 | P2 | M1 | M2 |
|-------|----------|-----:|-----:|-----:|-----:|
| Q1 | realtime | 54.8 | 32.5 | 12.2 | 11.2 |
| Q10 | realtime | 1.3 | 1.0 | 13.1 | 4.8 |
| Q11 | realtime | 0.9 | 1.0 | 5.7 | 1.2 |
| Q12 | analytic | 666.8 | 265.1 | 648.2 | 635.7 |
| Q13 | analytic | *4521.1* | *2187.2* | **69908.6** | *1565.3* |
| Q14 | navigati | 0.0 | 8.1 | 17.5 | 5.8 |
| Q15 | navigati | 0.0 | 5.5 | 24.1 | 11.1 |
| Q16 | navigati | 0.0 | 20.9 | 78.8 | 70.7 |
| Q17 | navigati | 0.0 | 1.3 | 6.6 | 2.2 |
| Q18 | navigati | 13.8 | 11.7 | 10.8 | 10.2 |
| Q19 | navigati | 2.2 | 1.1 | 0.0 | 3.9 |
| Q2 | realtime | 3.8 | 1.2 | 28.9 | 10.7 |
| Q20 | navigati | 2.4 | 1.3 | 17.3 | 12.6 |
| Q21 | navigati | 2.9 | 2.6 | 15.1 | 14.8 |
| Q22 | navigati | 1.1 | 1.1 | 6.4 | 2.2 |
| Q23 | navigati | 2.9 | 2.5 | 5.3 | 4.8 |
| Q24 | default | 0.0 | 1.0 | 12.2 | 12.2 |
| Q25 | default | 0.0 | 0.9 | 18.2 | 17.7 |
| Q26 | default | 0.0 | 4.2 | 8.4 | 8.3 |
| Q27 | navigati | 1.8 | 1.2 | 37.0 | 34.7 |
| Q28 | navigati | 4.8 | 5.4 | 2.7 | 2.5 |
| Q29 | navigati | 2.5 | 2.7 | 5.9 | 4.6 |
| Q3 | realtime | 0.7 | 0.6 | 3.0 | 1.5 |
| Q30 | navigati | 5.5 | 6.0 | **2177.0** | **2150.5** |
| Q31 | analytic | **21121.3** | **5017.1** | *3749.9* | 14.4 |
| Q32 | backgrou | 0.0 | 3.7 | 55.6 | 18.8 |
| Q33 | backgrou | 28.6 | 28.0 | 0.0 | 21.3 |
| Q34 | backgrou | 651.0 | 39.0 | 0.0 | 1.2 |
| Q35 | default | 1.0 | 0.8 | 5.0 | 3.6 |
| Q36 | default | 0.0 | 0.5 | 23.1 | 5.5 |
| Q37 | default | 0.6 | 0.6 | 21.9 | 4.5 |
| Q38 | default | 0.0 | 0.5 | 23.1 | 5.7 |
| Q39 | default | 0.6 | 0.6 | 0.9 | 1.3 |
| Q4 | realtime | 5.9 | 9.0 | 6.3 | 5.9 |
| Q40 | default | 0.6 | 0.6 | 0.9 | 0.9 |
| Q41 | default | 0.5 | 0.5 | 1.2 | 1.7 |
| Q5 | realtime | 20.6 | 18.7 | 14.1 | 6.8 |
| Q6 | analytic | 19.3 | 6.7 | 86.7 | 43.9 |
| Q7 | analytic | *1675.1* | **21740.1** | *1510.4* | *1470.2* |
| Q8 | analytic | 7.4 | 6.8 | 5.8 | 11.1 |
| Q9 | analytic | 1.7 | 2.0 | 5.0 | 4.7 |
| QW1 | write | 3.7 | 1.3 | 9.9 | 5.8 |
| QW10 | default | 1.2 | 0.6 | 0.9 | 1.2 |
| QW11 | default | 0.6 | 0.5 | 1.9 | 2.0 |
| QW12 | default | 1.4 | 0.8 | 9.3 | 9.6 |
| QW13 | default | 0.4 | 0.5 | 1.0 | 1.7 |
| QW14 | default | 0.0 | 0.5 | 19.2 | 4.5 |
| QW15 | default | 0.7 | 0.7 | 19.2 | 5.1 |
| QW16 | default | 0.0 | 0.8 | 1.3 | 1.1 |
| QW17 | default | 0.0 | 0.8 | 0.8 | 0.8 |
| QW18 | default | 0.0 | 0.8 | 0.8 | 0.8 |
| QW19 | default | 0.0 | 1.1 | 1.3 | 1.2 |
| QW2 | write | 0.0 | 1.4 | 24.0 | 6.4 |
| QW20 | default | 0.0 | 0.7 | 22.1 | 5.4 |
| QW21 | default | 0.6 | 0.6 | 2.6 | 2.6 |
| QW22 | default | 0.7 | 0.7 | 1.1 | 1.1 |
| QW23 | default | 0.8 | 0.8 | 1.6 | 1.6 |
| QW24 | default | 1.1 | 0.9 | 15.9 | 15.2 |
| QW3 | write | 1.0 | 0.6 | 47.0 | 8.2 |
| QW4 | write | 0.0 | 0.8 | 5.1 | 4.2 |
| QW5 | write | 0.0 | 0.8 | 3.1 | 1.7 |
| QW6 | write | 0.0 | 0.8 | 1.5 | 0.9 |
| QW7 | write | 0.0 | 0.8 | 3.3 | 3.3 |
| QW8 | write | 0.0 | 0.5 | 23.4 | 5.0 |
| QW9 | default | 0.7 | 0.6 | 3.0 | 3.3 |

### Query Coverage

| Paradigm | Answered | Impossible |
|----------|----------|------------|
| P1 | 65 | 0 |
| P2 | 65 | 0 |
| M1 | 65 | 0 |
| M2 | 65 | 0 |

### Environment

| Property | Value |
|----------|-------|
| Git | v3@2c1bc16 |
| Host | b3-128-sbg5 |
| Duration | 1163s |
