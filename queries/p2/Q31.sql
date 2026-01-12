-- Q31: Rolling Aggregation (P2 JSONB)
-- Status: NATIVE pour P2 (Window functions PostgreSQL)
-- Semantic: Calculate rolling averages and percentiles on timeseries
-- Parametres: $1 = BUILDING_ID, $2 = DATE_START, $3 = DATE_END

WITH building_points AS (
    SELECT DISTINCT p.id AS point_id
    FROM nodes f
    JOIN nodes s ON s.data->>'floor_id' = f.id AND s.node_type = 'Space'
    JOIN edges e ON e.target_id = s.id AND e.rel_type = 'SERVES'
    JOIN nodes eq ON eq.id = e.source_id AND eq.node_type = 'Equipment'
    JOIN nodes p ON p.data->>'equipment_id' = eq.id AND p.node_type = 'Point'
    WHERE f.node_type = 'Floor' AND f.data->>'building_id' = $1
),
hourly_data AS (
    SELECT
        ts.point_id,
        time_bucket('1 hour', ts.time) AS time_bucket,
        AVG(ts.value) AS avg_value
    FROM ts.timeseries ts
    JOIN building_points bp ON bp.point_id = ts.point_id
    WHERE ts.time >= $2 AND ts.time <= $3
    GROUP BY ts.point_id, time_bucket('1 hour', ts.time)
),
point_stats AS (
    SELECT
        point_id,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY avg_value) AS p95,
        STDDEV(avg_value) AS stddev
    FROM hourly_data
    GROUP BY point_id
)
SELECT
    h.point_id,
    h.time_bucket,
    AVG(h.avg_value) OVER (
        PARTITION BY h.point_id
        ORDER BY h.time_bucket
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS rolling_avg,
    ps.p95,
    ps.stddev
FROM hourly_data h
JOIN point_stats ps ON ps.point_id = h.point_id
ORDER BY h.point_id, h.time_bucket
LIMIT 1000;
