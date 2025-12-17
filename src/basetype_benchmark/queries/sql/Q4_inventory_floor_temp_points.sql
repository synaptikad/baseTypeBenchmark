-- Q4: Inventaire des points de température par étage (Floor Temperature Points)
-- Complexité: Traversée Building → Floor → Space → Equipment → Point avec filtrage
-- Domaines: Spatial, Equipment, Point
-- Use case: Inventorier tous les capteurs de température par étage pour audit HVAC

SELECT
    b.name AS building_name,
    f.id AS floor_id,
    f.name AS floor_name,
    f.properties->>'floor_number' AS floor_number,
    COUNT(DISTINCT s.id) AS spaces_count,
    COUNT(DISTINCT eq.id) AS hvac_equipment_count,
    COUNT(DISTINCT pt.id) AS temp_points_count,
    ARRAY_AGG(DISTINCT pt.id) FILTER (WHERE pt.id IS NOT NULL) AS point_ids,
    -- Statistiques sur les types d'équipements HVAC
    COUNT(DISTINCT CASE WHEN eq.properties->>'equipment_type' = 'AHU' THEN eq.id END) AS ahu_count,
    COUNT(DISTINCT CASE WHEN eq.properties->>'equipment_type' = 'VAV' THEN eq.id END) AS vav_count,
    COUNT(DISTINCT CASE WHEN eq.properties->>'equipment_type' = 'FCU' THEN eq.id END) AS fcu_count
FROM nodes b
JOIN edges e1 ON e1.src_id = b.id AND e1.rel_type = 'CONTAINS'
JOIN nodes f ON f.id = e1.dst_id AND f.type = 'Floor'
JOIN edges e2 ON e2.src_id = f.id AND e2.rel_type = 'CONTAINS'
JOIN nodes s ON s.id = e2.dst_id AND s.type = 'Space'
-- Équipements dans ou servant l'espace
LEFT JOIN edges loc ON (loc.dst_id = s.id AND loc.rel_type = 'LOCATED_IN')
                    OR (loc.dst_id = s.id AND loc.rel_type = 'SERVES')
LEFT JOIN nodes eq ON eq.id = loc.src_id AND eq.type = 'Equipment'
    AND eq.properties->>'equipment_type' IN ('AHU', 'VAV', 'FCU', 'Thermostat', 'TemperatureSensor')
-- Points de température sur ces équipements
LEFT JOIN edges hp ON hp.src_id = eq.id AND hp.rel_type = 'HAS_POINT'
LEFT JOIN nodes pt ON pt.id = hp.dst_id AND pt.type = 'Point'
    AND pt.properties->>'quantity' = 'temperature'
WHERE b.type = 'Building'
GROUP BY b.name, f.id, f.name, f.properties->>'floor_number'
ORDER BY b.name, (f.properties->>'floor_number')::int NULLS LAST;
