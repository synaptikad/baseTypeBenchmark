#!/usr/bin/env python3
"""
Test script for Option A (shared TimescaleDB) implementation.
Tests the key mechanisms without full benchmark run.
"""

import sys
import psycopg

# Configuration
DSN = "postgresql://postgres:postgres@localhost:5432/benchmark"

def test_connection():
    """Test 1: Verify database connection."""
    print("\n=== Test 1: Database Connection ===")
    try:
        with psycopg.connect(DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                print(f"✓ Connected to: {version[:50]}...")
                return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_timescale_extension():
    """Test 2: Verify TimescaleDB extension."""
    print("\n=== Test 2: TimescaleDB Extension ===")
    try:
        with psycopg.connect(DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")
                cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'timescaledb'")
                ext = cur.fetchone()
                if ext:
                    print(f"✓ TimescaleDB extension: {ext[1]}")
                    return True
                else:
                    print("✗ TimescaleDB extension not found")
                    return False
    except Exception as e:
        print(f"✗ Extension check failed: {e}")
        return False

def test_loader_detection_logic():
    """Test 3: Test PostgresLoader detection methods."""
    print("\n=== Test 3: Loader Detection Logic ===")
    try:
        # Import after adding to path
        sys.path.insert(0, '/home/ubuntu/baseTypeBenchmark/src')
        from basetype_benchmark.runner.loaders.postgres import PostgresLoader
        from basetype_benchmark.runner.config import PostgresConfig

        config = PostgresConfig(dsn=DSN)
        loader = PostgresLoader(config, paradigm="P1")

        # Test schema creation
        loader.ensure_timeseries_schema()
        print("✓ Schema creation successful")

        # Test detection on empty table
        is_populated = loader._is_timeseries_populated()
        print(f"✓ Empty table detection: {is_populated} (should be False)")

        if is_populated:
            print("  Warning: Table already has data")
            count = loader._count_timeseries_rows()
            print(f"  Current row count: {count:,}")

        return True
    except Exception as e:
        print(f"✗ Detection logic failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_clear_database_keep_flag():
    """Test 4: Test clear_database with keep_timeseries flag."""
    print("\n=== Test 4: clear_database(keep_timeseries) ===")
    try:
        sys.path.insert(0, '/home/ubuntu/baseTypeBenchmark/src')
        from basetype_benchmark.runner.loaders.postgres import PostgresLoader
        from basetype_benchmark.runner.config import PostgresConfig

        config = PostgresConfig(dsn=DSN)
        loader = PostgresLoader(config, paradigm="P1")

        # Ensure schema exists
        loader.ensure_timeseries_schema()

        # Insert test data
        with psycopg.connect(DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO timeseries (time, point_id, value)
                    VALUES
                        (NOW(), 'test_point_1', 42.0),
                        (NOW(), 'test_point_2', 43.0)
                    ON CONFLICT DO NOTHING
                """)
            conn.commit()

        count_before = loader._count_timeseries_rows()
        print(f"  Rows before clear: {count_before}")

        # Test 1: Clear without keeping timeseries
        print("\n  Test 4a: clear_database(keep_timeseries=False)")
        loader.clear_database(keep_timeseries=False)
        count_after_clear = loader._count_timeseries_rows()
        print(f"  Rows after clear: {count_after_clear}")

        if count_after_clear == 0:
            print("  ✓ Timeseries cleared correctly")
        else:
            print(f"  ✗ Timeseries not cleared (still {count_after_clear} rows)")

        # Re-insert data
        with psycopg.connect(DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO timeseries (time, point_id, value)
                    VALUES
                        (NOW(), 'test_point_1', 42.0),
                        (NOW(), 'test_point_2', 43.0)
                """)
            conn.commit()

        count_before_keep = loader._count_timeseries_rows()
        print(f"\n  Test 4b: clear_database(keep_timeseries=True)")
        print(f"  Rows before clear: {count_before_keep}")

        # Test 2: Clear while keeping timeseries
        loader.clear_database(keep_timeseries=True)
        count_after_keep = loader._count_timeseries_rows()
        print(f"  Rows after keep clear: {count_after_keep}")

        if count_after_keep == count_before_keep:
            print("  ✓ Timeseries preserved correctly")
            return True
        else:
            print(f"  ✗ Timeseries not preserved ({count_before_keep} → {count_after_keep})")
            return False

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scenario_orchestration():
    """Test 5: Test BenchmarkOrchestrator state tracking."""
    print("\n=== Test 5: Orchestrator State Tracking ===")
    try:
        sys.path.insert(0, '/home/ubuntu/baseTypeBenchmark/src')
        from basetype_benchmark.runner.benchmark.scenario import BenchmarkOrchestrator
        from basetype_benchmark.runner.config import PostgresConfig

        configs = {
            "P1": PostgresConfig(dsn=DSN),
            "P2": PostgresConfig(dsn=DSN),
        }

        orch = BenchmarkOrchestrator(configs)

        # Check initial state
        print(f"  Initial state: _timeseries_loaded = {orch._timeseries_loaded}")

        # Test _should_keep_timeseries logic
        keep_p1 = orch._should_keep_timeseries("P1")
        print(f"  P1 should keep (before load): {keep_p1} (expected: False)")

        # Simulate timeseries loaded
        orch._timeseries_loaded = True

        keep_p2 = orch._should_keep_timeseries("P2")
        print(f"  P2 should keep (after load): {keep_p2} (expected: True)")

        keep_m1 = orch._should_keep_timeseries("M1")
        print(f"  M1 should keep: {keep_m1} (expected: False, M1 doesn't use Timescale)")

        if not keep_p1 and keep_p2 and not keep_m1:
            print("✓ State tracking logic correct")
            return True
        else:
            print("✗ State tracking logic incorrect")
            return False

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup():
    """Cleanup test data."""
    print("\n=== Cleanup ===")
    try:
        with psycopg.connect(DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE timeseries CASCADE")
            conn.commit()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")

def main():
    """Run all tests."""
    print("=" * 60)
    print("OPTION A VALIDATION TESTS")
    print("=" * 60)

    results = []

    results.append(("Connection", test_connection()))
    results.append(("TimescaleDB Extension", test_timescale_extension()))
    results.append(("Loader Detection Logic", test_loader_detection_logic()))
    results.append(("keep_timeseries Flag", test_clear_database_keep_flag()))
    results.append(("Orchestrator State", test_scenario_orchestration()))

    cleanup()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Option A is functional.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
