// Q19: Equipment Digital Twin
// Status: DEGRADED pour M1/M2
// Note: Construction JSON manuelle, pas de stats live sans TimescaleDB
// Paramètre: $equipment_id

MATCH (eq:Equipment {id: $equipment_id})
OPTIONAL MATCH (eq)-[:HAS_POINT]->(p:Point)
WITH eq, collect({
    id: p.id,
    name: p.name,
    quantity: p.quantity,
    unit: p.unit
}) AS points
RETURN {
    id: eq.id,
    name: eq.name,
    type: eq.equipment_type,
    domain: eq.domain,
    capabilities: eq.capabilities,
    tags: eq.tags,
    points: points
} AS digital_twin;

// Note: metadata, protocol, stats live non disponibles
