// QW2: Metadata Update
// Paramètres: $node_id, $tag_key, $tag_value
// Intention: Mettre à jour des métadonnées/tags sur un nœud
//
// Status: DEGRADED pour M1 - Cypher ne supporte pas SET dynamique n[$key]
// Workaround: On utilise une propriété statique 'custom_tag' pour démontrer le concept

MATCH (n {id: $node_id})
SET n.custom_tag = $tag_value
RETURN count(n) AS rows_updated;
