---
license: cc-by-4.0
language:
  - en
  - fr
tags:
  - smart-building
  - benchmark
  - timeseries
  - graph-database
  - postgresql
  - memgraph
  - sparql
  - building-automation
task_categories:
  - time-series-forecasting
  - graph-ml
size_categories:
  - 100M<n<1B
configs:
  - config_name: default
    data_files:
      - split: graph_nodes
        path: data/graph/nodes.parquet
      - split: graph_edges
        path: data/graph/edges.parquet
      - split: timeseries
        path: data/timeseries/*.parquet
---

# BaseType Benchmark Dataset

Reference dataset for benchmarking database paradigms on smart building data.

## Paper

TBD

## Quick Start

```python
from basetype_benchmark.dataset.huggingface import load_benchmark_data

# Load a specific profile
data = load_benchmark_data(scale="medium", duration="1m")

print(f"Nodes: {len(data['nodes'])}")
print(f"Edges: {len(data['edges'])}")
print(f"Timeseries points: {len(data['timeseries'])}")
```

## Available Profiles

### Scale (Taille du graphe)

| Scale | Description | Points | Buildings |
|-------|-------------|--------|-----------|
| `small` | Single building | ~50k | 1 |
| `medium` | Small campus | ~100k | 5 |
| `large` | Full campus | ~500k | 10+ |

### Duration (Priode temporelle)

| Duration | Description | Days |
|----------|-------------|------|
| `1d` | One day | 1 |
| `1w` | One week | 7 |
| `1m` | One month | 30 |
| `6m` | Six months | 180 |
| `1y` | One year | 365 |

## Dataset Structure

```
data/
 graph/
    nodes.parquet     # ~50k nodes across 9 domains
    edges.parquet     # ~200k relationships
 timeseries/
    2024-01.parquet   # Partitioned by month
    2024-02.parquet
    ...
```

### Domains Covered

1. **Spatial**: Site, Building, Floor, Space, Zone
2. **Equipment**: Systems, Equipment, Sensors, Actuators
3. **Energy**: Meters (tree distribution), EnergyZones
4. **IT/Datacenter**: Servers, Racks, Network devices
5. **Audiovisual**: AV Systems, Displays, Projectors
6. **Parking**: Zones, Spots, Charging stations
7. **Security**: Access points, Cameras, Alarms
8. **Organization**: Departments, Teams, Persons
9. **Contractual**: Contracts, Providers, Work orders

## Schema

### nodes.parquet

| Column | Type | Description |
|--------|------|-------------|
| `node_id` | string | Unique identifier |
| `node_type` | string | Type (Building, Equipment, etc.) |
| `name` | string | Human-readable name |
| `building_id` | int | Building ID for scale filtering (0=cross-building) |
| `properties` | json | Domain-specific attributes |

### edges.parquet

| Column | Type | Description |
|--------|------|-------------|
| `src` | string | Source node ID |
| `dst` | string | Target node ID |
| `rel` | string | Relationship type |

### timeseries/*.parquet

| Column | Type | Description |
|--------|------|-------------|
| `point_id` | string | Reference to Point node |
| `timestamp` | timestamp | Measurement time |
| `value` | float64 | Measured value |
| `building_id` | int | Building ID for scale filtering |
| `year_month` | string | Partition key (YYYY-MM) |

## Scale Filtering

The dataset uses `building_id` for scale-based extraction:
- **small**: `building_id = 1` (single building)
- **medium**: `building_id IN (1,2,3,4,5)` (5 buildings)
- **large**: all buildings (no filter)
- `building_id = 0`: cross-building entities (Site, Organization, etc.)

## Benchmark Usage

```bash
# Run benchmark with specific profile
python -m basetype_benchmark.run --scale=medium --duration=1m

# Results include:
# - Query latencies (p50, p95, min, max)
# - Memory consumption (steady state, peak)
# - CPU usage (average, spikes)
# - Energy estimation (via RAPL/CPU-time)
```

## Author

Antoine Debienne

## Citation

```bibtex
@dataset{basetype_benchmark_2025,
  author = {Antoine Debienne},
  title = {BaseType Benchmark Dataset},
  year = {2025},
  publisher = {Hugging Face},
  url = {https://huggingface.co/datasets/synaptikAD/basetype-benchmark}
}
```

## License

CC-BY-4.0
