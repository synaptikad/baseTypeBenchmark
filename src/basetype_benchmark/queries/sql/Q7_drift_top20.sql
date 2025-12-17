-- Q7: Top 20 capteurs avec dérive (Sensor Drift Detection)
-- Complexité: Analyse statistique sur fenêtre glissante pour détecter les anomalies
-- Domaines: Timeseries, Point, Equipment
-- Use case: Identifier les capteurs dont les valeurs dérivent (maintenance prédictive)

WITH
-- Statistiques de référence (semaine -2 à -1)
baseline_stats AS (
    SELECT
        ts.point_id,
        AVG(ts.value) AS baseline_avg,
        STDDEV(ts.value) AS baseline_stddev,
        COUNT(*) AS baseline_samples
    FROM timeseries ts
    WHERE ts.time >= NOW() - INTERVAL '14 days'
      AND ts.time < NOW() - INTERVAL '7 days'
    GROUP BY ts.point_id
    HAVING COUNT(*) >= 100  -- Minimum de données pour baseline fiable
),

-- Statistiques récentes (dernière semaine)
recent_stats AS (
    SELECT
        ts.point_id,
        AVG(ts.value) AS recent_avg,
        STDDEV(ts.value) AS recent_stddev,
        COUNT(*) AS recent_samples,
        MIN(ts.value) AS recent_min,
        MAX(ts.value) AS recent_max
    FROM timeseries ts
    WHERE ts.time >= NOW() - INTERVAL '7 days'
    GROUP BY ts.point_id
    HAVING COUNT(*) >= 100
),

-- Calcul de la dérive
drift_analysis AS (
    SELECT
        b.point_id,
        b.baseline_avg,
        b.baseline_stddev,
        r.recent_avg,
        r.recent_stddev,
        r.recent_samples,
        -- Dérive de la moyenne (en nombre de stddev baseline)
        CASE
            WHEN b.baseline_stddev > 0
            THEN ABS(r.recent_avg - b.baseline_avg) / b.baseline_stddev
            ELSE 0
        END AS mean_drift_sigma,
        -- Changement de variabilité
        CASE
            WHEN b.baseline_stddev > 0
            THEN r.recent_stddev / b.baseline_stddev
            ELSE 1
        END AS variability_ratio,
        -- Dérive absolue
        ABS(r.recent_avg - b.baseline_avg) AS absolute_drift
    FROM baseline_stats b
    JOIN recent_stats r ON r.point_id = b.point_id
)

-- Top 20 capteurs avec la plus forte dérive
SELECT
    pt.id AS point_id,
    pt.name AS point_name,
    pt.properties->>'quantity' AS quantity,
    eq.name AS equipment_name,
    eq.properties->>'equipment_type' AS equipment_type,
    ROUND(da.baseline_avg::numeric, 2) AS baseline_avg,
    ROUND(da.recent_avg::numeric, 2) AS recent_avg,
    ROUND(da.absolute_drift::numeric, 2) AS absolute_drift,
    ROUND(da.mean_drift_sigma::numeric, 2) AS drift_sigma,
    ROUND(da.variability_ratio::numeric, 2) AS variability_ratio,
    da.recent_samples,
    -- Classification de l'anomalie
    CASE
        WHEN da.mean_drift_sigma > 3 THEN 'CRITICAL'
        WHEN da.mean_drift_sigma > 2 THEN 'WARNING'
        WHEN da.variability_ratio > 2 OR da.variability_ratio < 0.5 THEN 'UNSTABLE'
        ELSE 'NORMAL'
    END AS status
FROM drift_analysis da
JOIN nodes pt ON pt.id = da.point_id AND pt.type = 'Point'
LEFT JOIN edges hp ON hp.dst_id = pt.id AND hp.rel_type = 'HAS_POINT'
LEFT JOIN nodes eq ON eq.id = hp.src_id AND eq.type = 'Equipment'
WHERE da.mean_drift_sigma > 1  -- Au moins 1 sigma de dérive
   OR da.variability_ratio > 1.5
   OR da.variability_ratio < 0.67
ORDER BY da.mean_drift_sigma DESC, da.absolute_drift DESC
LIMIT 20;
