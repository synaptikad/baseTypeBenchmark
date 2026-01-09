// Q8: Tenant Energy
// Paramètres: $tenant_id, $date_start, $date_end
// Intention: Calculer la consommation énergétique totale d'un locataire
//
// Modèle M1: Utilise TimeseriesChunk nodes avec arrays de timestamps/values
// Traverse depuis Tenant -> Meters -> Points -> Chunks, puis agrège

MATCH (t:Tenant {id: $tenant_id})<-[:METERS_TENANT]-(m:Meter)-[:HAS_POINT]->(p:Point)
WHERE p.quantity = 'energy'

// Récupérer les chunks timeseries dans la plage de dates
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les valeurs et sommer
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
