// QW5: Deep Calibration Update
// Équivalent M1 - Mise à jour propriétés calibration
// Paramètres: $point_id, $calibration_date, $next_date, $technician
//
// Note: Cypher n'a pas de nested objects, on utilise des propriétés préfixées

MATCH (p:Point {id: $point_id})
SET p.calibration_last_date = $calibration_date,
    p.calibration_next_date = $next_date,
    p.calibration_technician = $technician
RETURN p.id AS id,
       {last_date: p.calibration_last_date,
        next_date: p.calibration_next_date,
        technician: p.calibration_technician} AS updated_calibration;
