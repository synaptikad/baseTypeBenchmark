-- Q24: Maintenance History Query
-- Status: NATIVE pour P2 (validation post-QW4)
-- Paramètres: equipment_id
-- Démontre: Lecture d'array JSONB avec agrégation

SELECT
    eq.id AS equipment_id,
    eq.name,
    jsonb_array_length(COALESCE(eq.data->'maintenance_history', '[]'::jsonb)) AS event_count,
    eq.data->'maintenance_history'->-1 AS last_event,
    (eq.data->'maintenance_history'->-1)->>'date' AS last_event_date,
    (eq.data->'maintenance_history'->-1)->>'technician' AS last_technician,
    (eq.data->'maintenance_history'->-1)->>'type' AS last_event_type,
    -- Calcul du coût total maintenance
    (
        SELECT COALESCE(SUM((evt->>'cost_eur')::numeric), 0)
        FROM jsonb_array_elements(eq.data->'maintenance_history') AS evt
    ) AS total_maintenance_cost,
    -- Liste des pièces remplacées (toutes interventions)
    (
        SELECT jsonb_agg(DISTINCT part)
        FROM jsonb_array_elements(eq.data->'maintenance_history') AS evt,
             jsonb_array_elements_text(evt->'parts_replaced') AS part
    ) AS all_parts_replaced
FROM p2.nodes eq
WHERE eq.id = %(equipment_id)s
  AND eq.node_type = 'Equipment';
