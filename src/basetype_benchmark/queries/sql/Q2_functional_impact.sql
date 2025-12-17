-- Q2: Impact fonctionnel en cascade (Functional Impact Analysis)
-- Complexite: Traversee recursive HAS_PART + jointure spatiale SERVES
-- Domaines: Equipment, Spatial
-- Use case: En cas de panne equipement parent, quels espaces sont impactes?

WITH RECURSIVE
root_equipments AS (
    SELECT n.id, n.name, n.properties->>'equipment_type' AS equip_type
    FROM nodes n
    WHERE n.type = 'Equipment'
      AND n.properties->>'equipment_type' IN ('Chiller', 'AHU', 'Boiler')
    LIMIT 10
),
equipment_cascade AS (
    SELECT
        r.id AS equip_id,
        r.name AS equip_name,
        r.equip_type,
        0 AS cascade_depth,
        ARRAY[r.id] AS cascade_path
    FROM root_equipments r

    UNION ALL

    SELECT
        child.id,
        child.name,
        child.properties->>'equipment_type',
        ec.cascade_depth + 1,
        ec.cascade_path || child.id
    FROM equipment_cascade ec
    JOIN edges e ON e.src_id = ec.equip_id AND e.rel_type = 'HAS_PART'
    JOIN nodes child ON child.id = e.dst_id AND child.type = 'Equipment'
    WHERE ec.cascade_depth < 6
      AND NOT (child.id = ANY(ec.cascade_path))
)
SELECT
    ec.equip_type,
    ec.cascade_depth,
    COUNT(DISTINCT ec.equip_id) AS equipments_in_cascade,
    COUNT(DISTINCT space.id) AS spaces_impacted,
    SUM(COALESCE((space.properties->>'capacity')::int, 0)) AS total_capacity_impacted
FROM equipment_cascade ec
LEFT JOIN edges serves ON serves.src_id = ec.equip_id AND serves.rel_type = 'SERVES'
LEFT JOIN nodes space ON space.id = serves.dst_id AND space.type = 'Space'
GROUP BY ec.equip_type, ec.cascade_depth
ORDER BY ec.equip_type, ec.cascade_depth;
