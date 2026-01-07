-- Q2: Functional Impact (P2 JSONB)
-- Paramètre: $1 = EQUIPMENT_ID

WITH RECURSIVE impact_chain AS (
    -- Base
    SELECT
        n.id,
        n.node_type AS type,
        n.name,
        ''::TEXT AS relation_type,
        0 AS depth
    FROM nodes n
    WHERE n.id = $1

    UNION ALL

    -- Récursion upstream
    SELECT
        n.id,
        n.node_type AS type,
        n.name,
        ed.rel_type AS relation_type,
        ic.depth + 1
    FROM impact_chain ic
    JOIN edges ed ON ed.target_id = ic.id
        AND ed.rel_type IN ('FEEDS', 'SERVES', 'CONTAINS')
    JOIN nodes n ON n.id = ed.source_id
    WHERE ic.depth < 10
)
SELECT id, type, name, relation_type, depth
FROM impact_chain
WHERE depth > 0
ORDER BY depth, id;
