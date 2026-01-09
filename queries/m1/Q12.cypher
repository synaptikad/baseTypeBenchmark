// Q12: Full Building Analytics
// Paramètres: $building_id, $date_start, $date_end
// Intention: Agrégation multi-domaine pour un bâtiment (énergie, température, occupation)
//
// Modèle M1: Traverse Building -> Equipment -> Points -> Chunks
// Agrège par quantity type

MATCH (b:Building {id: $building_id})<-[:LOCATED_IN*1..4]-(eq:Equipment)-[:HAS_POINT]->(p:Point)
WHERE p.quantity IN ['energy', 'temperature', 'occupancy']

// Récupérer les chunks timeseries dans la plage de dates
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les valeurs
UNWIND chunk.values AS value

// Grouper par quantity et agréger
WITH b.id AS building_id, p.quantity AS quantity, collect(value) AS values

// Calculer les agrégats par type
WITH building_id,
     CASE WHEN quantity = 'energy' THEN reduce(s = 0.0, v IN values | s + v) ELSE 0 END AS energy,
     CASE WHEN quantity = 'temperature' THEN reduce(s = 0.0, v IN values | s + v) / size(values) ELSE 0 END AS temp,
     CASE WHEN quantity = 'occupancy' THEN reduce(s = 0.0, v IN values | s + v) ELSE 0 END AS occupancy

RETURN
    building_id,
    sum(energy) AS total_energy_kwh,
    avg(CASE WHEN temp > 0 THEN temp ELSE null END) AS avg_temperature_c,
    sum(occupancy) AS total_occupancy;
