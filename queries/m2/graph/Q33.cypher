// Q33: Latest Value per Space
// Status: DEGRADED pour M2 (orchestration Cypher -> SQL requise)
// Semantic: Get latest value for each point per space
// Parametres: $building_id
// Note: Retourne les space/point IDs pour orchestration avec TimescaleDB

MATCH (b:Building {id: $building_id})-[:CONTAINS*1..3]->(s:Space)<-[:SERVES]-(eq:Equipment)-[:HAS_POINT]->(p:Point)
RETURN
    s.id AS space_id,
    s.name AS space_name,
    p.id AS point_id,
    p.quantity AS quantity
ORDER BY space_id, point_id;

// Note: La recuperation des dernieres valeurs se fait via TimescaleDB
// dans une seconde requete SQL avec les point_ids retournes
