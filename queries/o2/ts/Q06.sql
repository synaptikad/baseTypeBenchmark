-- Q6: Hourly Aggregation (O2)
-- Parametres: point_id, date_start, date_end

SELECT
    time_bucket('1 hour', time) AS hour_bucket,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS sample_count
FROM timeseries
WHERE point_id = %(point_id)s
  AND time >= %(date_start)s::timestamptz
  AND time <= %(date_end)s::timestamptz
GROUP BY hour_bucket
ORDER BY hour_bucket;
