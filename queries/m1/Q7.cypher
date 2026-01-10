// Q7: Drift Top-20
// Paramètres: $building_id, $date_start, $date_end
// Intention: Top 20 des points température avec plus grande variance (drift)
// Status: DEGRADED pour M1 - pas de TimescaleDB, utilise TimeseriesChunk avec UNWIND
// Note: Démontre la limitation des graphes pour l'agrégation timeseries

// Trouver tous les points température du bâtiment (via propriété dénormalisée)
MATCH (p:Point {building_id: $building_id})
WHERE p.quantity = 'temperature'

// Récupérer les chunks timeseries dans la plage de dates
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les valeurs depuis les arrays stockés dans les chunks
// C'est ici que M1 montre sa limitation: chaque valeur doit être extraite
UNWIND chunk.values AS value

// Agrégation par point: moyenne, somme carrés, count
WITH p.id AS point_id,
     p.name AS point_name,
     avg(value) AS mean_value,
     sum(value * value) AS sum_sq,
     sum(value) AS sum_val,
     count(value) AS sample_count

// Variance = E[X²] - E[X]² = sum_sq/n - (sum_val/n)²
// Note: stDev() non supporté par Memgraph, calcul manuel
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
