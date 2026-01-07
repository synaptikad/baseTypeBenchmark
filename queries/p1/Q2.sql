-- Q2: Functional Impact
-- Paramètre: $1 = EQUIPMENT_ID

WITH RECURSIVE impact_chain AS (
    -- Base
    SELECT
        $1::TEXT AS id,
        'Equipment'::TEXT AS type,
        ''::TEXT AS name,
        ''::TEXT AS relation_type,
        0 AS depth

    UNION ALL

    -- Récursion upstream (target → source)
    SELECT
        COALESCE(eq.id, b.id, f.id, s.id, site.id) AS id,
        CASE
            WHEN eq.id IS NOT NULL THEN 'Equipment'
            WHEN b.id IS NOT NULL THEN 'Building'
            WHEN f.id IS NOT NULL THEN 'Floor'
            WHEN s.id IS NOT NULL THEN 'Space'
            WHEN site.id IS NOT NULL THEN 'Site'
        END AS type,
        COALESCE(eq.name, b.name, f.name, s.name, site.name) AS name,
        ed.rel_type AS relation_type,
        ic.depth + 1
    FROM impact_chain ic
    JOIN edges ed ON ed.target_id = ic.id
        AND ed.rel_type IN ('FEEDS', 'SERVES', 'CONTAINS')
    LEFT JOIN equipment eq ON eq.id = ed.source_id
    LEFT JOIN buildings b ON b.id = ed.source_id
    LEFT JOIN floors f ON f.id = ed.source_id
    LEFT JOIN spaces s ON s.id = ed.source_id
    LEFT JOIN sites site ON site.id = ed.source_id
    WHERE ic.depth < 10
)
SELECT id, type, name, relation_type, depth
FROM impact_chain
WHERE depth > 0
ORDER BY depth, id;
