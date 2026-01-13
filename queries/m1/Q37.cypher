// Q37: Validate Relation Mutation (QW3)
// Valide que la relation FEEDS a été créée par QW3
// Paramètres: $source_id, $target_id (les IDs utilisés dans QW3)
//
// Semantic: Vérifie que la relation FEEDS existe entre source et target

MATCH (a {id: $source_id})-[r:FEEDS]->(b {id: $target_id})
RETURN a.id AS source_id,
       a.name AS source_name,
       type(r) AS rel_type,
       b.id AS target_id,
       b.name AS target_name;
