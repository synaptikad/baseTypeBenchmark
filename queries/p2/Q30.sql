-- Q30: Cycle Detection (P2 JSONB)
-- Status: DEGRADED pour P2 (CTE avec detection revisite via ARRAY, O(n^2))
-- Semantic: Detect cycles in FEEDS relationships
-- Parametres: none

WITH RECURSIVE cycle_search AS (
    SELECT
        n.id AS start_id,
        n.id AS current_id,
        ARRAY[n.id]::text[] AS path,
        1 AS depth,
        false AS found_cycle
    FROM nodes n
    WHERE n.node_type = 'Equipment'

    UNION ALL

    SELECT
        cs.start_id,
        n.id,
        cs.path || n.id,
        cs.depth + 1,
        n.id = cs.start_id AS found_cycle
    FROM cycle_search cs
    JOIN edges e ON e.source_id = cs.current_id AND e.rel_type = 'FEEDS'
    JOIN nodes n ON n.id = e.target_id AND n.node_type = 'Equipment'
    WHERE cs.depth < 10
      AND NOT cs.found_cycle
      AND (n.id = cs.start_id OR NOT (n.id = ANY(cs.path)))
)
SELECT DISTINCT
    n.id AS node_id,
    n.data->>'equipment_type' AS node_type,
    n.name AS node_name,
    cs.depth AS cycle_length
FROM cycle_search cs
JOIN nodes n ON n.id = cs.start_id AND n.node_type = 'Equipment'
WHERE cs.found_cycle
ORDER BY cycle_length, node_id;
