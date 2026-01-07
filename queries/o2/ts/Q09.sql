-- Q9: Tenant Carbon (O2)
SELECT SUM(value) AS total_energy_kwh, SUM(value) * $4 AS carbon_kg_co2
FROM timeseries
WHERE point_id = ANY($1::text[])
  AND time >= $2::timestamptz AND time <= $3::timestamptz;
