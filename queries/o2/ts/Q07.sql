-- Q7: Drift Top-20 (O2)
-- Parametres: point_ids (array), date_start, date_end

SELECT point_id, VAR_SAMP(value) AS variance, AVG(value) AS avg_value, COUNT(*) AS sample_count
FROM timeseries
WHERE point_id = ANY(%(point_ids)s::text[])
  AND time >= %(date_start)s::timestamptz
  AND time <= %(date_end)s::timestamptz
GROUP BY point_id
ORDER BY variance DESC NULLS LAST
LIMIT 20;
