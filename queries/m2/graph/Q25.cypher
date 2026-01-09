// Q25: Equipment Audit Trail
// Équivalent M1 - Vue 360° équipement
// Paramètres: $equipment_id

MATCH (eq:Equipment {id: $equipment_id})
OPTIONAL MATCH (eq)-[:HAS_POINT]->(p:Point)
WHERE p.calibration_next_date IS NOT NULL
WITH eq,
     collect({
         point_id: p.id,
         last_calibration: p.calibration_last_date,
         next_calibration: p.calibration_next_date,
         is_overdue: p.calibration_next_date < date()
     }) AS points_calibration
RETURN eq.id AS equipment_id,
       eq.name AS name,
       eq.equipment_type AS equipment_type,
       eq.firmware_version AS current_firmware,
       eq.firmware_update_date AS last_firmware_update,
       size(coalesce(eq.maintenance_history, [])) AS maintenance_events,
       CASE WHEN size(coalesce(eq.maintenance_history, [])) > 0
            THEN eq.maintenance_history[-1].date
            ELSE null END AS last_maintenance_date,
       points_calibration AS points_calibration_status,
       CASE
           WHEN eq.maintenance_priority = 'critical' THEN 'CRITICAL'
           WHEN size(coalesce(eq.maintenance_history, [])) > 5 THEN 'HIGH_MAINTENANCE'
           ELSE 'NORMAL'
       END AS health_status;
