// QW20: Restore Removed Key (Cleanup for QW8)
// Restaure une propriete precedemment supprimee
// Parametres: $node_id, $value_to_restore
//
// Use case: Annuler la suppression de custom_tag (cleanup QW8)
// Status: DEGRADED - Cypher ne supporte pas SET dynamique n[$key]
// Workaround: Restaure la propriete statique 'custom_tag'

MATCH (n {id: $node_id})
SET n.custom_tag = $value_to_restore
RETURN n.id AS id, n.custom_tag AS restored_value;
