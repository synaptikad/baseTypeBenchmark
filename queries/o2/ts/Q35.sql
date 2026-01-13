-- Q35: Validate Timeseries Append (QW1)
-- Status: NATIVE pour O2 (timeseries in shared ts schema via TimescaleDB)
-- Paramètres: %(point_id)s, %(reference_date)s
-- Semantic: Vérifie que les nouvelles valeurs timeseries ont été ajoutées

SELECT
    point_id,
    DATE(time) AS date,
    COUNT(*) AS record_count,
    ARRAY_AGG(time ORDER BY time DESC) FILTER (WHERE row_num <= 3) AS last_timestamps,
    ARRAY_AGG(value ORDER BY time DESC) FILTER (WHERE row_num <= 3) AS last_values
FROM (
    SELECT
        point_id,
        time,
        value,
        ROW_NUMBER() OVER (PARTITION BY point_id ORDER BY time DESC) AS row_num
    FROM ts.timeseries
    WHERE point_id = %(point_id)s
      AND DATE(time) = DATE(%(reference_date)s::timestamptz)
) sub
GROUP BY point_id, DATE(time);
