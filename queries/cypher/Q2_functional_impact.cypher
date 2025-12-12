// Impact fonctionnel d'un équipement sur les espaces et points associés
// Paramètres attendus: $equipment_id
MATCH (root:Node {id: $equipment_id, type: "Equipment"})
OPTIONAL MATCH (root)-[:HAS_PART*0..10]->(eq:Node {type: "Equipment"})
WITH DISTINCT eq
OPTIONAL MATCH (eq)-[:SERVES]->(sp:Node {type: "Space"})
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
RETURN DISTINCT sp.id AS space_id, sp.name AS space_name,
       eq.id AS equipment_id, eq.name AS equipment_name,
       pt.id AS point_id, pt.name AS point_name
ORDER BY space_id, equipment_id, point_id;
