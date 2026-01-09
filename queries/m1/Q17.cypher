// Q17: Capability Filter
// Status: NATIVE pour M1/M2
// Parametre: $capability
// Note: capabilities est maintenant une liste Cypher native (pas JSON string)

MATCH (eq:Equipment)
WHERE eq.domain = 'HVAC'
  AND eq.capabilities IS NOT NULL
  AND $capability IN eq.capabilities
RETURN
    eq.id AS equipment_id,
    eq.name,
    eq.equipment_type AS equipment_type,
    eq.capabilities AS all_capabilities
ORDER BY equipment_type, equipment_id;
