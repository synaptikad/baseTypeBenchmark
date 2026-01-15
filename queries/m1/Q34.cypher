// Q34: Materialized Energy Summary
// Status: DEGRADED pour M1 (pas de vues materialisees)
// Semantic: Compute daily energy aggregates (calculated on-the-fly, not pre-materialized)
// Parametres: $building_id, $date_start, $date_end
// Note: Calcul applicatif via UNWIND TimeseriesChunk - moins efficace qu'une vue matérialisée

// Trouver tous les points d'énergie du bâtiment
MATCH (p:Point {building_id: $building_id})
WHERE p.quantity = 'energy'

// Récupérer les chunks timeseries dans la plage de dates
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les valeurs avec leurs timestamps
UNWIND range(0, size(chunk.timestamps) - 1) AS idx
WITH p, chunk.timestamps[idx] AS timestamp, chunk.values[idx] AS value

// Filtrer par plage de temps exacte
WHERE timestamp >= $date_start AND timestamp <= $date_end

// Extraire le jour (format: "2024-01-15T08:00:00Z" -> "2024-01-15")
WITH p, substring(timestamp, 0, 10) AS day, value

// Agréger par jour
WITH day,
     SUM(value) AS total_energy_kwh,
     MAX(value) AS peak_power_kw,
     COUNT(DISTINCT p.id) AS meter_count

RETURN
    $building_id AS building_id,
    day,
    total_energy_kwh,
    peak_power_kw,
    meter_count
ORDER BY day;
