// Q12: Full Building Analytics Dashboard
// Building-level KPIs aggregation

MATCH (n:Node)
WITH n.building_id AS building_id, n.type AS type, count(*) AS cnt
WITH building_id,
     sum(CASE WHEN type = 'Floor' THEN cnt ELSE 0 END) AS floor_count,
     sum(CASE WHEN type = 'Space' THEN cnt ELSE 0 END) AS space_count,
     sum(CASE WHEN type = 'Equipment' THEN cnt ELSE 0 END) AS equipment_count,
     sum(CASE WHEN type = 'Point' THEN cnt ELSE 0 END) AS point_count,
     sum(CASE WHEN type = 'Tenant' THEN cnt ELSE 0 END) AS tenant_count,
     sum(cnt) AS total_nodes
RETURN building_id,
       floor_count,
       space_count,
       equipment_count,
       point_count,
       tenant_count,
       total_nodes
ORDER BY building_id;
