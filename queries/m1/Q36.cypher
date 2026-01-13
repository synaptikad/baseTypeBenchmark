// Q36: Validate Metadata Tag Update (QW2)
// Valide que le tag custom_tag a été mis à jour par QW2
// Paramètres: $node_id (le node_id utilisé dans QW2)
//
// Semantic: Vérifie que la propriété custom_tag a la valeur attendue

MATCH (n {id: $node_id})
RETURN n.id AS node_id,
       n.name AS node_name,
       n.custom_tag AS custom_tag,
       labels(n) AS node_labels;
