// Q38: Validate Property Removal (QW8)
// Valide que la propriété custom_tag a été supprimée par QW8
// Paramètres: $node_id (le node_id utilisé dans QW8)
//
// Semantic: Vérifie que la propriété custom_tag n'existe plus

MATCH (n {id: $node_id})
RETURN n.id AS node_id,
       n.name AS node_name,
       n.custom_tag IS NULL AS tag_removed,
       keys(n) AS remaining_properties;
