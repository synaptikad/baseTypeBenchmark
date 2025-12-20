// Q13: Friday Office Comfort - Stress-test for dechunking (M1)
// Benchmark: DOW filtering requires dechunking every chunk
// Parameters: $SPACE_TYPE - space type pattern, $DATE_START/$DATE_END (Unix timestamps)
// Pattern: UNWIND chunks + manual DOW calculation + occupancy correlation
// WARNING: This query is intentionally expensive on M1 to demonstrate chunking overhead

// Step 1: Find spaces of given type with thermostat setpoints
MATCH (sp:Node {type: 'Space'})<-[:LOCATED_IN]-(eq:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})-[:HAS_CHUNK]->(c:TSChunk)
WHERE sp.space_type STARTS WITH '$SPACE_TYPE'
  AND eq.equipment_type = 'Thermostat'
  AND p.name CONTAINS 'setpoint'
  AND c.start_ts >= $DATE_START AND c.start_ts < $DATE_END

// Step 2: Dechunk - reconstruct individual timestamps from chunks
WITH sp, p, c, c.start_ts AS base_ts, c.freq_sec AS freq, c.values AS vals
UNWIND RANGE(0, SIZE(vals)-1) AS idx
WITH sp, p, base_ts + (idx * freq) AS ts, vals[idx] AS setpoint

// Step 3: Filter to Fridays only (DOW calculation from Unix timestamp)
// Unix epoch (1970-01-01) was Thursday, so (ts/86400 + 4) % 7 gives DOW
// 0=Sunday, 1=Monday, ..., 5=Friday, 6=Saturday
WITH sp, ts, setpoint, ((ts / 86400) + 4) % 7 AS dow
WHERE dow = 5  // Friday

// Step 4: Find PeopleCounter in same space and get occupancy at same timestamp
OPTIONAL MATCH (sp)<-[:LOCATED_IN]-(eq2:Node {type: 'Equipment', equipment_type: 'PeopleCounter'})
               -[:HAS_POINT]->(p2:Node {type: 'Point'})-[:HAS_CHUNK]->(c2:TSChunk)
WHERE c2.start_ts <= ts < c2.start_ts + (SIZE(c2.values) * c2.freq_sec)

// Step 5: Extract occupancy value from chunk at matching timestamp
WITH sp, ts, setpoint, c2,
     CASE WHEN c2 IS NOT NULL AND c2.freq_sec > 0
          THEN (ts - c2.start_ts) / c2.freq_sec
          ELSE -1
     END AS occ_idx
WITH sp, ts, setpoint,
     CASE WHEN occ_idx >= 0 AND occ_idx < SIZE(c2.values)
          THEN c2.values[occ_idx]
          ELSE null
     END AS occupancy

// Step 6: Group by occupancy level
RETURN
    CASE
        WHEN occupancy IS NULL THEN 'unknown'
        WHEN occupancy < 5 THEN 'low (0-4)'
        WHEN occupancy < 15 THEN 'medium (5-14)'
        ELSE 'high (15+)'
    END AS occupancy_level,
    AVG(setpoint) AS avg_setpoint,
    MIN(setpoint) AS min_setpoint,
    MAX(setpoint) AS max_setpoint,
    COUNT(*) AS sample_count
ORDER BY occupancy_level;
