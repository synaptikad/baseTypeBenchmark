// Q2: Impact fonctionnel des équipements sur les espaces (Functional Impact Analysis)
// Complexité: Traversée équipements → sous-composants → espaces et points
// Domaines: Equipment, Spatial
// Use case: Analyser l'impact des équipements principaux sur les espaces qu'ils desservent

// Parcourir tous les équipements principaux et leurs impacts
MATCH (b:Node {type: "Building"})-[:CONTAINS]->(f:Node {type: "Floor"})-[:CONTAINS]->(s:Node {type: "Space"})
WITH b, f, s
OPTIONAL MATCH (eq:Node {type: "Equipment"})-[:SERVES]->(s)
OPTIONAL MATCH (eq)-[:HAS_PART*0..3]->(sub_eq:Node {type: "Equipment"})
OPTIONAL MATCH (sub_eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
RETURN
    f.name AS floor_name,
    s.id AS space_id,
    s.name AS space_name,
    COUNT(DISTINCT eq) AS main_equipment_count,
    COUNT(DISTINCT sub_eq) AS sub_equipment_count,
    COUNT(DISTINCT pt) AS points_count
ORDER BY floor_name, space_name
LIMIT 100;
