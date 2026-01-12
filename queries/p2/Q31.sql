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
)
SELECT
    point_id,
    time_bucket,
    AVG(avg_value) OVER (
        PARTITION BY point_id
        ORDER BY time_bucket
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS rolling_avg,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY avg_value) OVER (
        PARTITION BY point_id
    ) AS p95,
    STDDEV(avg_value) OVER (
        PARTITION BY point_id
    ) AS stddev
FROM hourly_data
ORDER BY point_id, time_bucket
LIMIT 1000;
