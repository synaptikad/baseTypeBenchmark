-- Q6: Hourly Aggregation
-- Paradigme: M2 (TimescaleDB externe pour Memgraph)
-- Paramètres: $1 = POINT_ID, $2 = DATE_START, $3 = DATE_END
--
-- Note: Cette query s'exécute sur TimescaleDB, pas sur Memgraph.
-- Le runner M2 doit router cette query vers la connexion TimescaleDB.

SELECT
    time_bucket('1 hour', time) AS hour_bucket,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS sample_count
FROM timeseries
WHERE point_id = $1
  AND time >= $2::timestamptz
  AND time <= $3::timestamptz
GROUP BY hour_bucket
ORDER BY hour_bucket;
