// Q7: Drift Top-20
// Paramètres: $building_id, $date_start, $date_end
// Intention: Top 20 des points température avec plus grande variance (drift)

// Trouver tous les points température du bâtiment
MATCH (b:Building {id: $building_id})<-[:LOCATED_IN*1..4]-(eq:Equipment)-[:HAS_POINT]->(p:Point)
WHERE p.quantity = 'temperature'

// Récupérer les chunks timeseries
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les valeurs
UNWIND chunk.values AS value

// Calculer variance par point (approximation via stdev)
WITH p.id AS point_id,
     p.name AS point_name,
     collect(value) AS values

WITH point_id, point_name,
     avg(values) AS mean_value,
     stDev(values) AS drift

// Top 20 par variance
RETURN
    point_id,
    point_name,
    mean_value,
    drift,
    size(values) AS sample_count
ORDER BY drift DESC
LIMIT 20;
