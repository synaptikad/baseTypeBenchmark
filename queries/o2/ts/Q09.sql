-- Q9: Tenant Carbon (O2)
-- Parametres: point_ids (array), date_start, date_end, co2_factor

SELECT SUM(value) AS total_energy_kwh, SUM(value) * %(co2_factor)s AS carbon_kg_co2
FROM timeseries
WHERE point_id = ANY(%(point_ids)s::text[])
  AND time >= %(date_start)s::timestamptz
  AND time <= %(date_end)s::timestamptz;
