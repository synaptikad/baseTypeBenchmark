// QW1: Timeseries Append (SpinalCom style daily chunking)
// Paramètres: $chunks = [{point_id, date, timestamps[], values[]}, ...]
// Intention: Append de nouvelles mesures aux chunks journaliers
//
// Modèle M1: UNWIND les chunks, MERGE sur TimeseriesChunk, append aux arrays

UNWIND $chunks AS chunk

// Trouver le point parent
MATCH (p:Point {id: chunk.point_id})

// Créer ou mettre à jour le chunk journalier
MERGE (c:TimeseriesChunk {point_id: chunk.point_id, date: chunk.date})
ON CREATE SET
    c.timestamps = chunk.timestamps,
    c.values = chunk.values
ON MATCH SET
    c.timestamps = c.timestamps + chunk.timestamps,
    c.values = c.values + chunk.values

// Créer la relation si elle n'existe pas
MERGE (p)-[:HAS_CHUNK]->(c)

RETURN count(c) AS chunks_written;
