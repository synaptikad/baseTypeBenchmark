// Q8: Tenant Energy
// Paramètres: $tenant_id, $date_start, $date_end
// Intention: Calculer la consommation énergétique totale d'un locataire
// Status: DEGRADED pour M1 - utilise TimeseriesChunk avec UNWIND
// Note: Démontre la limitation des graphes pour l'agrégation timeseries

// Traverse depuis Tenant <- METERS_TENANT <- Equipment (submeter) -> HAS_POINT -> Point -> HAS_CHUNK -> Chunk
MATCH (t:Tenant {id: $tenant_id})<-[:METERS_TENANT]-(m:Equipment)-[:HAS_POINT]->(p:Point)
WHERE p.quantity = 'energy'

// Récupérer les chunks timeseries dans la plage de dates
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les valeurs depuis les arrays stockés dans les chunks
UNWIND chunk.values AS value

WITH t.id AS tenant_id,
     count(DISTINCT m) AS meter_count,
     count(DISTINCT p) AS point_count,
     sum(value) AS total_energy

RETURN
    tenant_id,
    total_energy AS total_energy_kwh,
    meter_count,
    point_count;
