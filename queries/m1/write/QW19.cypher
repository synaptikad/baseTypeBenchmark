// QW19: Remove Capability (Cleanup for QW7)
// Retire une capability de la liste native Cypher
// Parametres: $equipment_id, $capability_to_remove
//
// Use case: Annuler l'ajout d'une capability (cleanup QW7)
// Utilise list comprehension pour filtrer

MATCH (eq:Equipment {id: $equipment_id})
WHERE eq.capabilities IS NOT NULL
  AND $capability_to_remove IN eq.capabilities
SET eq.capabilities = [cap IN eq.capabilities WHERE cap <> $capability_to_remove]
RETURN eq.id AS id, eq.capabilities AS updated_capabilities;
