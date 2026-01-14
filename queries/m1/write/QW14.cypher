// QW14: Remove Calibration Tag
// Supprimer une propriete tag de calibration
// Parametres: $node_id, $key_to_remove
//
// Use case: Retirer un tag de calibration obsolete
// Note: Cypher ne supporte pas REMOVE dynamique, on cible 'calibration_tag'

MATCH (n {id: $node_id})
REMOVE n.calibration_tag
RETURN n.id AS id;
