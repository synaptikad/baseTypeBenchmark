// Q7: Sensor Drift Detection - Top 20 drifting sensors in building (M1)
// Benchmark: Statistical analysis via daily archive UNWIND
// Pattern: Variance/CV calculation from dechunked values (explicit timestamps)
// Parameters: $BUILDING_ID - building to analyze, $DATE_START/$DATE_END (Unix timestamps)
// WARNING: Intentionally expensive on M1 - must dechunk all data for stats

// Step 1: Get all points in building with daily archives in time range
MATCH (p:Node {type: 'Point', building_id: '$BUILDING_ID'})-[:HAS_TIMESERIES]->(c:ArchiveDay)
WHERE c.timestamps[0] >= $DATE_START AND c.timestamps[0] < $DATE_END

// Step 2: Dechunk all values with explicit timestamps
WITH p, c.timestamps AS ts_list, c.values AS vals
UNWIND RANGE(0, SIZE(vals)-1) AS idx
WITH p.id AS point_id,
     p.name AS point_name,
     ts_list[idx] AS ts,
     vals[idx] AS value

// Step 3: Filter to exact time range
WHERE ts >= $DATE_START AND ts < $DATE_END

// Step 4: Compute statistics per point
WITH point_id, point_name, COLLECT(value) AS all_values
WHERE SIZE(all_values) > 100  // Minimum samples for meaningful stats

// Step 5: Calculate mean, stddev, range
WITH point_id, point_name, all_values,
     REDUCE(sum = 0.0, v IN all_values | sum + v) / SIZE(all_values) AS mean_value,
     REDUCE(min_v = all_values[0], v IN all_values | CASE WHEN v < min_v THEN v ELSE min_v END) AS min_value,
     REDUCE(max_v = all_values[0], v IN all_values | CASE WHEN v > max_v THEN v ELSE max_v END) AS max_value,
     SIZE(all_values) AS sample_count

// Step 6: Calculate variance and stddev manually
WITH point_id, point_name, mean_value, min_value, max_value, sample_count,
     max_value - min_value AS range_value,
     // Variance = avg((value - mean)^2)
     REDUCE(sum_sq = 0.0, v IN all_values | sum_sq + (v - mean_value) * (v - mean_value)) / SIZE(all_values) AS variance

WITH point_id, point_name, mean_value, range_value, sample_count,
     SQRT(variance) AS std_value

// Step 7: Coefficient of variation (CV = stddev / |mean|)
WITH point_id, point_name, mean_value, std_value, sample_count,
     CASE WHEN ABS(mean_value) > 0.001 THEN std_value / ABS(mean_value) ELSE std_value END AS cv

// Step 8: Return top 20 by CV (highest drift)
RETURN
    point_id,
    point_name,
    mean_value,
    std_value,
    cv AS coefficient_of_variation,
    sample_count
ORDER BY cv DESC
LIMIT 20;
