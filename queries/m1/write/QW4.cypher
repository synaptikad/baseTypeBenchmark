// QW4: Maintenance Event Append
// Équivalent M1 de l'append JSONB P2
// Paramètres: $equipment_id, $event (map avec date, type, technician, etc.)
//
// Note: Memgraph stocke les listes comme propriétés natives
// On utilise coalesce + list concatenation

MATCH (eq:Equipment {id: $equipment_id})
SET eq.maintenance_history = coalesce(eq.maintenance_history, []) + [$event]
RETURN eq.id AS id, size(eq.maintenance_history) AS event_count;
