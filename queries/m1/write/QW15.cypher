// QW15: Remove Relation
// Supprimer une relation par source/target/type
// Parametres: $source_id, $target_id, $rel_type
//
// Use case: Supprimer une relation specifique entre deux noeuds
// Note: Cypher ne supporte pas les types de relation dynamiques,
// on utilise FEEDS par defaut (cleanup de QW3)

MATCH (a {id: $source_id})-[r:FEEDS]->(b {id: $target_id})
DELETE r
RETURN a.id AS source_id, b.id AS target_id, 'FEEDS' AS rel_type, 1 AS relations_deleted;
