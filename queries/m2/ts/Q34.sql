-- Q34: Materialized Energy Summary - TimescaleDB SQL pour M2 hybrid
-- Parametres: point_ids (array), building_id, date_start, date_end
-- Semantic: Compute daily energy aggregates (or read from continuous aggregate)
-- Note: Could use TimescaleDB continuous aggregates for true materialization

SELECT
    %(building_id)s AS building_id,
    time_bucket('1 day', time)::date AS day,
    SUM(value) AS total_energy_kwh,
    MAX(value) AS peak_power_kw,
    COUNT(DISTINCT point_id) AS meter_count
FROM timeseries
WHERE point_id = ANY(%(point_ids)s::text[])
  AND time >= %(date_start)s::timestamptz
  AND time <= %(date_end)s::timestamptz
GROUP BY time_bucket('1 day', time)::date
ORDER BY day;
