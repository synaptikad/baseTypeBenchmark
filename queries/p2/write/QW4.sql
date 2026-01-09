-- QW4: Append to JSONB Array (Maintenance Event)
-- Démontre: Ajout d'élément à un array JSONB existant
-- Paramètres: %(equipment_id)s, %(event)s (jsonb object)
--
-- Use case: Ajouter un événement de maintenance à l'historique
-- Le champ maintenance_history est créé s'il n'existe pas

UPDATE p2.nodes
SET data = jsonb_set(
    COALESCE(data, '{}'::jsonb),
    '{maintenance_history}',
    COALESCE(data->'maintenance_history', '[]'::jsonb) || %(event)s::jsonb,
    true
)
WHERE id = %(equipment_id)s
  AND node_type = 'Equipment'
RETURNING id, jsonb_array_length(data->'maintenance_history') AS event_count;
