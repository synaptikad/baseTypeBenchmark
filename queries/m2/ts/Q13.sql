-- Q13: Office Hours Comfort
-- Parametres: $1 = temp_point_ids, $2 = co2_point_ids, $3 = DATE_START, $4 = DATE_END

SELECT
    point_id,
    AVG(value) AS avg_value,
    COUNT(CASE WHEN value < 19 OR value > 26 THEN 1 END) AS out_of_range_count
FROM timeseries
WHERE point_id = ANY($1::text[])
  AND time >= $3::timestamptz
  AND time <= $4::timestamptz
  AND EXTRACT(dow FROM time) BETWEEN 1 AND 5
  AND EXTRACT(hour FROM time) BETWEEN 8 AND 17
GROUP BY point_id;
