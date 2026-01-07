-- Q7: Drift Top-20 (O2)
-- Paramètres: $1 = point_ids, $2 = DATE_START, $3 = DATE_END

SELECT point_id, VAR_SAMP(value) AS variance, AVG(value) AS avg_value, COUNT(*) AS sample_count
FROM timeseries
WHERE point_id = ANY($1::text[])
  AND time >= $2::timestamptz AND time <= $3::timestamptz
GROUP BY point_id
ORDER BY variance DESC NULLS LAST
LIMIT 20;
