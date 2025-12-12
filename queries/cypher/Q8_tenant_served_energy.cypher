// Sélection des points de puissance pour les espaces occupés par un locataire
// Paramètres attendus: $tenant_id, $time_range (non utilisé côté graphe)
MATCH (t:Node {id: $tenant_id, type: "Tenant"})-[:OCCUPIES]->(sp:Node {type: "Space"})
MATCH (eq:Node {type: "Equipment"})-[:SERVES]->(sp)
OPTIONAL MATCH (eq)-[:HAS_PART*0..5]->(sub:Node {type: "Equipment"})
WITH DISTINCT sp, eq, sub
UNWIND [eq, sub] AS candidate
WITH sp, candidate WHERE candidate IS NOT NULL
OPTIONAL MATCH (candidate)-[:HAS_POINT]->(pt:Node {type: "Point"})
WHERE pt.quantity = "power"
RETURN DISTINCT pt.id AS point_id, candidate.id AS equipment_id, sp.id AS space_id
ORDER BY point_id;
