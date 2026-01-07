-- Q9: Tenant Carbon Footprint
-- Parametres: $1 = point_ids, $2 = DATE_START, $3 = DATE_END, $4 = CO2_FACTOR

SELECT
    SUM(value) AS total_energy_kwh,
    SUM(value) * $4 AS carbon_kg_co2
FROM timeseries
WHERE point_id = ANY($1::text[])
  AND time >= $2::timestamptz
  AND time <= $3::timestamptz;
