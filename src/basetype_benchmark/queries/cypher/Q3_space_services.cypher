// Q3: Services par espace (Space Services Inventory)
// Complexité: Jointures multi-niveaux Spatial → Equipment → Point
// Domaines: Spatial, Equipment
// Use case: Pour chaque espace, lister tous les équipements qui le desservent

MATCH (b:Node {type: "Building"})-[:CONTAINS]->(f:Node {type: "Floor"})-[:CONTAINS]->(s:Node {type: "Space"})
WITH f, s
OPTIONAL MATCH (eq:Node {type: "Equipment"})-[:SERVES]->(s)
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
WITH f.name AS floor_name, s.id AS space_id, s.name AS space_name,
     s.space_type AS space_type, s.area_sqm AS area_sqm, s.capacity AS capacity,
     COLLECT(DISTINCT eq) AS equipments, COLLECT(DISTINCT pt) AS points
RETURN
    floor_name,
    space_id,
    space_name,
    space_type,
    COALESCE(area_sqm, 0) AS area_sqm,
    COALESCE(capacity, 0) AS capacity,
    SIZE(equipments) AS equipment_count,
    SIZE(points) AS points_count
ORDER BY floor_name, space_name
LIMIT 100;
