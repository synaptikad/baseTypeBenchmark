-- Q1: Chaîne de distribution énergétique (Energy Distribution Chain)
-- Complexité: Traversée récursive de l'arbre de compteurs (8 niveaux max)
-- Domaines: Energy, Equipment
-- Use case: Identifier tous les équipements alimentés par un compteur donné

WITH RECURSIVE energy_tree AS (
    -- Point de départ: le compteur racine (point de livraison)
    SELECT
        n.id AS meter_id,
        n.name AS meter_name,
        0 AS depth,
        ARRAY[n.id] AS path
    FROM nodes n
    WHERE n.type = 'Meter'
    AND (n.properties->>'is_root')::boolean = true

    UNION ALL

    -- Récursion: suivre les relations FEEDS
    SELECT
        child.id,
        child.name,
        et.depth + 1,
        et.path || child.id
    FROM energy_tree et
    JOIN edges e ON e.src_id = et.meter_id AND e.rel_type = 'FEEDS'
    JOIN nodes child ON child.id = e.dst_id
    WHERE et.depth < 8
    AND NOT (child.id = ANY(et.path))  -- Éviter les cycles
)
SELECT
    et.depth,
    COUNT(DISTINCT et.meter_id) AS meters_at_level,
    COUNT(DISTINCT CASE WHEN n.type = 'Equipment' THEN n.id END) AS equipments_fed
FROM energy_tree et
LEFT JOIN edges e ON e.src_id = et.meter_id AND e.rel_type = 'FEEDS'
LEFT JOIN nodes n ON n.id = e.dst_id
GROUP BY et.depth
ORDER BY et.depth;
