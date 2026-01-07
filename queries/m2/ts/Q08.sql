-- Q8: Tenant Energy - Somme energie
-- Parametres: $1 = point_ids, $2 = DATE_START, $3 = DATE_END

SELECT
    SUM(value) AS total_energy_kwh,
    COUNT(DISTINCT point_id) AS point_count
FROM timeseries
WHERE point_id = ANY($1::text[])
  AND time >= $2::timestamptz
  AND time <= $3::timestamptz;
