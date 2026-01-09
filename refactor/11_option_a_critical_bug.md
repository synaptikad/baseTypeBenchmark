# Option A Critical Bug - Containers Stopped Between Paradigms

**Date Discovered**: 2026-01-08
**Status**: CRITICAL - BLOCKS Option A functionality
**Severity**: BLOCKER

---

## Summary

Option A implementation is **fundamentally broken** because containers are stopped and restarted between each paradigm execution, destroying the shared TimescaleDB data that Option A depends on.

## Root Cause

In [scenario.py:303](../src/basetype_benchmark/runner/benchmark/scenario.py#L303), the `_run_paradigm()` method unconditionally calls `self.isolation.stop_paradigm(paradigm)` in a finally block after each paradigm completes:

```python
# scenario.py lines 300-303
finally:
    # 5. Stop containers
    console.print(f"  [dim]Stopping containers...[/dim]")
    self.isolation.stop_paradigm(paradigm)
```

This happens for EVERY paradigm, regardless of whether subsequent paradigms need to reuse the data.

## Impact

### Expected Behavior (Option A Design)
1. P1 loads timeseries into TimescaleDB
2. Container stays running with data intact
3. P2 detects timeseries exists, skips loading
4. M2 detects timeseries exists, skips loading
5. O2 detects timeseries exists, skips loading

### Actual Behavior (Current Implementation)
1. P1 loads timeseries into TimescaleDB
2. **Container is STOPPED, data is LOST**
3. P2 starts fresh container with empty database
4. P2 loads timeseries again (duplication)
5. **Container is STOPPED, data is LOST**
6. M2 starts fresh container with empty database
7. M2 loads timeseries again (duplication)
8. And so on...

## Evidence

### Test Output Shows Container Stop/Start Cycle

From [e2e_test_output_v2.log](../../tmp/e2e_test_output_v2.log):

```
===== P1 (1/4) =====
  Exporting P1...
  Starting containers...      <--- Fresh start
  Loading data...
  Running RAM gradient...
  ...
  Stopping containers...      <--- Data destroyed

===== P2 (2/4) =====
  Exporting P2...
  Starting containers...      <--- Fresh start (empty DB!)
  Loading data...
  Running RAM gradient...
  ...
  Stopping containers...      <--- Data destroyed again
```

### Skip Messages Never Appeared

The validation test found ZERO skip messages for P2, M2, or O2:
- P2: "Timeseries already loaded, skipping (Option A)" - NOT FOUND
- M2: "Timeseries already loaded for M2, skipping" - NOT FOUND
- O2: "Timeseries already loaded for O2, skipping" - NOT FOUND

This is because `_is_timeseries_populated()` always returns False when querying a freshly started container.

### Volumes Are Preserved But Containers Are Not

The [isolation.py:171](../src/basetype_benchmark/runner/ram/isolation.py#L171) comment says:
```python
"""Stop and remove containers for a paradigm.

Note: Volumes are preserved to support Option A (shared TimescaleDB).
Use docker volume prune manually if cleanup is needed.
```

However, preserving volumes is USELESS if the containers are stopped, because:
1. Stopping a container loses all in-memory state
2. When a new container starts, it mounts volumes but they're EMPTY (Docker volumes don't persist across container lifecycles unless explicitly configured)
3. PostgreSQL/TimescaleDB data is lost when the container stops

## Code Flow Analysis

### Scenario.py: _run_paradigm() - Lines 245-309

```python
def _run_paradigm(...):
    try:
        # 1. Export paradigm data
        paradigm_export_dir = self._export_paradigm(...)

        # 2. Start containers
        self.isolation.start_paradigm(paradigm)  # <-- Stops previous paradigm!

        try:
            # 3. Load data
            self._load_data(paradigm, paradigm_export_dir)

            # 4. Run gradient
            gradient_result = self._run_gradient(...)

        finally:
            # 5. Stop containers
            self.isolation.stop_paradigm(paradigm)  # <-- BUG: Always stops!
```

### Isolation.py: start_paradigm() - Lines 120-166

```python
def start_paradigm(self, paradigm: str, clean_volumes: bool = False):
    # Stop any currently running paradigm
    if self._current_paradigm:
        self.stop_paradigm(self._current_paradigm)  # <-- BUG: Always stops!

    # Start new paradigm containers
    ...
```

## Why Option A Appeared to Work in Unit Tests

The unit tests in [test_option_a.py](../../test_option_a.py) passed because they:
1. Mock the database connections
2. Test individual loader methods in isolation
3. Don't actually run the full benchmark orchestration

The unit tests validate that:
- `_is_timeseries_populated()` can detect existing data
- `clear_database(keep_timeseries=True)` works
- Skip logic is syntactically correct

But they don't validate the END-TO-END flow where containers are stopped between paradigms.

## Fix Required (Not Applied - Documentation Only)

To fix Option A, the code must be modified to:

### Option 1: Skip stop_paradigm() for shared TimescaleDB

```python
# scenario.py _run_paradigm()
finally:
    # 5. Stop containers (unless next paradigm needs shared TimescaleDB)
    if not self._should_keep_containers_running(paradigm):
        console.print(f"  [dim]Stopping containers...[/dim]")
        self.isolation.stop_paradigm(paradigm)

def _should_keep_containers_running(self, paradigm: str) -> bool:
    """Check if containers should stay running for next paradigm."""
    if paradigm not in ("P1", "P2", "M2", "O2"):
        return False  # Non-TimescaleDB paradigms don't share state

    # Check if next paradigm in queue also uses TimescaleDB
    current_idx = self.paradigms.index(paradigm)
    if current_idx < len(self.paradigms) - 1:
        next_paradigm = self.paradigms[current_idx + 1]
        return next_paradigm in ("P1", "P2", "M2", "O2")

    return False  # Last paradigm, safe to stop
```

### Option 2: Don't stop between paradigms, only at end

```python
# scenario.py run()
for paradigm in paradigms:
    results.results[paradigm] = self._run_paradigm(
        paradigm=paradigm,
        source_dir=source_dir,
        export_dir=export_dir,
        queries=queries,
        scenario=scenario,
        cleanup_exports=cleanup_exports,
        on_progress=on_progress,
        keep_containers=True,  # <-- New parameter
    )

# Stop all containers at the very end
for paradigm in paradigms:
    self.isolation.stop_paradigm(paradigm)
```

### Option 3: Selective restart in isolation.py

```python
# isolation.py start_paradigm()
def start_paradigm(self, paradigm: str, clean_volumes: bool = False):
    paradigm = paradigm.upper()
    container_set = PARADIGM_CONTAINERS[paradigm]

    # Check if TimescaleDB container is already running
    if "timescale" in container_set.containers:
        # Don't stop if TimescaleDB is needed for next paradigm
        if not (self._current_paradigm and
                self._shares_timescaledb(self._current_paradigm, paradigm)):
            # Stop previous paradigm
            if self._current_paradigm:
                self.stop_paradigm(self._current_paradigm)
    else:
        # Always stop for non-TimescaleDB paradigms
        if self._current_paradigm:
            self.stop_paradigm(self._current_paradigm)

    # Start containers (idempotent if already running)
    ...

def _shares_timescaledb(self, p1: str, p2: str) -> bool:
    """Check if both paradigms use TimescaleDB."""
    ts_paradigms = {"P1", "P2", "M2", "O2"}
    return p1 in ts_paradigms and p2 in ts_paradigms
```

## Recommendations

1. This bug must be fixed BEFORE G2 (Option A validation) can be marked as completed
2. After fixing, re-run the e2e validation test to verify skip messages appear
3. Add integration tests that actually run multiple paradigms in sequence
4. Consider adding a `--keep-containers` flag for debugging/testing

## Related Documents

- [HANDOFF.md](../HANDOFF.md) - Option A implementation status
- [03_implementation_playbook.md](03_implementation_playbook.md) - Phase 3 design
- [option_a_validation_report.md](option_a_validation_report.md) - Test results showing failure
- [test_option_a_e2e.py](../../test_option_a_e2e.py) - End-to-end validation script

## Conclusion

**Option A is NOT implemented correctly.** The core mechanism (container persistence) is broken by unconditional `stop_paradigm()` calls. All 11 commits (phases 0-3) focused on loader logic, but missed the critical orchestration bug in scenario.py.

The unit tests passed because they only validate individual components, not the end-to-end workflow.

**G2 CANNOT be marked as completed** until this bug is fixed.
