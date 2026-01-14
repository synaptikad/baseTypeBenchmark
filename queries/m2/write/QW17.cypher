// QW17: Remove Calibration Info
// Supprimer les proprietes de calibration
// Parametres: $point_id
//
// Use case: Nettoyer les informations de calibration (cleanup de QW5)
// Cypher utilise des proprietes prefixees pour les nested objects

MATCH (p:Point {id: $point_id})
REMOVE p.calibration_last_date,
       p.calibration_next_date,
       p.calibration_technician
RETURN p.id AS id, 1 AS calibration_removed;
