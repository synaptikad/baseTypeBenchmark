-- Q31: Rolling Aggregation - TimescaleDB SQL pour M2 hybrid
-- Parametres: point_ids (array), date_start, date_end (lowercase for M2 hybrid)
-- Semantic: Calculate rolling averages and percentiles on timeseries

WITH hourly_data AS (
    SELECT
        point_id,
        time_bucket('1 hour', time) AS time_bucket,
        AVG(value) AS avg_value
    FROM timeseries
    WHERE point_id = ANY(%(point_ids)s::text[])
      AND time >= %(date_start)s::timestamptz
      AND time <= %(date_end)s::timestamptz
    GROUP BY point_id, time_bucket('1 hour', time)
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
