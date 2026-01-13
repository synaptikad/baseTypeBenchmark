// Q35: Validate Timeseries Append (QW1)
// Valide que les données timeseries ont été ajoutées par QW1
// Paramètres: $point_id (le point_id utilisé dans QW1)
//
// Semantic: Vérifie que le chunk journalier contient les nouvelles valeurs

MATCH (p:Point {id: $point_id})-[:HAS_CHUNK]->(c:TimeseriesChunk)
WHERE c.date = left($reference_date, 10)
RETURN p.id AS point_id,
       c.date AS chunk_date,
       size(c.timestamps) AS timestamp_count,
       size(c.values) AS value_count,
       c.timestamps[-3..] AS last_timestamps,
       c.values[-3..] AS last_values;
