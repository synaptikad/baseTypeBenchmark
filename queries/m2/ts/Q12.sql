-- Q12: Full Building Analytics
-- Parametres: energy_point_ids, temp_point_ids, occ_point_ids, date_start, date_end (lowercase for M2 hybrid)

SELECT
    SUM(CASE WHEN point_id = ANY(%(energy_point_ids)s::text[]) THEN value ELSE 0 END) AS total_energy_kwh,
    AVG(CASE WHEN point_id = ANY(%(temp_point_ids)s::text[]) THEN value END) AS avg_temperature_c,
    SUM(CASE WHEN point_id = ANY(%(occ_point_ids)s::text[]) THEN value ELSE 0 END)::integer AS total_occupancy
FROM timeseries
WHERE (point_id = ANY(%(energy_point_ids)s::text[]) OR point_id = ANY(%(temp_point_ids)s::text[]) OR point_id = ANY(%(occ_point_ids)s::text[]))
  AND time >= %(date_start)s::timestamptz
  AND time <= %(date_end)s::timestamptz;
