// Q9: Empreinte carbone par locataire (Tenant Carbon Footprint)
// COMPLEXITÉ MAXIMALE: Cross-domain query traversant 6 domaines
// Domaines croisés: Organization, Spatial, Equipment, Energy, Contractual, Timeseries
// Use case: Calculer l'empreinte carbone de chaque locataire sur 6 mois

// Note: Cette requête démontre la force native de Cypher pour les traversées
// mais aussi sa limite pour les agrégations temporelles (pas de support natif timeseries)

// 1. Trouver les tenants et leurs espaces occupés
MATCH (tenant:Node {type: 'Tenant'})-[:OCCUPIES]->(space:Node {type: 'Space'})

// 2. Équipements dans ces espaces
OPTIONAL MATCH (equip:Node {type: 'Equipment'})-[:LOCATED_IN]->(space)

// 3. Traversée de l'arbre de compteurs (FEEDS) - jusqu'à 8 niveaux
OPTIONAL MATCH path = (meter:Node {type: 'Meter'})-[:FEEDS*1..8]->(equip)

// 4. Points de mesure power sur les compteurs
OPTIONAL MATCH (meter)-[:HAS_POINT]->(point:Node {type: 'Point'})
WHERE point.properties.quantity = 'power'

// 5. Contrats et fournisseurs pour facteur carbone
OPTIONAL MATCH (tenant)-[:COVERED_BY]->(contract:Node {type: 'Contract'})-[:PROVIDED_BY]->(provider:Node {type: 'Provider'})

WITH tenant,
     COLLECT(DISTINCT space.id) AS spaces,
     COLLECT(DISTINCT equip.id) AS equipments,
     COLLECT(DISTINCT meter.id) AS meters,
     COLLECT(DISTINCT point.id) AS power_points,
     COLLECT(DISTINCT provider.name) AS providers,
     SUM(COALESCE(toFloat(space.properties.area_sqm), 0)) AS total_area_sqm

// Agrégation finale
RETURN tenant.name AS tenant_name,
       SIZE(spaces) AS spaces_count,
       SIZE(equipments) AS equipments_count,
       SIZE(meters) AS meters_count,
       SIZE(power_points) AS power_points_count,
       total_area_sqm,
       providers[0] AS main_provider,
       // Note: L'agrégation timeseries nécessite un appel externe ou une extension
       // Le graph in-memory n'a pas de support natif pour les séries temporelles
       'REQUIRES_EXTERNAL_TS_QUERY' AS energy_kwh_note
ORDER BY spaces_count DESC
LIMIT 20;
