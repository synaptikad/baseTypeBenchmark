-- Q25: Equipment Audit Trail
-- Status: NATIVE pour P2 (validation post-QW4/5/6)
-- Paramètres: equipment_id
-- Démontre: Agrégation multi-source JSONB (maintenance + calibration + firmware)

SELECT
    eq.id AS equipment_id,
    eq.name,
    eq.data->>'equipment_type' AS equipment_type,

    -- Firmware info (from QW6 metadata merge)
    eq.data->'metadata'->>'firmware_version' AS current_firmware,
    eq.data->'metadata'->>'firmware_update_date' AS last_firmware_update,

    -- Maintenance summary (from QW4)
    jsonb_array_length(COALESCE(eq.data->'maintenance_history', '[]'::jsonb)) AS maintenance_events,
    (
        SELECT MAX((evt->>'date')::date)
        FROM jsonb_array_elements(eq.data->'maintenance_history') AS evt
    ) AS last_maintenance_date,

    -- Calibration summary (from related points via QW5)
    (
        SELECT jsonb_agg(jsonb_build_object(
            'point_id', p.id,
            'last_calibration', p.data->'calibration'->>'last_date',
            'next_calibration', p.data->'calibration'->>'next_date',
            'is_overdue', (p.data->'calibration'->>'next_date')::date < CURRENT_DATE
        ))
        FROM p2.edges e
        JOIN p2.nodes p ON p.id = e.target_id AND p.node_type = 'Point'
        WHERE e.source_id = eq.id AND e.rel_type = 'HAS_POINT'
          AND p.data->'calibration' IS NOT NULL
    ) AS points_calibration_status,

    -- Overall health score (computed)
    CASE
        WHEN eq.data->'metadata'->>'maintenance_priority' = 'critical' THEN 'CRITICAL'
        WHEN jsonb_array_length(COALESCE(eq.data->'maintenance_history', '[]'::jsonb)) > 5 THEN 'HIGH_MAINTENANCE'
        ELSE 'NORMAL'
    END AS health_status

FROM p2.nodes eq
WHERE eq.id = %(equipment_id)s
  AND eq.node_type = 'Equipment';
