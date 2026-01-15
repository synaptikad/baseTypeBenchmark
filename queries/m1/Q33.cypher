// Q33: Latest Value per Space
// Status: DEGRADED pour M1 (pas de LATERAL, pas de TimescaleDB)
// Semantic: Get latest value for each point per space
// Parametres: $building_id
// Note: Calcul applicatif via UNWIND TimeseriesChunk - moins efficace que LATERAL

// Trouver tous les espaces du bâtiment avec leurs points
MATCH (b:Building {id: $building_id})-[:CONTAINS*1..3]->(s:Space)<-[:SERVES]-(eq:Equipment)-[:HAS_POINT]->(p:Point)

// Récupérer le chunk le plus récent pour chaque point
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WITH s, p, chunk
ORDER BY chunk.date DESC
WITH s, p, collect(chunk)[0] AS latest_chunk

// Extraire la dernière valeur du chunk (dernier index du tableau)
WITH s, p, latest_chunk,
     latest_chunk.timestamps[size(latest_chunk.timestamps) - 1] AS last_ts,
     latest_chunk.values[size(latest_chunk.values) - 1] AS last_val

RETURN
    s.id AS space_id,
    s.name AS space_name,
    p.id AS point_id,
    p.quantity AS quantity,
    last_val AS last_value,
    last_ts AS last_time
ORDER BY space_id, point_id
LIMIT 100;
