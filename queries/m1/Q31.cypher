// Q31: Rolling Aggregation
// Status: DEGRADED pour M1 (pas de window functions natives)
// Semantic: Calculate rolling averages and percentiles on timeseries
// Parametres: $building_id, $date_start, $date_end
// Note: M1 n'a pas TimescaleDB, approximation via TimeseriesChunk

MATCH (b:Building {id: $building_id})-[:CONTAINS*1..3]->(s:Space)<-[:SERVES]-(eq:Equipment)-[:HAS_POINT]->(p:Point)
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= date($date_start) AND chunk.date <= date($date_end)
UNWIND chunk.values AS val
WITH p.id AS point_id, chunk.date AS time_bucket, val
WITH point_id, time_bucket,
     collect(val) AS values
WITH point_id, time_bucket, values,
     reduce(s = 0.0, v IN values | s + v) / size(values) AS rolling_avg
RETURN
    point_id,
    time_bucket,
    rolling_avg,
    0.0 AS p95,  // Percentile non supporté nativement
    0.0 AS stddev  // Stddev approximatif non implémenté
ORDER BY point_id, time_bucket
LIMIT 1000;
