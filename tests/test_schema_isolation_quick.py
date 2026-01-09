#!/usr/bin/env python3
"""Quick test of schema isolation implementation."""
import time
from pathlib import Path
from src.basetype_benchmark.runner.loaders.postgres import PostgresLoader
from src.basetype_benchmark.runner.config import PostgresConfig

# Config
config = PostgresConfig(
    dsn="postgresql://postgres:postgres@localhost:5432/benchmark"
)

print("=" * 60)
print("Schema Isolation Quick Test")
print("=" * 60)

# Wait for DB to be ready
print("\nWaiting for database...")
time.sleep(3)

# Test P1
print("\n1. Testing P1 loader...")
p1_loader = PostgresLoader(config, paradigm="P1")
print(f"   ts_schema: {p1_loader.ts_schema}")
print(f"   struct_schema: {p1_loader.struct_schema}")

print("\n   Creating schemas...")
assert p1_loader.ensure_timeseries_schema(), "Failed to create ts schema"
assert p1_loader.ensure_structural_schema(), "Failed to create p1 schema"

print("\n   Loading P1 data...")
data_dir = Path("data/exports/p1/small-2d")
result = p1_loader.load_all(data_dir, workers=4)
print(f"   Result: {result.nodes_loaded} nodes, {result.edges_loaded} edges, {result.timeseries_loaded} timeseries")

# Verify schemas with psycopg
import psycopg
conn = psycopg.connect(config.dsn)
cur = conn.cursor()

print("\n2. Verifying database schemas...")
cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('ts', 'p1', 'p2') ORDER BY schema_name;")
schemas = [row[0] for row in cur.fetchall()]
print(f"   Schemas found: {schemas}")
assert "ts" in schemas, "ts schema not found!"
assert "p1" in schemas, "p1 schema not found!"

print("\n3. Verifying ts.timeseries...")
cur.execute("SELECT COUNT(*) FROM ts.timeseries;")
ts_count = cur.fetchone()[0]
print(f"   ts.timeseries rows: {ts_count}")
assert ts_count > 0, "No timeseries data!"

print("\n4. Verifying p1 tables...")
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'p1' ORDER BY table_name;")
p1_tables = [row[0] for row in cur.fetchall()]
print(f"   P1 tables: {', '.join(p1_tables)}")
assert "edges" in p1_tables, "p1.edges not found!"
assert "sites" in p1_tables, "p1.sites not found!"

print("\n5. Verifying p1.edges schema (should NOT have properties column)...")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'p1' AND table_name = 'edges' ORDER BY ordinal_position;")
edge_columns = [row[0] for row in cur.fetchall()]
print(f"   p1.edges columns: {', '.join(edge_columns)}")
assert "properties" not in edge_columns, "ERROR: p1.edges should NOT have properties column!"

print("\n6. Testing P2 loader (should create p2 schema with properties)...")
p2_loader = PostgresLoader(config, paradigm="P2")
print(f"   ts_schema: {p2_loader.ts_schema}")
print(f"   struct_schema: {p2_loader.struct_schema}")

print("\n   Clearing P2 database (keeping timeseries)...")
p2_loader.clear_database(keep_timeseries=True)

print("\n   Creating p2 structural schema...")
assert p2_loader.ensure_structural_schema(), "Failed to create p2 schema"

print("\n7. Verifying p2.edges schema (should HAVE properties column)...")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'p2' AND table_name = 'edges' ORDER BY ordinal_position;")
p2_edge_columns = [row[0] for row in cur.fetchall()]
print(f"   p2.edges columns: {', '.join(p2_edge_columns)}")
assert "properties" in p2_edge_columns, "ERROR: p2.edges SHOULD have properties column!"

print("\n8. Verifying timeseries preserved...")
cur.execute("SELECT COUNT(*) FROM ts.timeseries;")
ts_count_after = cur.fetchone()[0]
print(f"   ts.timeseries rows after P2 clear: {ts_count_after}")
assert ts_count_after == ts_count, f"Timeseries count changed! Was {ts_count}, now {ts_count_after}"

conn.close()

print("\n" + "=" * 60)
print("✅ All schema isolation tests PASSED!")
print("=" * 60)
print("\nKey achievements:")
print("  - ts schema created and shared")
print("  - p1 schema created without properties column")
print("  - p2 schema created WITH properties column")
print("  - timeseries preserved across paradigm switches")
print("  - No schema conflicts!")
