// Q4: Inventaire des points de température par étage (Floor Temperature Points)
// Complexité: Traversée Building → Floor → Space → Equipment → Point avec filtrage
// Domaines: Spatial, Equipment, Point
// Use case: Inventorier tous les capteurs de température par étage pour audit HVAC

MATCH (b:Node {type: "Building"})-[:CONTAINS]->(f:Node {type: "Floor"})-[:CONTAINS]->(s:Node {type: "Space"})
WITH b, f, s
// Équipements dans ou servant l'espace
OPTIONAL MATCH (eq:Node {type: "Equipment"})-[:LOCATED_IN|SERVES]->(s)
WHERE eq.equipment_type IN ["AHU", "VAV", "FCU", "Thermostat", "TemperatureSensor"]
// Points de température
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
WHERE pt.quantity = "temperature"
WITH b.name AS building_name, f.id AS floor_id, f.name AS floor_name, f.floor_number AS floor_number,
     COLLECT(DISTINCT s) AS spaces, COLLECT(DISTINCT eq) AS hvac_equipments, COLLECT(DISTINCT pt) AS temp_points
RETURN
    building_name,
    floor_id,
    floor_name,
    floor_number,
    SIZE(spaces) AS spaces_count,
    SIZE(hvac_equipments) AS hvac_equipment_count,
    SIZE(temp_points) AS temp_points_count
ORDER BY building_name, floor_number
LIMIT 50;
