// Inventaire des points de température sur un étage
// Paramètres attendus: $floor_id
MATCH (f:Node {id: $floor_id, type: "Floor"})-[:CONTAINS]->(sp:Node {type: "Space"})
OPTIONAL MATCH (eq:Node {type: "Equipment"})-[:LOCATED_IN]->(sp)
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
WHERE pt.quantity = "temperature"
RETURN DISTINCT sp.id AS space_id, sp.name AS space_name,
       eq.id AS equipment_id, eq.name AS equipment_name,
       pt.id AS point_id, pt.name AS point_name
ORDER BY space_id, equipment_id, point_id;
