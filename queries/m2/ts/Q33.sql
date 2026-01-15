-- Q33: Latest Value per Space - TimescaleDB SQL pour M2 hybrid
-- Parametres: point_ids (array) - injected from Cypher query
-- Semantic: Get latest value for each point using LATERAL JOIN

SELECT
    point_id,
    value AS last_value,
    time AS last_time
FROM (
    SELECT
        point_id,
        value,
        time,
        ROW_NUMBER() OVER (PARTITION BY point_id ORDER BY time DESC) AS rn
    FROM timeseries
    WHERE point_id = ANY(%(point_ids)s::text[])
) sub
WHERE rn = 1
ORDER BY point_id;
