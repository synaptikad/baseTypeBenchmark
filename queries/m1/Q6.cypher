// Q6: Hourly Aggregation
// Paramètres: $point_id, $date_start, $date_end
// Intention: Agrégation horaire des valeurs pour un point donné
//
// Modèle M1: Utilise TimeseriesChunk nodes avec arrays de timestamps/values
// Déroule (UNWIND) les arrays et agrège par heure

MATCH (p:Point {id: $point_id})-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les arrays de timestamps et values
UNWIND range(0, size(chunk.timestamps) - 1) AS idx
WITH chunk.timestamps[idx] AS timestamp,
     chunk.values[idx] AS value

// Extraire l'heure (format: "2024-01-15T08:00:00Z" -> "2024-01-15 08")
WITH substring(timestamp, 0, 13) AS hour,
     value

// Filtrer par plage de temps
WHERE timestamp >= $date_start AND timestamp <= $date_end

// Agréger par heure
RETURN
    hour + ':00:00' AS time_bucket,
    avg(value) AS avg_value,
    min(value) AS min_value,
    max(value) AS max_value,
    count(value) AS sample_count
ORDER BY time_bucket;
