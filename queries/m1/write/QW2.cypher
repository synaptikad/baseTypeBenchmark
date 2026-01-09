// QW2: Metadata Update
// Paramètres: $node_id, $tag_key, $tag_value
// Intention: Mettre à jour des métadonnées/tags sur un nœud
//
// Modèle M1: SET dynamique de propriété

MATCH (n {id: $node_id})
SET n[$tag_key] = $tag_value
RETURN count(n) AS rows_updated;
