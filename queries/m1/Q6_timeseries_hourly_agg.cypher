// Q6: Timeseries Hourly Aggregation - Dechunking stress-test (M1)
// Benchmark: Manual hourly aggregation via chunk UNWIND
// Pattern: Reconstruct timestamps from chunks, bucket by hour
// Parameters: $POINT_ID - point to aggregate, $DATE_START/$DATE_END (Unix timestamps)
// WARNING: Intentionally expensive on M1 to demonstrate chunking overhead vs time_bucket

// Step 1: Get point with chunks in time range
MATCH (p:Node {id: '$POINT_ID'})-[:HAS_CHUNK]->(c:TSChunk)
WHERE c.start_ts >= $DATE_START AND c.start_ts < $DATE_END

// Step 2: Dechunk - reconstruct individual values with timestamps
WITH p, c, c.start_ts AS base_ts, c.freq_sec AS freq, c.values AS vals
UNWIND RANGE(0, SIZE(vals)-1) AS idx
WITH p.id AS point_id,
     base_ts + (idx * freq) AS ts,
     vals[idx] AS value

// Step 3: Filter to exact time range (chunks may extend beyond)
WHERE ts >= $DATE_START AND ts < $DATE_END

// Step 4: Bucket by hour (floor to hour boundary)
WITH point_id,
     (ts / 3600) * 3600 AS hour_bucket,
     value

// Step 5: Aggregate per hour per point
RETURN
    hour_bucket,
    point_id,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS sample_count
ORDER BY hour_bucket DESC, point_id
LIMIT 1000;
