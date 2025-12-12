-- Profil relationnel strict : requêtes Q1..Q8 alignées sur docs/queries.md

-- Q1 Chaîne énergétique profondeur ≤10
WITH RECURSIVE energy_chain AS (
    SELECT e.src_id AS meter_id, e.dst_id AS equipment_id, 1 AS depth
    FROM edges e
    WHERE e.rel_type = 'FEEDS' AND e.src_id = :'root_meter'
    UNION ALL
    SELECT c.meter_id, e.dst_id, c.depth + 1
    FROM energy_chain c
    JOIN edges e ON e.src_id = c.equipment_id AND e.rel_type = 'FEEDS'
    WHERE c.depth < 10
)
SELECT c.depth, c.equipment_id, n.name, n.type
FROM energy_chain c
JOIN nodes n ON n.id = c.equipment_id
ORDER BY c.depth, c.equipment_id;

-- Q2 Impact AHU -> zones -> espaces -> points (profondeur ≤8)
WITH RECURSIVE functional AS (
    SELECT e.dst_id AS equipment_id, 1 AS depth
    FROM edges e
    WHERE e.rel_type = 'HAS_PART' AND e.src_id = :'ahu_id'
    UNION ALL
    SELECT e.dst_id, f.depth + 1
    FROM functional f
    JOIN edges e ON e.src_id = f.equipment_id AND e.rel_type = 'HAS_PART'
    WHERE f.depth < 8
), served_spaces AS (
    SELECT DISTINCT f.equipment_id, s.dst_id AS space_id
    FROM functional f
    JOIN edges s ON s.src_id = f.equipment_id AND s.rel_type = 'SERVES'
), points AS (
    SELECT p.src_id AS equipment_id, p.dst_id AS point_id
    FROM edges p
    WHERE p.rel_type = 'HAS_POINT'
)
SELECT DISTINCT f.depth, f.equipment_id, ss.space_id, pt.point_id
FROM functional f
LEFT JOIN served_spaces ss ON ss.equipment_id = f.equipment_id
LEFT JOIN points pt ON pt.equipment_id = f.equipment_id
ORDER BY f.depth, f.equipment_id;

-- Q3 Équipements qui servent un espace donné
SELECT e.src_id AS equipment_id, n.name
FROM edges e
JOIN nodes n ON n.id = e.src_id
WHERE e.rel_type = 'SERVES' AND e.dst_id = :'space_id'
ORDER BY equipment_id;

-- Q4 Inventaire des points et quantités par étage
WITH RECURSIVE floor_spaces AS (
    SELECT e.dst_id AS space_id
    FROM edges e
    WHERE e.rel_type = 'CONTAINS' AND e.src_id = :'floor_id'
), equipments AS (
    SELECT l.src_id AS equipment_id, l.dst_id AS space_id
    FROM edges l
    WHERE l.rel_type = 'LOCATED_IN' AND l.dst_id IN (SELECT space_id FROM floor_spaces)
), points AS (
    SELECT p.src_id AS equipment_id, p.dst_id AS point_id
    FROM edges p
    JOIN equipments e ON e.equipment_id = p.src_id
    WHERE p.rel_type = 'HAS_POINT'
), quantities AS (
    SELECT pt.point_id, m.dst_id AS quantity
    FROM points pt
    JOIN edges m ON m.src_id = pt.point_id AND m.rel_type = 'MEASURES'
)
SELECT q.quantity, COUNT(*) AS point_count
FROM quantities q
GROUP BY q.quantity
ORDER BY q.quantity;

-- Q5 Détection des orphelins
SELECT n.id, n.type, n.name
FROM nodes n
LEFT JOIN edges e_out ON e_out.src_id = n.id
LEFT JOIN edges e_in ON e_in.dst_id = n.id
WHERE e_out.src_id IS NULL AND e_in.dst_id IS NULL
ORDER BY n.id;

-- Q6 Séries temporelles avec agrégation horaire
SELECT point_id, date_trunc('hour', time) AS heure, AVG(value) AS moyenne
FROM timeseries
WHERE quantity = 'temperature'
GROUP BY point_id, heure
ORDER BY heure, point_id;

-- Q7 Détection de dérive (top 20)
WITH latest AS (
    SELECT point_id, value AS last_value
    FROM (
        SELECT point_id, value, ROW_NUMBER() OVER (PARTITION BY point_id ORDER BY time DESC) AS rn
        FROM timeseries
    ) sub
    WHERE rn = 1
), baseline AS (
    SELECT point_id, AVG(value) AS avg_24h
    FROM timeseries
    WHERE time >= NOW() - INTERVAL '24 hours'
    GROUP BY point_id
)
SELECT l.point_id, l.last_value, b.avg_24h, ABS(l.last_value - b.avg_24h) AS derive
FROM latest l
JOIN baseline b ON b.point_id = l.point_id
ORDER BY derive DESC NULLS LAST
LIMIT 20;

-- Q8 Parcours mixte tenant -> served -> timeseries
WITH tenant_spaces AS (
    SELECT dst_id AS space_id
    FROM edges
    WHERE rel_type = 'OCCUPIES' AND src_id = :'tenant_id'
), serving AS (
    SELECT src_id AS equipment_id, dst_id AS space_id
    FROM edges
    WHERE rel_type = 'SERVES'
), points AS (
    SELECT p.src_id AS equipment_id, p.dst_id AS point_id
    FROM edges p
    WHERE p.rel_type = 'HAS_POINT'
)
SELECT ts.point_id, date_trunc('hour', ts.time) AS heure, AVG(ts.value) AS moyenne
FROM timeseries ts
JOIN points pt ON pt.point_id = ts.point_id
JOIN serving s ON s.equipment_id = pt.equipment_id
JOIN tenant_spaces t ON t.space_id = s.space_id
GROUP BY ts.point_id, heure
ORDER BY heure, ts.point_id;
