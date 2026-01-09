# Bug #4: O2 Runner Parameter Substitution Breaks SPARQL Syntax

**Date**: 2026-01-08
**Severity**: CRITICAL
**Status**: NOT FIXED
**Affects**: O2 paradigm (Oxigraph SPARQL queries)

---

## Problem

The Oxigraph runner's parameter substitution logic (`_substitute_params`) performs **naive string replacement** that corrupts SPARQL syntax by replacing SPARQL variables with literal values.

**File**: `src/basetype_benchmark/runner/runners/oxigraph.py` lines 197-233

### Buggy Code

```python
def _substitute_params(self, query: str, params: dict[str, Any]) -> str:
    result = query
    for key, value in params.items():
        # ... format value ...

        # Replace $key and ?key placeholders
        result = result.replace(f"${key}", formatted)
        result = result.replace(f"?{key}", formatted)  # ← BUG!

    return result
```

### Why This Breaks

**SPARQL variables use `?` prefix** (e.g., `?equipment_id`, `?name`). The substitution logic **cannot distinguish** between:
- **Parameter placeholders**: `?equipment_id` (intended for substitution)
- **SPARQL variables**: `?equipment_id` (must NOT be substituted)

**Example:**

Original query:
```sparql
SELECT ?equipment_id ?name
WHERE {
    ?eq btb:id ?equipment_id ;
        btb:name ?name .
}
```

With `params = {"equipment_id": "eq_ahu_1"}`, substitution produces:
```sparql
SELECT "eq_ahu_1" ?name          # ← INVALID: string in SELECT
WHERE {
    ?eq btb:id "eq_ahu_1" ;      # ← OK (coincidentally)
        btb:name ?name .
}
```

**Result**: HTTP 400 parse error (malformed SPARQL)

---

## Impact

**All O2 queries fail** when parameters are provided, even though:
- ✅ Loader works (data in default graph)
- ✅ Queries work manually (without params)
- ✅ Oxigraph endpoint functional

**Error symptoms:**
```
Q1 (1/3) ERROR: HTTP 400: error at 12:13: expected one of ">", [_]
Q15 (2/3) ERROR: HTTP 400: error at 13:27: expected IRI parsing fai
Q16 (3/3) ERROR: HTTP 400: error at 11:23: expected one of ">", [_]
```

Position errors (12:13, 13:27, 11:23) indicate **malformed SPARQL syntax** sent to server.

---

## Root Cause Analysis

### Problem 1: Ambiguous Placeholder Syntax

SPARQL uses `?var` for variables. The runner uses `?param` for placeholders. **These conflict.**

### Problem 2: Global String Replace

`str.replace()` is indiscriminate - it replaces **all occurrences**, not just placeholders.

### Problem 3: No Escaping Mechanism

SPARQL has no standard parameterized query syntax (unlike SQL's `$1, $2`). The runner must:
- Use distinct placeholder syntax (not `?`), OR
- Parse SPARQL to identify variables vs placeholders

---

## Solution Strategies

### Option A: Change Placeholder Syntax (Recommended)

Use `{{param}}` or `$PARAM` syntax to avoid conflict with `?var`:

**Before:**
```sparql
SELECT ?equipment_id WHERE { ?eq btb:id ?equipment_id }
```

**After:**
```sparql
SELECT ?equipment_id WHERE { ?eq btb:id {{equipment_id}} }
```

**Changes required:**
- Update all O2 query files (Q1-Q23)
- Update `_substitute_params` to use new syntax
- Update catalog parameter format definitions

**Pros:** Clean separation, no ambiguity
**Cons:** Requires query file updates

---

### Option B: SPARQL-Aware Parsing

Parse SPARQL to identify variables, avoid substituting them:

```python
import re

def _substitute_params(self, query: str, params: dict[str, Any]) -> str:
    # Extract SPARQL variables from SELECT/WHERE
    sparql_vars = re.findall(r'\?(\w+)', query)

    for key, value in params.items():
        # Skip if key is a SPARQL variable
        if key in sparql_vars:
            continue

        formatted = self._format_value(value)
        query = query.replace(f"${key}", formatted)

    return query
```

**Pros:** No query file changes
**Cons:** Complex, fragile (regex won't handle all SPARQL constructs)

---

### Option C: Prepared Query Pattern

Use `VALUES` clause for parameters (SPARQL 1.1 standard):

**Original:**
```sparql
SELECT ?equipment_id WHERE { ?eq btb:id ?equipment_id }
PARAMS: {"equipment_id": "eq_ahu_1"}
```

**Transformed:**
```sparql
VALUES ?param_equipment_id { "eq_ahu_1" }
SELECT ?equipment_id WHERE {
    ?eq btb:id ?equipment_id .
    FILTER(?equipment_id = ?param_equipment_id)
}
```

**Pros:** SPARQL-native, no syntax conflicts
**Cons:** Query rewriting complexity, performance impact

---

## Recommendation

**Implement Option A** (distinct placeholder syntax):
1. Use `{{param_name}}` for placeholders
2. Update `_substitute_params` to replace `{{...}}` only
3. Update O2 query files with new syntax
4. Keep SPARQL variables (`?var`) untouched

**Estimated effort:** 2-3 hours (22 query files + runner code)

---

## Workaround (Temporary)

Until fixed, O2 queries can only run **without parameters** or with **hardcoded VALUES**:

```sparql
# Instead of parameterized:
# SELECT ?id WHERE { ?eq btb:id ?equipment_id }
# PARAMS: {"equipment_id": "eq_1"}

# Use VALUES directly:
SELECT ?id WHERE {
    VALUES ?equipment_id { "eq_1" }
    ?eq btb:id ?equipment_id
}
```

---

## Testing After Fix

```bash
# Should return results, not HTTP 400
python3 -m src.basetype_benchmark.runner benchmark \
  -s data/generated/small-2d \
  -e data/exports \
  -p O2 \
  --queries Q1,Q15,Q16 \
  --ram 16 \
  --runs 1
```

**Expected:** No HTTP 400 errors, queries return rows

---

## Related Issues

- ✅ **Fixed**: Loader graph targeting (commit ff0a0ae)
- ✅ **Fixed**: Turtle syntax (commit 4356334)
- ✅ **Fixed**: Runner categories (commit 914b421)
- ❌ **This issue**: Param substitution (NOT FIXED)

---

## References

- **File**: `src/basetype_benchmark/runner/runners/oxigraph.py` lines 197-233
- **SPARQL 1.1 Spec**: https://www.w3.org/TR/sparql11-query/#rVARNAME
- **Similar issue**: PostgresRunner uses `$1, $2` syntax (no conflict with SQL)
