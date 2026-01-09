-- QW5: Deep Nested Update (Calibration)
-- Démontre: Mise à jour d'un champ profondément imbriqué
-- Paramètres: %(point_id)s, %(calibration_date)s, %(next_date)s, %(technician)s
--
-- Use case: Mettre à jour les dates de calibration d'un point
-- Préserve les autres champs de calibration (offset, etc.)

UPDATE p2.nodes
SET data = jsonb_set(
    jsonb_set(
        jsonb_set(
            COALESCE(data, '{}'::jsonb),
            '{calibration,last_date}',
            to_jsonb(%(calibration_date)s::text),
            true
        ),
        '{calibration,next_date}',
        to_jsonb(%(next_date)s::text),
        true
    ),
    '{calibration,technician}',
    to_jsonb(%(technician)s::text),
    true
)
WHERE id = %(point_id)s
  AND node_type = 'Point'
RETURNING
    id,
    data->'calibration' AS updated_calibration;
