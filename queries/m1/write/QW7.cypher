// QW7: Add Capability (Idempotent)
// Equivalent M1 - Ajout conditionnel a la liste capabilities native
// Parametres: $equipment_id, $new_capability
//
// Note: Le loader parse maintenant les JSON arrays comme listes Cypher natives.
// capabilities est donc une vraie liste Cypher, pas un JSON string.

MATCH (eq:Equipment {id: $equipment_id})
WHERE eq.capabilities IS NULL
   OR NOT $new_capability IN eq.capabilities
SET eq.capabilities = coalesce(eq.capabilities, []) + [$new_capability]
RETURN eq.id AS id, eq.capabilities AS updated_capabilities;
