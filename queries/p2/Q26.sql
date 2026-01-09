-- Q26: Capability Evolution Report
-- Status: NATIVE pour P2 (validation post-QW7)
-- Paramètres: domain (ex: 'HVAC')
-- Démontre: Agrégation sur arrays JSONB avec statistiques

WITH equipment_caps AS (
    SELECT
        eq.data->>'equipment_type' AS equipment_type,
        eq.id,
        jsonb_array_length(COALESCE(eq.data->'capabilities', '[]'::jsonb)) AS cap_count,
        eq.data->'capabilities' AS capabilities
    FROM p2.nodes eq
    WHERE eq.node_type = 'Equipment'
      AND eq.data->>'domain' = %(domain)s
),
cap_distribution AS (
    SELECT
        equipment_type,
        cap,
        COUNT(*) AS cap_occurrences
    FROM equipment_caps,
         jsonb_array_elements_text(capabilities) AS cap
    GROUP BY equipment_type, cap
),
cap_stats AS (
    SELECT
        equipment_type,
        jsonb_object_agg(cap, cap_occurrences) AS distribution,
        (SELECT cap FROM cap_distribution cd2
         WHERE cd2.equipment_type = cd.equipment_type
         ORDER BY cap_occurrences DESC LIMIT 1) AS most_common
    FROM cap_distribution cd
    GROUP BY equipment_type
)
SELECT
    ec.equipment_type,
    COUNT(DISTINCT ec.id) AS equipment_count,
    cs.distribution AS capabilities_distribution,
    cs.most_common AS most_common_capability,
    ROUND(AVG(ec.cap_count), 2) AS avg_capabilities
FROM equipment_caps ec
LEFT JOIN cap_stats cs ON cs.equipment_type = ec.equipment_type
GROUP BY ec.equipment_type, cs.distribution, cs.most_common
ORDER BY equipment_count DESC;
