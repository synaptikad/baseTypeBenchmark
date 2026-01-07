-- Q19: Equipment Digital Twin
-- Status: NATIVE pour P2
-- Paramètres: $1 = EQUIPMENT_ID

SELECT jsonb_build_object(
    'id', eq.id,
    'name', eq.name,
    'type', eq.data->>'equipment_type',
    'domain', eq.data->>'domain',
    'metadata', eq.data->'metadata',
    'capabilities', eq.data->'capabilities',
    'protocol', eq.data->'protocol',
    'tags', eq.data->'tags',
    'points', COALESCE(
        (SELECT jsonb_agg(jsonb_build_object(
            'id', p.id,
            'name', p.name,
            'quantity', p.data->>'quantity',
            'unit', p.data->>'unit',
            'protocol', p.data->'protocol',
            'calibration', p.data->'calibration'
        ))
        FROM edges e_hp
        JOIN nodes p ON p.id = e_hp.target_id AND p.node_type = 'Point'
        WHERE e_hp.source_id = eq.id AND e_hp.rel_type = 'HAS_POINT'),
        '[]'::jsonb
    )
) AS digital_twin
FROM nodes eq
WHERE eq.id = $1 AND eq.node_type = 'Equipment';
