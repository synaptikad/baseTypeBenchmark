-- Q9: Tenant Carbon Footprint
-- Benchmark: Complex aggregation with carbon factor calculation
-- Pattern: Energy → Carbon conversion

WITH tenant_energy AS (
    SELECT DISTINCT
        t.id as tenant_id,
        t.name as tenant_name,
        t.building_id,
        p.id as point_id
    FROM nodes t
    JOIN edges e1 ON e1.src_id = t.id AND e1.rel_type = 'OCCUPIES'
    JOIN nodes sp ON sp.id = e1.dst_id AND sp.type = 'Space'
    JOIN edges e2 ON (e2.src_id = sp.id OR e2.dst_id = sp.id)
    JOIN nodes eq ON (eq.id = e2.dst_id OR eq.id = e2.src_id) AND eq.type = 'Equipment' AND eq.id != sp.id
    JOIN edges e3 ON e3.src_id = eq.id AND e3.rel_type = 'HAS_POINT'
    JOIN nodes p ON p.id = e3.dst_id AND p.type = 'Point'
    JOIN edges e4 ON e4.src_id = p.id AND e4.rel_type = 'MEASURES' AND e4.dst_id = 'Power'
    WHERE t.type = 'Tenant'
),
energy_consumption AS (
    SELECT
        te.tenant_id,
        te.tenant_name,
        te.building_id,
        SUM(ts.value) / 1000.0 as total_kwh  -- Convert W to kWh
    FROM tenant_energy te
    JOIN timeseries ts ON ts.point_id = te.point_id
    WHERE ts.time >= NOW() - INTERVAL '30 days'
    GROUP BY te.tenant_id, te.tenant_name, te.building_id
)
SELECT
    tenant_id,
    tenant_name,
    building_id,
    total_kwh,
    total_kwh * 0.4 as carbon_kg,  -- ~0.4 kg CO2/kWh (grid average)
    total_kwh * 0.4 / 1000.0 as carbon_tonnes
FROM energy_consumption
ORDER BY carbon_kg DESC;
