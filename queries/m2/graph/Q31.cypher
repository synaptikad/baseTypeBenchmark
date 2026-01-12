// Q31: Rolling Aggregation
// Status: NATIVE pour M2 (via TimescaleDB)
// Semantic: Calculate rolling averages and percentiles
// Note: M2 utilise TimescaleDB pour les agregations - voir Q31.sql dans m2/
// Cette query retourne les point_ids pour orchestration

MATCH (b:Building {id: $building_id})-[:CONTAINS*1..3]->(s:Space)<-[:SERVES]-(eq:Equipment)-[:HAS_POINT]->(p:Point)
RETURN DISTINCT p.id AS point_id
ORDER BY point_id;

// Note: L'agregation reelle se fait via TimescaleDB dans m2/Q31.sql
