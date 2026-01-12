-- Q30: Failure Impact Analysis
-- Status: DEGRADED pour P1 (CTE récursif, natif pour graphes)
-- Semantic: Si cet équipement tombe en panne, quels espaces/équipements sont impactés?
-- Parametres: $1 = EQUIPMENT_ID

WITH RECURSIVE impact_propagation AS (
    -- Point de départ: l'équipement en panne
    SELECT
        eq.id AS equipment_id,
        eq.name AS equipment_name,
        eq.equipment_type,
        0 AS hop_distance,
        ARRAY[eq.id]::text[] AS path
    FROM equipment eq
    WHERE eq.id = $1

    UNION ALL

    -- Propagation via FEEDS (équipements alimentés)
    SELECT
        eq.id,
        eq.name,
        eq.equipment_type,
        ip.hop_distance + 1,
        ip.path || eq.id
    FROM impact_propagation ip
    JOIN edges e ON e.source_id = ip.equipment_id AND e.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = e.target_id
    WHERE ip.hop_distance < 10
      AND NOT (eq.id = ANY(ip.path))
),
impacted_spaces AS (
    -- Espaces desservis par les équipements impactés
    SELECT DISTINCT
        s.id AS space_id,
        s.name AS space_name,
        ip.equipment_id,
        ip.equipment_name,
        ip.hop_distance
    FROM impact_propagation ip
    JOIN edges e ON e.source_id = ip.equipment_id AND e.rel_type IN ('SERVES', 'MONITORS', 'LOCATED_IN')
    JOIN spaces s ON s.id = e.target_id
)
SELECT
    'equipment' AS impact_type,
    equipment_id AS impacted_id,
    equipment_name AS impacted_name,
    equipment_type AS impacted_subtype,
    hop_distance,
    NULL AS served_by_equipment
FROM impact_propagation
WHERE hop_distance > 0  -- Exclure l'équipement source

UNION ALL

SELECT
    'space' AS impact_type,
    space_id AS impacted_id,
    space_name AS impacted_name,
    'Space' AS impacted_subtype,
    hop_distance,
    equipment_name AS served_by_equipment
FROM impacted_spaces

ORDER BY hop_distance, impact_type, impacted_id;
