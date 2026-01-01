# BaseType Benchmark - Query Specification

## Overview

This document formalizes the 13 benchmark queries in natural language, their expected behavior, and validation criteria.

## Query Catalog

### Q1: Energy Chain Traversal
**Natural Language:** Starting from a meter, find all equipment/devices that are fed by this meter through the FEEDS relationship chain (up to 10 hops).

**Parameters:**
- `$METER_ID` - Starting meter ID (e.g., `meter_main_1`)

**Expected Result:** List of nodes (id, type, name, depth) reachable from the meter via FEEDS relationships.

**Pattern:** Graph traversal (variable length path)

**Current Status:** ❌ MISMATCH
- P1/P2: 1904 rows
- M1/M2: 3806 rows  
- O1/O2: 827 rows

**Analysis Needed:** Different traversal semantics? Different relationship mappings?

---

### Q2: Functional Impact Analysis
**Natural Language:** If equipment X fails, what spaces would be affected? Find all spaces that depend on this equipment through SERVES relationships.

**Parameters:**
- `$EQUIPMENT_ID` - Equipment to analyze

**Expected Result:** List of affected spaces with their types.

**Pattern:** Reverse traversal (impact analysis)

**Current Status:** ✅ MATCH (2 rows all engines)

---

### Q3: Space Services
**Natural Language:** What equipment serves a given space? Find all equipment connected to this space via SERVES relationship.

**Parameters:**
- `$SPACE_ID` - Space to query

**Expected Result:** List of serving equipment with their types.

**Pattern:** Direct relationship lookup

**Current Status:** ❌ MISMATCH
- P1/P2/M1/M2: 21 rows
- O1/O2: 17 rows

**Analysis Needed:** Missing relationships in RDF export? Different edge mapping?

---

### Q4: Floor Temperature Points Inventory
**Natural Language:** List all temperature sensor points on a specific floor.

**Parameters:**
- `$FLOOR_ID` - Floor to inventory

**Expected Result:** List of temperature points with their details.

**Pattern:** Filtering + aggregation

**Current Status:** ⚠️ PARTIAL
- P1/P2: 1153 rows
- M1/M2/O1/O2: 0 rows

**Analysis Needed:** Query uses different filtering logic? Point type detection issue?

---

### Q5: Orphan Detection
**Natural Language:** Find all nodes that have no incoming or outgoing relationships (disconnected nodes).

**Parameters:** None

**Expected Result:** List of orphan nodes (should be 0 in a well-connected graph).

**Pattern:** Anti-join

**Current Status:** ⚠️ ALL ZERO (expected - no orphans in generated dataset)

---

### Q6: Timeseries Hourly Aggregation
**Natural Language:** For a given point, aggregate its timeseries values by hour within a time range.

**Parameters:**
- `$POINT_ID` - Point to aggregate
- `$DATE_START` / `$DATE_END` - Time range

**Expected Result:** Hourly aggregates (avg, min, max, count) for the point.

**Pattern:** Time bucketing + aggregation

**Current Status:** ⚠️ ALL ZERO

**Analysis Needed:** Time range mismatch? Point ID not found?

---

### Q7: Sensor Drift Detection (Top 20)
**Natural Language:** Find the 20 sensors with highest coefficient of variation (CV) in a building over a time period - indicating potential drift or anomalies.

**Parameters:**
- `$BUILDING_ID` - Building to analyze
- `$DATE_START` / `$DATE_END` - Time range

**Expected Result:** Top 20 sensors ranked by CV (stddev/mean).

**Pattern:** Statistical analysis over timeseries

**Current Status:** ⚠️ PARTIAL
- P1/P2: 20 rows ✅
- M1/M2/O1/O2: 0 rows

**Analysis Needed:** M1 query requires dechunking from ArchiveDay nodes - filter too strict? Time window mismatch?

---

### Q8: Tenant Energy Consumption
**Natural Language:** Calculate total energy consumption for a tenant by traversing: Tenant → Spaces → Equipment → Points → Timeseries.

**Parameters:**
- `$TENANT_ID` - Tenant to analyze
- `$DATE_START` / `$DATE_END` - Time range

**Expected Result:** Aggregated energy consumption for the tenant.

**Pattern:** Multi-hop traversal + timeseries aggregation

**Current Status:** ⚠️ PARTIAL
- P1/P2: 1 row
- M1/M2/O1/O2: 0 rows

**Analysis Needed:** Tenant → Space relationship missing? Different path semantics?

---

### Q9: Tenant Carbon Footprint
**Natural Language:** Calculate carbon footprint for a tenant based on energy consumption with emission factor.

**Parameters:**
- `$TENANT_ID` - Tenant to analyze
- `$DATE_START` / `$DATE_END` - Time range

**Expected Result:** Carbon footprint calculation (energy × factor).

**Pattern:** Similar to Q8 with carbon calculation

**Current Status:** ⚠️ PARTIAL
- P1/P2: 1 row
- M1/M2/O1/O2: 0 rows

---

### Q10: Security Access Analysis
**Natural Language:** Analyze access patterns for a security zone.

**Parameters:**
- `$ZONE_ID` - Zone to analyze
- `$DATE_START` / `$DATE_END` - Time range

**Expected Result:** Access event analysis.

**Pattern:** Zone → Access points → Events

**Current Status:** ⚠️ ALL ZERO

**Analysis Needed:** No Zone nodes in dataset? No security equipment generated?

---

### Q11: IT Infrastructure Impact
**Natural Language:** Analyze IT infrastructure dependencies in a building (server rooms, network equipment).

**Parameters:**
- `$BUILDING_ID` - Building to analyze

**Expected Result:** IT equipment dependency graph.

**Pattern:** Equipment dependency analysis

**Current Status:** ⚠️ PARTIAL
- P1/P2/O1/O2: 2 rows
- M1/M2: 0 rows (30 errors reported)

**Analysis Needed:** M1/M2 query syntax error? Missing node types?

---

### Q12: Full Building Analytics Dashboard
**Natural Language:** Get comprehensive building statistics: count of floors, spaces, equipment, points, tenants.

**Parameters:**
- `$BUILDING_ID` - Building to analyze
- `$DATE_START` / `$DATE_END` - For timeseries stats

**Expected Result:** Single row with building KPIs.

**Pattern:** Multi-dimensional aggregation

**Current Status:** ✅ MATCH (1 row all engines)

---

### Q13: Friday Office Comfort
**Natural Language:** Analyze comfort metrics (temperature, humidity, CO2) for office spaces on Fridays.

**Parameters:**
- `$SPACE_TYPE` - Space type pattern (e.g., 'office_%')
- `$DATE_START` / `$DATE_END` - Time range

**Expected Result:** Comfort metrics aggregated by space.

**Pattern:** DOW filtering + spatial join

**Current Status:** ⚠️ ALL ZERO

**Analysis Needed:** No Friday data in 2-day dataset? Space type mismatch?

---

## Summary

| Query | P1/P2 | M1/M2 | O1/O2 | Status |
|-------|-------|-------|-------|--------|
| Q1 | 1904 | 3806 | 827 | ❌ MISMATCH |
| Q2 | 2 | 2 | 2 | ✅ |
| Q3 | 21 | 21 | 17 | ❌ MISMATCH |
| Q4 | 1153 | 0 | 0 | ⚠️ PARTIAL |
| Q5 | 0 | 0 | 0 | ⚠️ ALL ZERO |
| Q6 | 0 | 0 | 0 | ⚠️ ALL ZERO |
| Q7 | 20 | 0 | 0 | ⚠️ PARTIAL |
| Q8 | 1 | 0 | 0 | ⚠️ PARTIAL |
| Q9 | 1 | 0 | 0 | ⚠️ PARTIAL |
| Q10 | 0 | 0 | 0 | ⚠️ ALL ZERO |
| Q11 | 2 | 0 | 2 | ⚠️ PARTIAL |
| Q12 | 1 | 1 | 1 | ✅ |
| Q13 | 0 | 0 | 0 | ⚠️ ALL ZERO |

## Priority Fixes

1. **Q1 MISMATCH (HIGH):** Core graph traversal - must produce identical results
2. **Q3 MISMATCH (MEDIUM):** Simple relationship lookup - should be trivial to match
3. **Q4/Q7/Q8/Q9 PARTIAL:** P1/P2 work but graph DBs don't - likely query semantics issue

## Next Steps

1. Debug Q1 across all engines - compare actual query execution
2. Verify relationship types are consistent across exports
3. Check time range parameters align with dataset timestamps
4. Investigate Q11 errors in M1/M2
