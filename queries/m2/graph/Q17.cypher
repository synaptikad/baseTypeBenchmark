// Q17: Capability Filter
// Status: NATIVE pour M1/M2 (avec MAGE)
// Paramètre: $capability
// Utilise json_util.from_json_list() de MAGE pour parser les capabilities JSON

MATCH (eq:Equipment)
WHERE eq.domain = 'HVAC'
  AND eq.capabilities IS NOT NULL
WITH eq, json_util.from_json_list(eq.capabilities) AS cap_list
WHERE cap_list IS NOT NULL
  AND any(c IN cap_list WHERE toString(c) = $capability)
RETURN
    eq.id AS equipment_id,
    eq.name,
    eq.equipment_type AS equipment_type,
    cap_list AS all_capabilities
ORDER BY equipment_type, equipment_id;
