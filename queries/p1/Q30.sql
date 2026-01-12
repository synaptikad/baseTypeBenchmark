-- Q30: Cycle Detection
-- Status: DEGRADED pour P1 (CTE avec detection revisite via ARRAY, O(n^2))
-- Semantic: Detect cycles in FEEDS relationships
-- Parametres: none

WITH RECURSIVE cycle_search AS (
    SELECT
        eq.id AS start_id,
        eq.id AS current_id,
        ARRAY[eq.id]::text[] AS path,
        1 AS depth,
        false AS found_cycle
    FROM equipment eq

    UNION ALL

    SELECT
        cs.start_id,
        eq.id,
        cs.path || eq.id,
        cs.depth + 1,
        eq.id = cs.start_id AS found_cycle
    FROM cycle_search cs
    JOIN edges e ON e.source_id = cs.current_id AND e.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = e.target_id
    WHERE cs.depth < 10
      AND NOT cs.found_cycle
      AND (eq.id = cs.start_id OR NOT (eq.id = ANY(cs.path)))
)
SELECT DISTINCT
    eq.id AS node_id,
    eq.equipment_type AS node_type,
    eq.name AS node_name,
    cs.depth AS cycle_length
FROM cycle_search cs
JOIN equipment eq ON eq.id = cs.start_id
WHERE cs.found_cycle
ORDER BY cycle_length, node_id;
