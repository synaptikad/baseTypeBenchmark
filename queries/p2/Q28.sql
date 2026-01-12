-- Q28: Tenant Impact Chain (P2 JSONB)
-- Status: DEGRADED pour P2 (5 JOINs verbose mais fonctionnel)
-- Semantic: If this submeter is cut, which tenants are impacted?
-- Parametres: $1 = METER_ID

WITH meter_equipment AS (
    SELECT id FROM nodes
    WHERE id = $1
      AND node_type = 'Equipment'
      AND data->>'equipment_type' IN ('SubMeter', 'MainMeter')
),
fed_equipment AS (
    SELECT DISTINCT n.id AS equipment_id
    FROM meter_equipment m
    JOIN edges e1 ON e1.source_id = m.id AND e1.rel_type = 'FEEDS'
    JOIN nodes n ON n.id = e1.target_id AND n.node_type = 'Equipment'

    UNION

    SELECT DISTINCT n.id
    FROM meter_equipment m
    JOIN edges e1 ON e1.source_id = m.id AND e1.rel_type = 'FEEDS'
    JOIN edges e2 ON e2.source_id = e1.target_id AND e2.rel_type = 'FEEDS'
    JOIN nodes n ON n.id = e2.target_id AND n.node_type = 'Equipment'

    UNION

    SELECT DISTINCT n.id
    FROM meter_equipment m
    JOIN edges e1 ON e1.source_id = m.id AND e1.rel_type = 'FEEDS'
    JOIN edges e2 ON e2.source_id = e1.target_id AND e2.rel_type = 'FEEDS'
    JOIN edges e3 ON e3.source_id = e2.target_id AND e3.rel_type = 'FEEDS'
    JOIN nodes n ON n.id = e3.target_id AND n.node_type = 'Equipment'
),
served_spaces AS (
    SELECT DISTINCT n.id AS space_id, fe.equipment_id
    FROM fed_equipment fe
    JOIN edges e ON e.source_id = fe.equipment_id AND e.rel_type = 'SERVES'
    JOIN nodes n ON n.id = e.target_id AND n.node_type = 'Space'
),
impacted_tenants AS (
    SELECT
        t.id AS tenant_id,
        t.name AS tenant_name,
        COUNT(DISTINCT ss.space_id) AS affected_spaces,
        COUNT(DISTINCT ss.equipment_id) AS affected_equipment
    FROM served_spaces ss
    JOIN edges e ON e.target_id = ss.space_id AND e.rel_type = 'OCCUPIES'
    JOIN nodes t ON t.id = e.source_id AND t.node_type = 'Tenant'
    GROUP BY t.id, t.name
)
SELECT tenant_id, tenant_name, affected_spaces, affected_equipment
FROM impacted_tenants
ORDER BY affected_equipment DESC, tenant_id;
