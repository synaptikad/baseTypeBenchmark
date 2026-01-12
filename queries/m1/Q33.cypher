// Q33: Latest Value per Space
// Status: IMPOSSIBLE pour M1 (pas de LATERAL, pas de TimescaleDB)
// Semantic: Get latest value for each point per space
// Parametres: $building_id
// Note: M1 ne peut pas faire de subquery correlee efficace sans TS

// IMPOSSIBLE - Retourne message d'erreur
RETURN
    'IMPOSSIBLE' AS space_id,
    'M1 does not support LATERAL JOIN or TimescaleDB' AS space_name,
    'N/A' AS point_id,
    'N/A' AS quantity,
    0.0 AS last_value,
    datetime() AS last_time;
