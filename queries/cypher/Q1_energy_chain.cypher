// Chaîne énergétique à partir d'un compteur (profondeur FEEDS bornée)
// Paramètres attendus: $meter_id
MATCH (m:Node {id: $meter_id})
OPTIONAL MATCH path=(m)-[:FEEDS*1..10]->(eq:Node)
WHERE eq.type IN ["Equipment", "Meter"]
WITH DISTINCT eq
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
RETURN DISTINCT eq.id AS equipment_id, eq.name AS equipment_name,
       pt.id AS point_id, pt.name AS point_name
ORDER BY equipment_id, point_id;
