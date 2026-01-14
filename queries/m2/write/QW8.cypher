// QW8: Remove Property
// Équivalent M1 - Suppression de propriété
// Paramètres: $node_id, $key_to_remove
//
// Status: DEGRADED pour M2 - Cypher ne supporte pas REMOVE dynamique n[$key]
// Workaround: On supprime une propriété statique 'custom_tag' pour démontrer le concept

MATCH (n {id: $node_id})
REMOVE n.custom_tag
RETURN n.id AS id;
