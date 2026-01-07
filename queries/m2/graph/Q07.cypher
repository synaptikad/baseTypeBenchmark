// Q7: Drift Top-20 - Extraction point_ids
// Parametre: $building_id
// Output: Liste de point_ids pour la query timeseries

MATCH (p:Point {building_id: $building_id})
RETURN collect(p.id) AS point_ids;
