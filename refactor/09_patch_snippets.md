# 09 - Patch snippets (copy-paste)

These snippets are designed to be pasted into the V3 codebase by a dev agent.

## A. Remove volume deletion in IsolationManager

File: `src/basetype_benchmark/runner/ram/isolation.py`

Find:
```python
cmd = [
  "docker", "compose", "-f", str(self.compose_file),
  "down", "-v",
]
```

Replace with:
```python
cmd = [
  "docker", "compose", "-f", str(self.compose_file),
  "down",
]
```

Rationale:
- Preserve volumes so Timescale data survives container restarts.

## B. PostgresLoader.clear_database keep_timeseries flag

File: `src/basetype_benchmark/runner/loaders/postgres.py`

Change signature:
```python
def clear_database(self) -> None:
```

To:
```python
def clear_database(self, keep_timeseries: bool = False) -> None:
```

Then guard the timeseries truncate:
```python
if not keep_timeseries:
    cursor.execute("TRUNCATE TABLE timeseries;")
```

Also ensure P1/P2 scenario calls pass `keep_timeseries=True` when Option A is enabled.

## C. Skip timeseries load when already loaded (scenario-level flag)

File: `src/basetype_benchmark/runner/benchmark/scenario.py`

Add to __init__:
```python
self._timeseries_loaded = False
```

In `_load_data()`:
- If paradigm uses Timescale and `_timeseries_loaded` is False:
  - load timeseries and set True
- Else:
  - do not call any timeseries load function

For M2/O2, you can:
- add a `skip_timeseries` argument to `MemgraphLoader.load_all()` / `OxigraphLoader.load_all()`
or
- wrap timeseries load calls with an if condition in scenario.

## D. Escape literal percent signs for psycopg SQL

File: `src/basetype_benchmark/runner/runners/postgres.py`

Add helper:
```python
import re

def _escape_percent_literals(sql: str) -> str:
    # Replace any % not followed by s, (, or % with %%
    return re.sub(r'%(?![s%(])', '%%', sql)
```

Then apply before execute:
```python
query = _escape_percent_literals(query)
```

This should run after `$1` -> `%s` conversion.

## E. Fix catalog categories for Q10/Q11

File: `queries/catalog.yaml`

Change:
```yaml
Q10:
  category: hybrid
Q11:
  category: hybrid
```

To:
```yaml
Q10:
  category: graph_only
Q11:
  category: graph_only
```

## F. Rename hybrid TS files (recommended)

Rename:
- `queries/m2/ts/Q06.sql` -> `Q6.sql`
- `queries/m2/ts/Q07.sql` -> `Q7.sql`
- `queries/m2/ts/Q08.sql` -> `Q8.sql`
- `queries/m2/ts/Q09.sql` -> `Q9.sql`
- same for `queries/o2/ts/`

If you do not want renames, adjust the loader to accept both `Q7.sql` and `Q07.sql`.

## G. Warmup ordered SQL params (optional)

File: `src/basetype_benchmark/runner/ram/gradient.py`

In `_warmup()`, for P1/P2 build ordered tuple:
```python
ordered = tuple(params[name] for name in query_def.parameter_order)
runner.execute(query_text, ordered, timeout)
```

Instead of passing dict.

