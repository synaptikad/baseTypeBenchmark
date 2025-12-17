// Détection des points et équipements orphelins
// Aucun paramètre requis
MATCH (p:Node {type: "Point"})
WHERE NOT ( (:Node)-[:HAS_POINT]->(p) )
RETURN "Point" AS entity_type, p.id AS id, p.name AS name
UNION
MATCH (e:Node {type: "Equipment"})
WHERE NOT (e)-[:LOCATED_IN]->(:Node)
RETURN "Equipment" AS entity_type, e.id AS id, e.name AS name;
