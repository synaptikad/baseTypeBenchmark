-- Q12: Full Building Analytics
-- Parametres: $1 = energy_point_ids, $2 = temp_point_ids, $3 = occ_point_ids, $4 = DATE_START, $5 = DATE_END

SELECT
    SUM(CASE WHEN point_id = ANY($1::text[]) THEN value ELSE 0 END) AS total_energy_kwh,
    AVG(CASE WHEN point_id = ANY($2::text[]) THEN value END) AS avg_temperature_c,
    SUM(CASE WHEN point_id = ANY($3::text[]) THEN value ELSE 0 END)::integer AS total_occupancy
FROM timeseries
WHERE (point_id = ANY($1::text[]) OR point_id = ANY($2::text[]) OR point_id = ANY($3::text[]))
  AND time >= $4::timestamptz
  AND time <= $5::timestamptz;
