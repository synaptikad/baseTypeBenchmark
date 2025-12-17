-- Q3: Services par espace (Space Services Inventory)
-- Complexité: Jointures multi-niveaux Spatial → Equipment → Point
-- Domaines: Spatial, Equipment
-- Use case: Pour chaque espace, lister tous les équipements qui le desservent

SELECT
    f.name AS floor_name,
    s.id AS space_id,
    s.name AS space_name,
    s.properties->>'space_type' AS space_type,
    COALESCE((s.properties->>'area_sqm')::int, 0) AS area_sqm,
    COALESCE((s.properties->>'capacity')::int, 0) AS capacity,
    COUNT(DISTINCT eq.id) AS equipment_count,
    ARRAY_AGG(DISTINCT eq.properties->>'equipment_type') FILTER (WHERE eq.id IS NOT NULL) AS equipment_types,
    COUNT(DISTINCT pt.id) AS points_count
FROM nodes b
JOIN edges e1 ON e1.src_id = b.id AND e1.rel_type = 'CONTAINS'
JOIN nodes f ON f.id = e1.dst_id AND f.type = 'Floor'
JOIN edges e2 ON e2.src_id = f.id AND e2.rel_type = 'CONTAINS'
JOIN nodes s ON s.id = e2.dst_id AND s.type = 'Space'
-- Équipements qui servent cet espace
LEFT JOIN edges serves ON serves.dst_id = s.id AND serves.rel_type = 'SERVES'
LEFT JOIN nodes eq ON eq.id = serves.src_id AND eq.type = 'Equipment'
-- Points de mesure sur ces équipements
LEFT JOIN edges hp ON hp.src_id = eq.id AND hp.rel_type = 'HAS_POINT'
LEFT JOIN nodes pt ON pt.id = hp.dst_id AND pt.type = 'Point'
WHERE b.type = 'Building'
GROUP BY f.name, s.id, s.name, s.properties->>'space_type',
         s.properties->>'area_sqm', s.properties->>'capacity'
ORDER BY f.name, s.name
LIMIT 100;
