// QW3: Relation Mutation
// Paramètres: $source_id, $target_id, $rel_type
// Intention: Ajouter une relation entre deux nœuds
//
// Modèle M1: MERGE pour créer la relation si elle n'existe pas
// Note: Cypher ne supporte pas les types de relation dynamiques,
// donc on utilise FEEDS par défaut (la relation la plus commune)

MATCH (a {id: $source_id}), (b {id: $target_id})
MERGE (a)-[r:FEEDS]->(b)
RETURN count(r) AS rows_inserted;
