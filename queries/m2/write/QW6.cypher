// QW6: Metadata Merge
// Équivalent M1 - SET multiple propriétés
// Paramètres: $equipment_id, $reference_date (from queries_params.yaml)
//
// Note: Pas de merge natif en Cypher, on SET les propriétés explicitement
// Uses available params + hardcoded firmware version for benchmark consistency

MATCH (eq:Equipment {id: $equipment_id})
SET eq.firmware_version = '3.2.1',
    eq.firmware_update_date = $reference_date,
    eq.firmware_update_by = 'system_update'
RETURN eq.id AS id,
       {firmware_version: eq.firmware_version,
        firmware_update_date: eq.firmware_update_date} AS merged_metadata;
