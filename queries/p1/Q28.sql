-- Q28: Tenant Impact Chain
-- Status: DEGRADED pour P1 (5 JOINs verbose mais fonctionnel)
-- Semantic: If this submeter is cut, which tenants are impacted?
-- Parametres: $1 = METER_ID

WITH meter_equipment AS (
    SELECT id FROM equipment
    WHERE id = $1 AND equipment_type IN ('SubMeter', 'MainMeter')
),
fed_equipment AS (
    -- Equipment fed by the meter (up to 3 hops)
    SELECT DISTINCT eq.id AS equipment_id
    FROM meter_equipment m
    JOIN edges e1 ON e1.source_id = m.id AND e1.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = e1.target_id

    UNION

    SELECT DISTINCT eq.id
    FROM meter_equipment m
    JOIN edges e1 ON e1.source_id = m.id AND e1.rel_type = 'FEEDS'
    JOIN edges e2 ON e2.source_id = e1.target_id AND e2.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = e2.target_id

    UNION

    SELECT DISTINCT eq.id
    FROM meter_equipment m
    JOIN edges e1 ON e1.source_id = m.id AND e1.rel_type = 'FEEDS'
    JOIN edges e2 ON e2.source_id = e1.target_id AND e2.rel_type = 'FEEDS'
    JOIN edges e3 ON e3.source_id = e2.target_id AND e3.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = e3.target_id
),
served_spaces AS (
    SELECT DISTINCT s.id AS space_id, fe.equipment_id
    FROM fed_equipment fe
    JOIN edges e ON e.source_id = fe.equipment_id AND e.rel_type = 'SERVES'
    JOIN spaces s ON s.id = e.target_id
),
impacted_tenants AS (
    SELECT
        t.id AS tenant_id,
        t.name AS tenant_name,
        COUNT(DISTINCT ss.space_id) AS affected_spaces,
        COUNT(DISTINCT ss.equipment_id) AS affected_equipment
    FROM served_spaces ss
    JOIN edges e ON e.target_id = ss.space_id AND e.rel_type = 'OCCUPIES'
    JOIN tenants t ON t.id = e.source_id
    GROUP BY t.id, t.name
)
SELECT tenant_id, tenant_name, affected_spaces, affected_equipment
FROM impacted_tenants
ORDER BY affected_equipment DESC, tenant_id;
