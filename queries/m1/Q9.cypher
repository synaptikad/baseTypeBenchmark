// Q9: Tenant Carbon Footprint
// Paramètres: $tenant_id, $date_start, $date_end, $co2_factor
// Intention: Calculer l'empreinte carbone d'un locataire (énergie × facteur CO2)
// Status: DEGRADED pour M1 - utilise TimeseriesChunk avec UNWIND
// Note: Extension de Q8 avec multiplication par facteur CO2

MATCH (t:Tenant {id: $tenant_id})<-[:METERS_TENANT]-(m:Equipment)-[:HAS_POINT]->(p:Point)
WHERE p.quantity = 'energy'

// Récupérer les chunks timeseries dans la plage de dates
MATCH (p)-[:HAS_CHUNK]->(chunk:TimeseriesChunk)
WHERE chunk.date >= substring($date_start, 0, 10)
  AND chunk.date <= substring($date_end, 0, 10)

// Dérouler les valeurs depuis les arrays stockés dans les chunks
UNWIND chunk.values AS value

WITH t.id AS tenant_id, sum(value) AS total_energy

RETURN
    tenant_id,
    total_energy AS total_energy_kwh,
    total_energy * $co2_factor AS carbon_kg_co2;
