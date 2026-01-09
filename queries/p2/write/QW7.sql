-- QW7: Add Capability (Array Element)
-- Démontre: Ajout conditionnel d'un élément à un array (évite doublons)
-- Paramètres: %(equipment_id)s, %(new_capability)s
--
-- Use case: Ajouter une nouvelle capability si elle n'existe pas déjà
-- Utilise NOT @> pour vérifier l'absence

UPDATE p2.nodes
SET data = jsonb_set(
    data,
    '{capabilities}',
    COALESCE(data->'capabilities', '[]'::jsonb) || jsonb_build_array(%(new_capability)s)
)
WHERE id = %(equipment_id)s
  AND node_type = 'Equipment'
  AND NOT (COALESCE(data->'capabilities', '[]'::jsonb) @> jsonb_build_array(%(new_capability)s))
RETURNING
    id,
    data->'capabilities' AS updated_capabilities;
