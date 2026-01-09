-- Q8: Tenant Energy (O2)
-- Parametres: point_ids (array), date_start, date_end

SELECT SUM(value) AS total_energy_kwh, COUNT(DISTINCT point_id) AS point_count
FROM timeseries
WHERE point_id = ANY(%(point_ids)s::text[])
  AND time >= %(date_start)s::timestamptz
  AND time <= %(date_end)s::timestamptz;
