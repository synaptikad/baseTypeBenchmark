# Sampler Improvements: Reducing 0-Row Results

## Problem Statement

The current parameter sampler (`ParamSampler`) generates random values independently, without considering query patterns. This causes many queries to return 0 rows because the sampled parameter combinations don't match actual data relationships.

**Example**: Q5 searches for equipment in a specific space, but:
- Sampled `space_id` may not have any equipment
- Even if it does, the equipment may not have the required relationships

## Current Architecture

**File**: `src/basetype_benchmark/runner/core/param_sampler.py`

### Sampling Flow

```
ParamSampler.sample()
  ├─ _sample_id("Building")      # Random building_id
  ├─ _sample_id("Floor")         # Random floor_id (unrelated to building!)
  ├─ _sample_id("Space")         # Random space_id (unrelated to floor!)
  ├─ _sample_equipment_by_type() # Random equipment
  └─ Returns SampledParams
```

### Problem: Independent Sampling

Each entity type is sampled independently:
- `building_id` from all buildings
- `floor_id` from all floors (not necessarily in the sampled building)
- `space_id` from all spaces (not necessarily on the sampled floor)

This violates the hierarchical relationships in the data model:
```
Building → Floor → Space → Equipment
```

## Proposed Solutions

### Option 1: Correlation Sampling (Recommended)

Sample entities following the hierarchy:

```python
def sample_correlated(self) -> SampledParams:
    # 1. Sample building first
    building_id = self._sample_id("Building")

    # 2. Sample floor WITHIN that building
    floor_id = self._sample_floor_in_building(building_id)

    # 3. Sample space WITHIN that floor
    space_id = self._sample_space_on_floor(floor_id)

    # 4. Sample equipment WITHIN that space (if applicable)
    equipment_id = self._sample_equipment_in_space(space_id)

    return SampledParams(
        building_id=building_id,
        floor_id=floor_id,
        space_id=space_id,
        equipment_id=equipment_id,
    )
```

**Pros**:
- Guarantees valid relationships
- No additional queries at benchmark time

**Cons**:
- More complex sampling queries
- May bias toward densely connected entities

### Option 2: Query-Aware Candidate Sets

Pre-compute valid parameter sets per query:

```python
class QueryAwareSampler:
    def __init__(self, paradigm: str, connection):
        self.candidate_sets = {}

    def _build_candidate_set_q5(self) -> list[dict]:
        """Build valid params for Q5 (equipment in space)."""
        query = """
        SELECT DISTINCT s.id AS space_id, e.id AS equipment_id
        FROM spaces s
        JOIN equipment e ON e.space_id = s.id
        LIMIT 1000
        """
        return self._execute(query)

    def sample_for_query(self, query_id: str) -> dict:
        candidates = self.candidate_sets.get(query_id, [])
        return random.choice(candidates) if candidates else {}
```

**Pros**:
- Guarantees non-empty results
- Query-specific optimization

**Cons**:
- Requires pre-computation phase
- Different candidate sets per paradigm

### Option 3: Re-sampling with Fallback

If a query returns 0 rows, resample and retry:

```python
def execute_with_retry(self, query_id: str, max_retries: int = 3) -> RunResult:
    for attempt in range(max_retries):
        params = self.sampler.sample()
        result = self.execute(query_id, params)

        if result.row_count > 0:
            return result

        # Resample and retry
        self.sampler.reseed()

    return result  # Return last attempt even if 0 rows
```

**Pros**:
- Simple to implement
- Works with existing sampler

**Cons**:
- May not converge for queries with sparse matches
- Biases toward well-connected data
- Adds latency to benchmark

### Option 4: Golden Parameter Sets

Define known-good parameter combinations in configuration:

```yaml
# golden_params.yaml
Q5:
  - space_id: "space_001"
    equipment_id: "eq_hvac_001"
  - space_id: "space_042"
    equipment_id: "eq_lighting_007"
```

**Pros**:
- Deterministic results
- Easy to debug

**Cons**:
- Not truly dynamic
- Requires manual maintenance

## Implementation Roadmap

### Phase 1: Quick Win (Correlation Sampling)

1. Add `_sample_floor_in_building()` method
2. Add `_sample_space_on_floor()` method
3. Add `_sample_equipment_in_space()` method
4. Update `sample()` to use correlated sampling

### Phase 2: Query-Specific (If Needed)

1. Identify queries with persistent 0-row issues
2. Build candidate sets for those queries
3. Add `sample_for_query(query_id)` method

### Phase 3: Validation

1. Run full benchmark suite
2. Track 0-row percentage per query
3. Compare before/after metrics

## Affected Queries

Queries most likely to return 0 rows with independent sampling:

| Query | Parameters | Issue |
|-------|------------|-------|
| Q5 | space_id | Equipment may not exist in random space |
| Q8 | floor_id | May not have sensors |
| Q12 | building_id, tenant_id | Tenant may not be in building |
| Q18 | meter_id | Meter may not have timeseries |

## Testing

```bash
# Run benchmark and track 0-row queries
python run.py  # Benchmark -> P1 -> All queries

# Check results for row_count = 0
grep "row_count: 0" results/*.json
```

## References

- Current sampler: `src/basetype_benchmark/runner/core/param_sampler.py`
- Parameter mapping: `get_params_for_query()` function
- Query catalog: `queries/golden_answers.yaml`
