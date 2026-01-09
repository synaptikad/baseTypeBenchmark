-- Q13: Office Hours Comfort
-- Parametres: temp_point_ids, co2_point_ids, date_start, date_end (lowercase for M2 hybrid)

SELECT
    point_id,
    AVG(value) AS avg_value,
    COUNT(CASE WHEN value < 19 OR value > 26 THEN 1 END) AS out_of_range_count
FROM timeseries
WHERE point_id = ANY(%(temp_point_ids)s::text[])
  AND time >= %(date_start)s::timestamptz
  AND time <= %(date_end)s::timestamptz
  AND EXTRACT(dow FROM time) BETWEEN 1 AND 5
  AND EXTRACT(hour FROM time) BETWEEN 8 AND 17
GROUP BY point_id;
