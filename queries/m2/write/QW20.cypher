// QW20: Restore Removed Key (cleanup QW8)
// Restaure la propriété custom_tag supprimée par QW8
// Paramètres: $qw8_node_id, $qw8_original_value
// Note: Cypher ne supporte pas SET dynamique, donc on utilise le nom statique

MATCH (n {id: $qw8_node_id})
SET n.custom_tag = $qw8_original_value
RETURN n.id AS node_id;
