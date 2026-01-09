// Q13: Office Hours Comfort
// Paramètres: $building_id, $date_start, $date_end
// Intention: Analyser le confort (température, CO2) dans les bureaux pendant les heures de travail (8h-18h)
//
// Modèle M1: Traverse Building -> Spaces (offices) -> Equipment -> Points -> Chunks
// Filtre sur heures de bureau puis agrège

MATCH (b:Building {id: $building_id})<-[:LOCATED_IN*1..3]-(s:Space)
WHERE s.type STARTS WITH 'office'

MATCH (s)<-[:SERVES]-(eq:Equipment)-[:HAS_POINT]->(p:Point)
WHERE p.quantity IN ['temperature', 'co2']

// Récupérer les chunks timeseries dans la plage de dates
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les timestamps et valeurs ensemble
UNWIND range(0, size(chunk.timestamps) - 1) AS idx
WITH s, p.quantity AS qty, chunk.timestamps[idx] AS ts, chunk.values[idx] AS val

// Filtrer heures de bureau (8h-18h) - format timestamp: "2024-01-15T08:00:00Z"
WHERE toInteger(substring(ts, 11, 2)) >= 8 AND toInteger(substring(ts, 11, 2)) < 18

// Grouper par espace et quantity
WITH s.id AS space_id, s.name AS space_name, qty, collect(val) AS values

// Calculer les moyennes par quantity
WITH space_id, space_name,
     CASE WHEN qty = 'temperature' THEN reduce(s = 0.0, v IN values | s + v) / size(values) ELSE null END AS temp,
     CASE WHEN qty = 'co2' THEN reduce(s = 0.0, v IN values | s + v) / size(values) ELSE null END AS co2

RETURN
    space_id,
    space_name,
    avg(temp) AS avg_temp_c,
    avg(co2) AS avg_co2_ppm
ORDER BY space_id;
