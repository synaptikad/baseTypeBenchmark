# 12 - Schema Isolation Implementation Plan (Option A Fix)

**Date**: 2026-01-08
**Status**: PLANNED (not yet implemented)
**Related**: `addendum.md`, `refactor/11_option_a_critical_bug.md`

---

## Summary

This document describes the implementation plan for fixing Option A using PostgreSQL schema isolation, as specified in `addendum.md`. This is the correct solution to the P1/P2 schema incompatibility problem discovered during E2E testing.

**Current Status (commit 8f98537)**:
- ✅ Container lifecycle fix implemented (P2→M2→O2 keep containers running)
- ✅ M2 and O2 skip messages working
- ❌ P2 fails with "column properties does not exist" error
- ❌ P1 excluded from sharing (workaround, not a real fix)

**Target Status**:
- ✅ P1, P2, M2, O2 all share timeseries via schema isolation
- ✅ P1 and P2 have separate structural schemas (p1/p2)
- ✅ Timeseries lives in shared `ts` schema
- ✅ All paradigms work without schema conflicts

---

## Problem Analysis

### Root Cause
P1 and P2 have **incompatible structural schemas**:
- P1: `edges` table WITHOUT `properties` column (relational)
- P2: `edges` table WITH `properties JSONB` column

When P1's container is kept alive for P2, P2 tries to load data into P1's schema and fails.

### Why Current Fix is Incomplete
Our container lifecycle fix (commit 8f98537) keeps containers running, but doesn't solve the schema conflict. We temporarily excluded P1 from sharing, which defeats the purpose of Option A.

### Correct Solution: Schema Isolation
Use PostgreSQL schemas (namespaces) to isolate structural tables while sharing timeseries:
- `ts` schema: shared timeseries hypertable
- `p1` schema: P1 structural tables (nodes, edges without properties, etc.)
- `p2` schema: P2 structural tables (nodes, edges with properties JSONB, etc.)

All in the **same PostgreSQL/TimescaleDB container**, no performance penalty.

---

## Implementation Plan

### Phase 1: PostgresLoader Schema Support

**File**: `src/basetype_benchmark/runner/loaders/postgres.py`

#### 1.1 Add Schema Names Property

```python
class PostgresLoader(BaseLoader):
    def __init__(self, config: PostgresConfig, paradigm: Literal["P1", "P2"]):
        super().__init__(engine=paradigm)
        self.config = config
        self.paradigm = paradigm

        # NEW: Schema isolation for Option A
        self.ts_schema = "ts"  # Shared timeseries schema
        self.struct_schema = "p1" if paradigm == "P1" else "p2"  # Structural schema

        self._parallel_copy_bin = shutil.which("timescaledb-parallel-copy")
```

#### 1.2 Create ensure_timeseries_schema() Method

This method should be called BEFORE any timeseries operations:

```python
def ensure_timeseries_schema(self) -> bool:
    """Ensure ts schema and timeseries hypertable exist.

    This is called once per benchmark run to set up the shared
    timeseries infrastructure for Option A.

    Returns:
        True if successful
    """
    schema_sql = """
    -- Create ts schema if not exists
    CREATE SCHEMA IF NOT EXISTS ts;

    -- Enable TimescaleDB extension
    CREATE EXTENSION IF NOT EXISTS timescaledb;

    -- Create timeseries hypertable in ts schema
    CREATE TABLE IF NOT EXISTS ts.timeseries (
        ts TIMESTAMPTZ NOT NULL,
        point_id TEXT NOT NULL,
        value DOUBLE PRECISION,
        quality INTEGER,
        PRIMARY KEY (ts, point_id)
    );

    -- Convert to hypertable
    SELECT create_hypertable('ts.timeseries', 'ts', if_not_exists => TRUE);

    -- Create performance index
    CREATE INDEX IF NOT EXISTS idx_timeseries_point_ts
      ON ts.timeseries (point_id, ts DESC);
    """

    try:
        with psycopg.connect(self.config.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error creating ts schema: {e}")
        return False
```

#### 1.3 Create ensure_structural_schema() Method

This creates the paradigm-specific structural tables:

```python
def ensure_structural_schema(self) -> bool:
    """Ensure paradigm-specific structural schema exists.

    Creates p1 or p2 schema and tables based on self.paradigm.

    Returns:
        True if successful
    """
    # Create schema
    schema_create = f"CREATE SCHEMA IF NOT EXISTS {self.struct_schema};"

    if self.paradigm == "P1":
        # P1: Relational tables (no JSONB properties)
        tables_sql = """
        CREATE TABLE IF NOT EXISTS {schema}.sites (...);
        CREATE TABLE IF NOT EXISTS {schema}.buildings (...);
        CREATE TABLE IF NOT EXISTS {schema}.floors (...);
        CREATE TABLE IF NOT EXISTS {schema}.spaces (...);
        CREATE TABLE IF NOT EXISTS {schema}.equipment (...);
        CREATE TABLE IF NOT EXISTS {schema}.points (...);
        CREATE TABLE IF NOT EXISTS {schema}.edges (
            edge_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            edge_type TEXT NOT NULL
            -- NO properties column
        );
        CREATE TABLE IF NOT EXISTS {schema}.tenants (...);
        CREATE TABLE IF NOT EXISTS {schema}.zones (...);
        CREATE TABLE IF NOT EXISTS {schema}.contracts (...);
        """.format(schema=self.struct_schema)
    else:  # P2
        # P2: JSONB-enriched tables
        tables_sql = """
        CREATE TABLE IF NOT EXISTS {schema}.nodes (
            node_id TEXT PRIMARY KEY,
            node_type TEXT NOT NULL,
            properties JSONB  -- JSONB properties
        );
        CREATE TABLE IF NOT EXISTS {schema}.edges (
            edge_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            edge_type TEXT NOT NULL,
            properties JSONB  -- JSONB properties
        );
        CREATE TABLE IF NOT EXISTS {schema}.points (
            point_id TEXT PRIMARY KEY,
            node_id TEXT NOT NULL,
            properties JSONB  -- JSONB properties
        );
        """.format(schema=self.struct_schema)

    try:
        with psycopg.connect(self.config.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(schema_create)
                cur.execute(tables_sql)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error creating {self.struct_schema} schema: {e}")
        return False
```

**Note**: The exact table definitions should be extracted from the existing code and adapted with schema prefixes.

#### 1.4 Update clear_database()

```python
def clear_database(self, keep_timeseries: bool = False) -> bool:
    """Clear database for paradigm.

    Args:
        keep_timeseries: If True, preserve ts.timeseries (Option A)

    Strategy:
        - Drop and recreate structural schema (cleanest approach)
        - Optionally truncate ts.timeseries (if not keeping)

    Returns:
        True if successful
    """
    try:
        with psycopg.connect(self.config.dsn) as conn:
            with conn.cursor() as cur:
                # Drop structural schema CASCADE (removes all tables/indexes/constraints)
                cur.execute(f"DROP SCHEMA IF EXISTS {self.struct_schema} CASCADE;")

                # Recreate empty structural schema
                cur.execute(f"CREATE SCHEMA {self.struct_schema};")

                # Truncate timeseries if not keeping
                if not keep_timeseries:
                    cur.execute("TRUNCATE TABLE ts.timeseries;")

            conn.commit()

        # Recreate structural tables
        return self.ensure_structural_schema()

    except Exception as e:
        print(f"Error clearing database: {e}")
        return False
```

#### 1.5 Update load_all() to Call ensure_*_schema()

```python
def load_all(
    self,
    data_dir: Path,
    progress_callback: ProgressCallback | None = None,
    workers: int = 16,
) -> LoadResult:
    """Load all data for paradigm.

    This now ensures schemas exist before loading.
    """
    result = LoadResult()

    # Step 1: Ensure timeseries schema exists (shared)
    if not self.ensure_timeseries_schema():
        result.success = False
        result.errors.append("Failed to create ts schema")
        return result

    # Step 2: Ensure structural schema exists (paradigm-specific)
    if not self.ensure_structural_schema():
        result.success = False
        result.errors.append(f"Failed to create {self.struct_schema} schema")
        return result

    # Step 3: Load data (existing logic with schema-qualified table names)
    # ... rest of existing load_all() logic
```

#### 1.6 Update _is_timeseries_populated()

This is used by the skip logic:

```python
def _is_timeseries_populated(self) -> bool:
    """Check if ts.timeseries has data (Option A detection).

    Returns:
        True if timeseries table exists and has rows
    """
    try:
        with psycopg.connect(self.config.dsn) as conn:
            with conn.cursor() as cur:
                # Check if ts schema and table exist
                cur.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'ts'
                        AND table_name = 'timeseries'
                    )
                """)
                if not cur.fetchone()[0]:
                    return False

                # Check if table has data
                cur.execute("SELECT COUNT(*) FROM ts.timeseries LIMIT 1;")
                count = cur.fetchone()[0]
                return count > 0
    except Exception:
        return False
```

---

### Phase 2: PostgresRunner search_path Configuration

**File**: `src/basetype_benchmark/runner/runners/postgres.py`

#### 2.1 Set search_path on Connection

```python
class PostgresRunner(BaseRunner):
    def __init__(self, config: PostgresConfig, paradigm: Literal["P1", "P2"]):
        super().__init__(engine=paradigm)
        self.config = config
        self.paradigm = paradigm

        # NEW: search_path for schema isolation
        self.search_path = f"{paradigm.lower()}, ts, public"

    def _get_connection(self):
        """Get connection with correct search_path."""
        conn = psycopg.connect(self.config.dsn)

        # Set search_path for paradigm
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {self.search_path};")

        return conn
```

This ensures queries like `SELECT * FROM edges` automatically resolve to `p1.edges` or `p2.edges` based on paradigm, while `timeseries` resolves to `ts.timeseries`.

---

### Phase 3: Update Hybrid Loaders (M2/O2)

**Files**:
- `src/basetype_benchmark/runner/loaders/memgraph.py`
- `src/basetype_benchmark/runner/loaders/oxigraph.py`

#### 3.1 Pass ts_config with Schema Awareness

M2 and O2 loaders receive a `ts_config` (PostgresConfig) to access the shared timeseries. They need to know about the `ts` schema:

```python
class MemgraphLoader(BaseLoader):
    def __init__(self, config: MemgraphConfig, ts_config: PostgresConfig | None = None):
        super().__init__(engine="M2")
        self.config = config
        self.ts_config = ts_config

        # For timeseries access
        self.ts_schema = "ts"

    def _is_timeseries_populated(self) -> bool:
        """Check if ts.timeseries exists and has data."""
        if not self.ts_config:
            return False

        try:
            with psycopg.connect(self.ts_config.dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT 1 FROM ts.timeseries LIMIT 1
                        )
                    """)
                    return cur.fetchone()[0]
        except Exception:
            return False
```

---

### Phase 4: Update scenario.py timescale_paradigms

**File**: `src/basetype_benchmark/runner/benchmark/scenario.py`

Now that P1 and P2 can share via schema isolation, **re-include P1** in the sharing set:

```python
def _should_keep_containers_running(
    self,
    current_paradigm: str,
    all_paradigms: list[str]
) -> bool:
    """Check if containers should stay running for next paradigm."""

    # TimescaleDB paradigms that can share state via Option A
    # WITH schema isolation: P1, P2, M2, O2 can all share ts.timeseries
    timescale_paradigms = {"P1", "P2", "M2", "O2"}  # P1 re-included!

    # ... rest of logic unchanged
```

**File**: `src/basetype_benchmark/runner/ram/isolation.py`

Same update:

```python
# Stop any currently running paradigm (unless they share TimescaleDB)
if self._current_paradigm:
    # Check if both paradigms use TimescaleDB (Option A shared state)
    # WITH schema isolation: all TimescaleDB paradigms can share
    timescale_paradigms = {"P1", "P2", "M2", "O2"}  # P1 re-included!

    current_uses_ts = self._current_paradigm in timescale_paradigms
    next_uses_ts = paradigm in timescale_paradigms

    # Only stop if they don't share TimescaleDB
    if not (current_uses_ts and next_uses_ts):
        self.stop_paradigm(self._current_paradigm)
```

---

## Migration Strategy

### Step 1: Database Reset
Before testing the new schema approach, **clean the existing database**:

```bash
docker compose -f docker/docker-compose.yml down -v  # Remove volumes
docker compose -f docker/docker-compose.yml up -d timescale
```

This ensures no old schema conflicts.

### Step 2: Implement Changes in Order

1. **PostgresLoader** (Phase 1) - Core schema isolation
2. **PostgresRunner** (Phase 2) - search_path configuration
3. **Hybrid loaders** (Phase 3) - M2/O2 ts schema awareness
4. **Orchestration** (Phase 4) - Re-include P1 in sharing

### Step 3: Test Incrementally

```bash
# Test 1: P1 alone
python -m src.basetype_benchmark.runner benchmark \
  -s data/generated/small-2d \
  -e data/exports \
  -p P1 \
  --ram 16 --runs 1

# Test 2: P1 → P2 (schema isolation test)
python -m src.basetype_benchmark.runner benchmark \
  -s data/generated/small-2d \
  -e data/exports \
  -p P1,P2 \
  --ram 16 --runs 1 --no-cleanup

# Verify:
docker exec benchmark-timescale psql -U postgres -d benchmark -c "\dn"  # List schemas
docker exec benchmark-timescale psql -U postgres -d benchmark -c "\dt p1.*"  # P1 tables
docker exec benchmark-timescale psql -U postgres -d benchmark -c "\dt p2.*"  # P2 tables
docker exec benchmark-timescale psql -U postgres -d benchmark -c "SELECT COUNT(*) FROM ts.timeseries;"  # Shared TS

# Test 3: Full Option A (P1 → P2 → M2 → O2)
python test_option_a_e2e.py
```

### Step 4: Validation

✅ **Success Criteria**:
1. P1 creates `p1` schema with relational tables
2. P2 creates `p2` schema with JSONB tables
3. Both share `ts.timeseries`
4. Skip messages appear for P2, M2, O2:
   - `⏭️ Timeseries already loaded, skipping (Option A)` for P2
   - `⏭️ Timeseries already loaded for M2, skipping` for M2
   - `⏭️ Timeseries already loaded for O2, skipping` for O2
5. Timeseries row count stable across all paradigms
6. No schema conflicts or "column does not exist" errors

---

## Estimated Effort

- **Phase 1** (PostgresLoader): 2-3 hours (core implementation)
- **Phase 2** (PostgresRunner): 30 minutes (search_path config)
- **Phase 3** (Hybrid loaders): 1 hour (ts schema awareness)
- **Phase 4** (Orchestration): 10 minutes (re-include P1)
- **Testing**: 1-2 hours (incremental validation)

**Total**: ~5-7 hours of focused implementation + testing

---

## Current Status (End of Session)

**Completed**:
- ✅ Container lifecycle fix (commit 8f98537)
- ✅ M2/O2 skip messages working
- ✅ Documentation of schema isolation approach (this file)

**Blocked** (awaiting implementation):
- ❌ Schema isolation in PostgresLoader
- ❌ search_path in PostgresRunner
- ❌ P1 → P2 compatibility
- ❌ Full P1 → P2 → M2 → O2 Option A validation

**Next Session**:
1. Implement Phase 1 (PostgresLoader schema isolation)
2. Test P1 → P2 transition
3. Re-run E2E validation test
4. Mark G2 as COMPLETED if validation passes

---

## References

- `addendum.md` - Complete specification of schema isolation approach
- `refactor/11_option_a_critical_bug.md` - Original bug report
- `refactor/03_implementation_playbook.md` - Phase 3 objectives
- Commit 8f98537 - Container lifecycle fix (incomplete without schema isolation)
