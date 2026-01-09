# SPARQL Parameter Binding Strategy

## Overview

This document describes the parameter binding strategy used in the O2 (Oxigraph) runner for SPARQL queries.

## Why VALUES Injection (Not String Replace)

SPARQL uses `?` for variables (e.g., `?meterId`). Naive string replacement breaks queries:

```sparql
-- Original query
SELECT ?id ?type ?name
WHERE {
    ?source btb:id ?meterId .
    ...
}

-- After naive replace of ?meterId with "eq_main_1"
SELECT ?id ?type ?name        -- BROKEN: ?meterId in SELECT becomes undefined
WHERE {
    ?source btb:id "eq_main_1" .
    ...
}
```

The SPARQL 1.1 `VALUES` clause is the correct approach for parameter injection.

## Implementation

### Core Functions

**File**: `src/basetype_benchmark/runner/runners/oxigraph.py`

#### `_inject_values_clause()` (lines 266-335)

Injects a `VALUES` clause after `WHERE {`:

```python
def _inject_values_clause(self, query: str, params: dict[str, Any]) -> str:
    # 1. Check for conflicts with existing VALUES
    # 2. Format values as SPARQL literals
    # 3. Build VALUES clause
    # 4. Inject via regex after WHERE {
```

**Injection point**: Just after `WHERE {` (beginning of the pattern).

**Example transformation**:

```sparql
-- Before (with params {"meterId": "eq_main_1"})
SELECT ?id ?type ?name
WHERE {
    ?source btb:id ?meterId .
    ?source btb:feeds+ ?target .
}

-- After injection
SELECT ?id ?type ?name
WHERE {
    VALUES ?meterId { "eq_main_1" }
    ?source btb:id ?meterId .
    ?source btb:feeds+ ?target .
}
```

#### `_format_sparql_value()` (lines 212-264)

Formats Python values as SPARQL typed literals:

| Python Type | SPARQL Format | Example |
|-------------|---------------|---------|
| `date` | `"2024-06-01"^^xsd:date` | Date objects |
| `datetime` | `"2024-06-01T00:00:00"^^xsd:dateTime` | Timestamps |
| `int` | `123` | Unquoted integers |
| `float` | `3.14` | Unquoted decimals |
| `bool` | `true` / `false` | Boolean literals |
| `str` | `"escaped_value"` | Quoted with escaping |
| `None` | `UNDEF` | NULL handling |

### Multi-Parameter Support

For queries with multiple parameters:

```sparql
-- Single parameter
VALUES ?meterId { "eq_main_1" }

-- Multiple parameters
VALUES (?meterId ?startDate) { ("eq_main_1" "2024-06-01"^^xsd:date) }
```

## Conflict Detection

The implementation detects existing `VALUES` clauses to avoid conflicts:

```python
# Check if VALUES already exists for this variable
existing_values = re.findall(r'VALUES\s+\?\w+', query, re.IGNORECASE)
if any(f'?{var}' in existing for existing in existing_values):
    raise ValueError(f"VALUES clause already exists for ?{var}")
```

## Known Pitfalls

### Hardcoded VALUES in Query Files

Some queries (Q1, Q15) have hardcoded `VALUES` for testing:

```sparql
-- Q1.sparql (hardcoded for standalone testing)
VALUES ?meterId { "eq_main_1" }
```

**Recommendation**: Remove hardcoded VALUES and let the runner inject them dynamically.

### Variable Name Casing

Parameter keys are normalized based on paradigm:
- **P1/P2**: `lowercase` for `%(name)s` placeholders
- **M1/M2**: `lowercase` for `$name` Cypher params
- **O2**: `camelCase` for `?varName` SPARQL bindings

**Example**: `METER_ID` → `meterId` for O2

### WHERE Clause Required

The injection requires a `WHERE {` clause in the query. Queries without `WHERE` will raise `ValueError`.

## Testing

To verify VALUES injection works correctly:

```bash
# Run a query with dynamic params
python -m basetype_benchmark.runner.cli benchmark -p O2 --queries Q1

# Check logs for injected VALUES
# Should show: "Injecting VALUES ?meterId { ... }"
```

## References

- [SPARQL 1.1 VALUES](https://www.w3.org/TR/sparql11-query/#inline-data)
- [Oxigraph SPARQL Support](https://github.com/oxigraph/oxigraph)
