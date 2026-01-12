// Q30: Failure Impact Analysis
// Status: NATIVE pour M1/M2 (traversal pattern naturel)
// Semantic: Si cet équipement tombe en panne, quels espaces/équipements sont impactés?
// Parametres: $equipment_id

// Trouver tous les équipements impactés via FEEDS
MATCH (source:Equipment {id: $equipment_id})
OPTIONAL MATCH path = (source)-[:FEEDS*1..10]->(impacted:Equipment)
WITH source, impacted, length(path) AS hop_distance
WHERE impacted IS NOT NULL

// Collecter les équipements impactés
WITH collect({
    impact_type: 'equipment',
    impacted_id: impacted.id,
    impacted_name: impacted.name,
    impacted_subtype: impacted.equipment_type,
    hop_distance: hop_distance,
    served_by_equipment: null
}) AS equipment_impacts

// Trouver les espaces impactés (via équipements dans la chaîne FEEDS)
MATCH (source:Equipment {id: $equipment_id})
OPTIONAL MATCH path = (source)-[:FEEDS*0..10]->(eq:Equipment)-[:SERVES|MONITORS|LOCATED_IN]->(space:Space)
WITH equipment_impacts, eq, space,
     CASE WHEN path IS NOT NULL
          THEN size(nodes(path)) - 2
          ELSE 0 END AS hop_distance
WHERE space IS NOT NULL

WITH equipment_impacts, collect(DISTINCT {
    impact_type: 'space',
    impacted_id: space.id,
    impacted_name: space.name,
    impacted_subtype: 'Space',
    hop_distance: hop_distance,
    served_by_equipment: eq.name
}) AS space_impacts

// Combiner et retourner
UNWIND (equipment_impacts + space_impacts) AS impact
RETURN
    impact.impact_type AS impact_type,
    impact.impacted_id AS impacted_id,
    impact.impacted_name AS impacted_name,
    impact.impacted_subtype AS impacted_subtype,
    impact.hop_distance AS hop_distance,
    impact.served_by_equipment AS served_by_equipment
ORDER BY impact.hop_distance, impact.impact_type, impact.impacted_id;
