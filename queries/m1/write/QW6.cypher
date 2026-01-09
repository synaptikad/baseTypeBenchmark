// QW6: Metadata Merge
// Équivalent M1 - SET multiple propriétés
// Paramètres: $equipment_id, $firmware_version, $firmware_update_date (propriétés individuelles)
//
// Note: Pas de merge natif en Cypher, on SET les propriétés explicitement
// Le caller doit passer chaque champ séparément

MATCH (eq:Equipment {id: $equipment_id})
SET eq.firmware_version = coalesce($firmware_version, eq.firmware_version),
    eq.firmware_update_date = coalesce($firmware_update_date, eq.firmware_update_date),
    eq.firmware_update_by = coalesce($firmware_update_by, eq.firmware_update_by)
RETURN eq.id AS id,
       {firmware_version: eq.firmware_version,
        firmware_update_date: eq.firmware_update_date} AS merged_metadata;
