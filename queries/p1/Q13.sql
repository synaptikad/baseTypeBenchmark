-- Q13: Office Hours Comfort
-- Paramètres: $1 = BUILDING_ID, $2 = DATE_START, $3 = DATE_END

WITH office_points AS (
    SELECT DISTINCT p.id AS point_id, s.id AS space_id, s.name AS space_name, p.quantity
    FROM spaces s
    JOIN equipment eq ON eq.space_id = s.id OR EXISTS (
        SELECT 1 FROM edges e WHERE e.source_id = eq.id AND e.target_id = s.id
        AND e.rel_type IN ('SERVES', 'MONITORS', 'LOCATED_IN')
    )
    JOIN edges e_hp ON e_hp.source_id = eq.id AND e_hp.rel_type = 'HAS_POINT'
    JOIN points p ON p.id = e_hp.target_id
    WHERE s.building_id = $1
      AND s.space_type LIKE 'office%%'
      AND p.quantity IN ('temperature', 'co2')
),
office_hours_data AS (
    SELECT
        op.space_id,
        op.space_name,
        op.quantity,
        ts.value,
        ts.time
    FROM office_points op
    JOIN timeseries ts ON ts.point_id = op.point_id
    WHERE ts.time >= $2::timestamptz
      AND ts.time <= $3::timestamptz
      AND EXTRACT(dow FROM ts.time) BETWEEN 1 AND 5  -- Mon-Fri
      AND EXTRACT(hour FROM ts.time) BETWEEN 8 AND 17  -- 8h-18h
)
SELECT
    space_id,
    space_name,
    AVG(CASE WHEN quantity = 'temperature' THEN value END) AS avg_temp_c,
    AVG(CASE WHEN quantity = 'co2' THEN value END) AS avg_co2_ppm,
    COUNT(CASE WHEN quantity = 'temperature' AND (value < 19 OR value > 26) THEN 1 END) AS hours_out_of_range
FROM office_hours_data
GROUP BY space_id, space_name
ORDER BY hours_out_of_range DESC, space_id;
