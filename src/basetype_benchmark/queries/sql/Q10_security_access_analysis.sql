-- Q10: Analyse d'accès sécurité cross-domain (Security Access Analysis)
-- COMPLEXITÉ MAXIMALE: Croisement Sécurité × Organisation × Spatial × Timeseries
-- Domaines croisés: Security, Organization, Spatial, Timeseries (événements)
-- Use case: Pour chaque zone de sécurité, analyser les accès par département
-- sur les 30 derniers jours et identifier les anomalies (accès hors heures)

WITH
-- 1. Hiérarchie organisationnelle complète
org_hierarchy AS (
    SELECT
        p.id AS person_id,
        p.name AS person_name,
        p.properties->>'role' AS role,
        t.id AS team_id,
        t.name AS team_name,
        d.id AS dept_id,
        d.name AS dept_name
    FROM nodes p
    JOIN edges bt ON bt.src_id = p.id AND bt.rel_type = 'BELONGS_TO'
    JOIN nodes t ON t.id = bt.dst_id AND t.type = 'Team'
    JOIN edges bt2 ON bt2.src_id = t.id AND bt2.rel_type = 'BELONGS_TO'
    JOIN nodes d ON d.id = bt2.dst_id AND d.type = 'Department'
    WHERE p.type = 'Person'
),

-- 2. Zones de sécurité et leurs points d'accès
security_topology AS (
    SELECT
        sz.id AS zone_id,
        sz.name AS zone_name,
        sz.properties->>'security_level' AS security_level,
        ap.id AS access_point_id,
        ap.name AS access_point_name,
        s.id AS space_id,
        s.name AS space_name
    FROM nodes sz
    JOIN edges contains ON contains.src_id = sz.id AND contains.rel_type = 'CONTAINS'
    JOIN nodes ap ON ap.id = contains.dst_id AND ap.type = 'AccessPoint'
    JOIN edges loc ON loc.src_id = ap.id AND loc.rel_type = 'LOCATED_IN'
    JOIN nodes s ON s.id = loc.dst_id AND s.type = 'Space'
    WHERE sz.type = 'SecurityZone'
),

-- 3. Points de mesure des accès
access_points_measures AS (
    SELECT
        st.zone_id,
        st.zone_name,
        st.security_level,
        st.access_point_id,
        st.space_name,
        pt.id AS point_id
    FROM security_topology st
    JOIN edges hp ON hp.src_id = st.access_point_id AND hp.rel_type = 'HAS_POINT'
    JOIN nodes pt ON pt.id = hp.dst_id AND pt.type = 'Point'
    WHERE pt.properties->>'quantity' = 'access_event'
),

-- 4. Personnes travaillant dans ces espaces (droits d'accès implicites)
workspace_persons AS (
    SELECT DISTINCT
        st.zone_id,
        st.space_id,
        oh.person_id,
        oh.dept_name
    FROM security_topology st
    JOIN edges wi ON wi.dst_id = st.space_id AND wi.rel_type = 'WORKS_IN'
    JOIN org_hierarchy oh ON oh.person_id = wi.src_id
),

-- 5. Analyse temporelle des accès (30 derniers jours)
access_events AS (
    SELECT
        apm.zone_id,
        apm.zone_name,
        apm.security_level,
        apm.space_name,
        ts.time AS access_time,
        EXTRACT(HOUR FROM ts.time) AS access_hour,
        EXTRACT(DOW FROM ts.time) AS access_dow,
        ts.value AS event_value,
        -- Détection accès hors heures (avant 7h ou après 20h, ou weekend)
        CASE
            WHEN EXTRACT(DOW FROM ts.time) IN (0, 6) THEN true
            WHEN EXTRACT(HOUR FROM ts.time) < 7 OR EXTRACT(HOUR FROM ts.time) > 20 THEN true
            ELSE false
        END AS is_off_hours
    FROM access_points_measures apm
    JOIN timeseries ts ON ts.point_id = apm.point_id
    WHERE ts.time >= NOW() - INTERVAL '30 days'
)

-- Résultat: analyse par zone de sécurité
SELECT
    ae.zone_name,
    ae.security_level,
    COUNT(*) AS total_access_events,
    COUNT(*) FILTER (WHERE ae.is_off_hours) AS off_hours_events,
    ROUND(100.0 * COUNT(*) FILTER (WHERE ae.is_off_hours) / NULLIF(COUNT(*), 0), 2) AS off_hours_pct,
    COUNT(DISTINCT ae.space_name) AS unique_spaces,
    COUNT(DISTINCT wp.dept_name) AS departments_with_access,
    -- Distribution horaire (peak hours)
    MODE() WITHIN GROUP (ORDER BY ae.access_hour) AS peak_hour
FROM access_events ae
LEFT JOIN workspace_persons wp ON wp.zone_id = ae.zone_id
GROUP BY ae.zone_name, ae.security_level
ORDER BY off_hours_pct DESC, total_access_events DESC;
