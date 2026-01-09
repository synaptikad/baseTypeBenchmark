// Q24: Maintenance History
// Équivalent M1 - Lecture historique maintenance
// Paramètres: $equipment_id

MATCH (eq:Equipment {id: $equipment_id})
WITH eq,
     coalesce(eq.maintenance_history, []) AS history
RETURN eq.id AS equipment_id,
       eq.name AS name,
       size(history) AS event_count,
       CASE WHEN size(history) > 0 THEN history[-1] ELSE null END AS last_event,
       CASE WHEN size(history) > 0 THEN history[-1].date ELSE null END AS last_event_date,
       CASE WHEN size(history) > 0 THEN history[-1].technician ELSE null END AS last_technician,
       reduce(total = 0.0, evt IN history | total + coalesce(evt.cost_eur, 0.0)) AS total_maintenance_cost;
