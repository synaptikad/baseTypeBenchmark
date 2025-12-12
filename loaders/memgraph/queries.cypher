// Requêtes Cypher pour Memgraph (Q1 à Q8)

// Q1 - Chaîne énergétique
MATCH (m:Node {id: $meter_id})
OPTIONAL MATCH (m)-[:FEEDS*1..10]->(eq:Node)
WHERE eq.type IN ["Equipment", "Meter"]
WITH DISTINCT eq
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
RETURN DISTINCT eq.id AS equipment_id, eq.name AS equipment_name,
       pt.id AS point_id, pt.name AS point_name
ORDER BY equipment_id, point_id;

// Q2 - Impact fonctionnel
MATCH (root:Node {id: $equipment_id, type: "Equipment"})
OPTIONAL MATCH (root)-[:HAS_PART*0..10]->(eq:Node {type: "Equipment"})
WITH DISTINCT eq
OPTIONAL MATCH (eq)-[:SERVES]->(sp:Node {type: "Space"})
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
RETURN DISTINCT sp.id AS space_id, sp.name AS space_name,
       eq.id AS equipment_id, eq.name AS equipment_name,
       pt.id AS point_id, pt.name AS point_name
ORDER BY space_id, equipment_id, point_id;

// Q3 - Services rendus à un espace
MATCH (sp:Node {id: $space_id, type: "Space"})
OPTIONAL MATCH (eq:Node {type: "Equipment"})-[:SERVES]->(sp)
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
RETURN DISTINCT eq.id AS equipment_id, eq.name AS equipment_name,
       pt.id AS point_id, pt.name AS point_name
ORDER BY equipment_id, point_id;

// Q4 - Inventaire température par étage
MATCH (f:Node {id: $floor_id, type: "Floor"})-[:CONTAINS]->(sp:Node {type: "Space"})
OPTIONAL MATCH (eq:Node {type: "Equipment"})-[:LOCATED_IN]->(sp)
OPTIONAL MATCH (eq)-[:HAS_POINT]->(pt:Node {type: "Point"})
WHERE pt.quantity = "temperature"
RETURN DISTINCT sp.id AS space_id, sp.name AS space_name,
       eq.id AS equipment_id, eq.name AS equipment_name,
       pt.id AS point_id, pt.name AS point_name
ORDER BY space_id, equipment_id, point_id;

// Q5 - Orphelins
MATCH (p:Node {type: "Point"})
WHERE NOT ( (:Node)-[:HAS_POINT]->(p) )
RETURN "Point" AS entity_type, p.id AS id, p.name AS name
UNION
MATCH (e:Node {type: "Equipment"})
WHERE NOT (e)-[:LOCATED_IN]->(:Node)
RETURN "Equipment" AS entity_type, e.id AS id, e.name AS name;

// Q6 - Agrégation horaire (non applicable dans Memgraph)
RETURN "Not applicable in Memgraph; utiliser TimescaleDB" AS note;

// Q7 - Dérive top 20 (non applicable dans Memgraph)
RETURN "Not applicable in Memgraph; utiliser TimescaleDB" AS note;

// Q8 - Points de puissance pour un locataire
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
