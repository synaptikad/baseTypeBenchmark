// Équipements qui desservent un espace et leurs points
// Paramètres attendus: $space_id
MATCH (sp:Node {id: $space_id, type: "Space"})
OPTIONAL MATCH (eq:Node {type: "Equipment"})-[:SERVES]->(sp)
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
RETURN DISTINCT eq.id AS equipment_id, eq.name AS equipment_name,
       pt.id AS point_id, pt.name AS point_name
ORDER BY equipment_id, point_id;
