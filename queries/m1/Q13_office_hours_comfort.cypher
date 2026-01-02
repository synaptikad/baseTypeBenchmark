// Q13: Office Hours Comfort - Stress-test for dechunking (M1)
// Benchmark: Hour filtering requires dechunking every daily archive
// Parameters: $SPACE_TYPE - space type pattern, $DATE_START/$DATE_END (Unix timestamps)
// Pattern: UNWIND daily archives (explicit timestamps) + manual DOW calculation + occupancy correlation
// WARNING: This query is intentionally expensive on M1 to demonstrate chunking overhead

// Step 1: Find spaces of given type with thermostat setpoints
MATCH (sp:Node {type: 'Space'})<-[:LOCATED_IN]-(eq:Node {type: 'Equipment'})
      -[:HAS_POINT]->(p:Node {type: 'Point'})-[:HAS_TIMESERIES]->(c:ArchiveDay)
WHERE sp.space_type STARTS WITH '$SPACE_TYPE'
  AND eq.equipment_type = 'Thermostat'
  AND p.name CONTAINS 'setpoint'
  AND c.timestamps[0] >= $DATE_START AND c.timestamps[0] < $DATE_END

// Step 2: Dechunk - extract individual values with explicit timestamps
WITH sp, p, c, c.timestamps AS ts_list, c.values AS vals
UNWIND RANGE(0, SIZE(vals)-1) AS idx
WITH sp, p, ts_list[idx] AS ts, vals[idx] AS setpoint

// Step 3: Filter to office hours (9h-17h) only (DOW calculation from Unix timestamp)
// Unix epoch (1970-01-01) was Thursday, so (ts/86400 + 4) % 7 gives DOW
// 0=Sunday, 1=Monday, ..., 5=Friday, 6=Saturday
WITH sp, ts, setpoint, (ts % 86400) / 3600 AS hour
WHERE hour >= 9 AND hour <= 17  // Office hours (9h-17h)

// Step 4: Find PeopleCounter in same space - dechunk to find closest timestamp
OPTIONAL MATCH (sp)<-[:LOCATED_IN]-(eq2:Node {type: 'Equipment', equipment_type: 'PeopleCounter'})
               -[:HAS_POINT]->(p2:Node {type: 'Point'})-[:HAS_TIMESERIES]->(c2:ArchiveDay)
WHERE c2.timestamps[0] <= ts AND ts <= c2.timestamps[-1]

// Step 5: Extract occupancy value - find closest timestamp in chunk
// With explicit timestamps, search for value at matching or nearest timestamp
WITH sp, ts, setpoint, c2,
     [i IN RANGE(0, SIZE(c2.timestamps)-1) WHERE c2.timestamps[i] = ts | c2.values[i]] AS exact_match
WITH sp, ts, setpoint,
     CASE WHEN SIZE(exact_match) > 0 THEN exact_match[0]
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
