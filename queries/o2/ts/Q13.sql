-- Q13: Office Hours Comfort (O2)
SELECT point_id, AVG(value) AS avg_value,
       COUNT(CASE WHEN value < 19 OR value > 26 THEN 1 END) AS out_of_range
FROM timeseries
WHERE point_id = ANY($1::text[])
  AND time >= $2::timestamptz AND time <= $3::timestamptz
  AND EXTRACT(dow FROM time) BETWEEN 1 AND 5
  AND EXTRACT(hour FROM time) BETWEEN 8 AND 17
GROUP BY point_id;
