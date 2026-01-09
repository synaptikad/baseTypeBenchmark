// Q7: Drift Top-20
// Paramètres: $building_id, $date_start, $date_end
// Intention: Top 20 des points température avec plus grande variance (drift)
// Memgraph: stDev non supporté, calcul manuel de variance

// Trouver tous les points température du bâtiment
MATCH (b:Building {id: $building_id})<-[:LOCATED_IN*1..4]-(eq:Equipment)-[:HAS_POINT]->(p:Point)
WHERE p.quantity = 'temperature'

// Récupérer les chunks timeseries
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les valeurs et calculer stats
UNWIND chunk.values AS value

// Agrégation par point: moyenne, somme carrés, count
WITH p.id AS point_id,
     p.name AS point_name,
     avg(value) AS mean_value,
     sum(value * value) AS sum_sq,
     sum(value) AS sum_val,
     count(value) AS sample_count

// Variance = E[X²] - E[X]² = sum_sq/n - (sum_val/n)²
WITH point_id, point_name, mean_value, sample_count,
     CASE WHEN sample_count > 1
          THEN sqrt((sum_sq / sample_count) - (mean_value * mean_value))
          ELSE 0.0
     END AS drift

// Top 20 par variance (drift)
RETURN
    point_id,
    point_name,
    mean_value,
    drift,
    sample_count
ORDER BY drift DESC
LIMIT 20;
