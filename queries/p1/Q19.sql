-- Q19: Equipment Digital Twin
-- Status: VERY DEGRADED pour P1
-- Raison: P1 ne peut pas construire un document JSON riche.
-- Cette implémentation retourne des colonnes séparées, pas un JSON.
-- Paramètres: $1 = EQUIPMENT_ID

SELECT
    eq.id,
    eq.name,
    eq.equipment_type AS type,
    NULL AS metadata,
    NULL AS capabilities,
    NULL AS protocol,
    jsonb_agg(jsonb_build_object(
        'id', p.id,
        'name', p.name,
        'quantity', p.quantity,
        'unit', p.unit
    )) AS points
FROM equipment eq
LEFT JOIN edges e_hp ON e_hp.source_id = eq.id AND e_hp.rel_type = 'HAS_POINT'
LEFT JOIN points p ON p.id = e_hp.target_id
WHERE eq.id = $1
GROUP BY eq.id, eq.name, eq.equipment_type;

-- Note: metadata, capabilities, protocol sont NULL car non disponibles en P1
