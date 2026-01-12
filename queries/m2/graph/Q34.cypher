// Q34: Materialized Energy Summary
// Status: DEGRADED pour M2 (via TimescaleDB continuous aggregates)
// Semantic: Read from pre-computed materialized view
// Note: M2 peut utiliser les continuous aggregates de TimescaleDB
// Cette query retourne simplement le building_id pour orchestration

MATCH (b:Building {id: $building_id})
RETURN b.id AS building_id;

// Note: La lecture de la vue materialisee se fait via TimescaleDB
// dans m2/Q34.sql
