"""
Intgration HuggingFace pour publication et chargement du dataset.

Ce module permet de:
- Publier le dataset de rfrence sur HuggingFace Hub
- Charger des sous-ensembles par scale (small/medium/large) et dure (1d/1w/1m/6m/1y)
- Extraire dynamiquement partir du dataset de rfrence

Prrequis:
    pip install huggingface_hub datasets pyarrow

Configuration:
    export HF_TOKEN=hf_xxxxx  # Token avec permissions write
    huggingface-cli login     # Alternative interactive
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterator, List, Literal, Optional, Union

try:
    from huggingface_hub import HfApi, create_repo, upload_folder, hf_hub_download
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_REPO_ID = "synaptikad/basetype-benchmark"
"""Repo HuggingFace par dfaut pour le dataset."""

ScaleType = Literal["small", "medium", "large"]
DurationType = Literal["1d", "1w", "1m", "6m", "1y"]

# Mapping scale -> building_ids pour le filtrage
# small = building 1 seulement, medium = buildings 1-5, large = tous
SCALE_BUILDINGS: Dict[ScaleType, Optional[List[int]]] = {
    "small": [1],
    "medium": [1, 2, 3, 4, 5],
    "large": None,  # Pas de filtre = tous les buildings
}

# Conversion durée -> jours
DURATION_DAYS: Dict[DurationType, int] = {
    "1d": 1,
    "1w": 7,
    "1m": 30,
    "6m": 180,
    "1y": 365,
}


# =============================================================================
# Publication
# =============================================================================

def publish_dataset(
    local_path: Path,
    repo_id: str = DEFAULT_REPO_ID,
    token: Optional[str] = None,
    private: bool = False,
    commit_message: str = "Update dataset",
) -> str:
    """
    Publie le dataset sur HuggingFace Hub.

    Args:
        local_path: Chemin vers le dossier contenant les parquet
        repo_id: ID du repo HuggingFace (user/dataset-name)
        token: Token HF (ou variable HF_TOKEN)
        private: Dataset priv ou public
        commit_message: Message de commit

    Returns:
        URL du dataset publi

    Raises:
        ImportError: Si huggingface_hub n'est pas install
        ValueError: Si le chemin n'existe pas
    """
    if not HF_AVAILABLE:
        raise ImportError(
            "huggingface_hub n'est pas install. "
            "Installez avec: pip install huggingface_hub"
        )

    local_path = Path(local_path)
    if not local_path.exists():
        raise ValueError(f"Le chemin {local_path} n'existe pas")

    token = token or os.environ.get("HF_TOKEN")
    api = HfApi(token=token)

    # Crer le repo si n'existe pas
    create_repo(
        repo_id=repo_id,
        repo_type="dataset",
        private=private,
        exist_ok=True,
        token=token,
    )

    # Upload avec LFS pour les gros fichiers
    api.upload_folder(
        folder_path=str(local_path),
        repo_id=repo_id,
        repo_type="dataset",
        commit_message=commit_message,
        token=token,
    )

    return f"https://huggingface.co/datasets/{repo_id}"


# =============================================================================
# Chargement avec filtrage
# =============================================================================

def load_benchmark_data(
    scale: ScaleType = "small",
    duration: DurationType = "1m",
    repo_id: str = DEFAULT_REPO_ID,
    cache_dir: Optional[Path] = None,
    streaming: bool = False,
) -> Dict[str, Any]:
    """
    Charge un sous-ensemble du dataset selon scale et duration.

    Le dataset de rfrence (large-1y) est tlcharg et filtr
    dynamiquement pour extraire le profil demand.

    Args:
        scale: Taille du graphe (small/medium/large)
        duration: Priode temporelle (1d/1w/1m/6m/1y)
        repo_id: ID du repo HuggingFace
        cache_dir: Rpertoire de cache local
        streaming: Mode streaming pour gros volumes (non support)

    Returns:
        Dict avec 'nodes', 'edges', 'timeseries' (listes de dicts)

    Example:
        >>> data = load_benchmark_data(scale="medium", duration="1m")
        >>> print(f"Nodes: {len(data['nodes'])}")
    """
    if not HF_AVAILABLE:
        raise ImportError("huggingface_hub n'est pas install")
    if not PYARROW_AVAILABLE:
        raise ImportError("pyarrow n'est pas install")

    if streaming:
        raise NotImplementedError("Le mode streaming n'est pas encore support")

    building_ids = SCALE_BUILDINGS[scale]
    duration_days = DURATION_DAYS[duration]

    # Télécharger les fichiers depuis HuggingFace
    api = HfApi()

    # Charger les nodes
    nodes_path = hf_hub_download(
        repo_id=repo_id,
        filename="data/graph/nodes.parquet",
        repo_type="dataset",
        cache_dir=cache_dir,
    )
    nodes_table = pq.read_table(nodes_path)

    # Filtrer par building_id
    nodes_filtered = _filter_by_building_id(nodes_table, building_ids)

    # Charger les edges
    edges_path = hf_hub_download(
        repo_id=repo_id,
        filename="data/graph/edges.parquet",
        repo_type="dataset",
        cache_dir=cache_dir,
    )
    edges_table = pq.read_table(edges_path)

    # Filtrer les edges pour ne garder que ceux entre nodes valides
    valid_node_ids = set(nodes_filtered.column("node_id").to_pylist())
    edges_filtered = _filter_edges_by_nodes(edges_table, valid_node_ids)

    # Charger et filtrer les timeseries
    timeseries_data = _load_timeseries_filtered(
        repo_id=repo_id,
        building_ids=building_ids,
        duration_days=duration_days,
        cache_dir=cache_dir,
    )

    return {
        "nodes": nodes_filtered.to_pylist(),
        "edges": edges_filtered.to_pylist(),
        "timeseries": timeseries_data,
    }


def _filter_by_building_id(table: pa.Table, building_ids: Optional[List[int]]) -> pa.Table:
    """Filtre une table Parquet par building_id.

    Args:
        table: Table Parquet à filtrer
        building_ids: Liste des building_ids à inclure, ou None pour tout garder

    Returns:
        Table filtrée
    """
    if building_ids is None:
        return table  # Pas de filtre = tous les buildings

    if "building_id" not in table.schema.names:
        return table  # Pas de colonne building_id, retourner tout

    # Inclure building_id 0 (entités cross-buildings comme Site, Organization, etc.)
    allowed = building_ids + [0]
    mask = pa.compute.is_in(table.column("building_id"), pa.array(allowed))
    return table.filter(mask)


def _filter_edges_by_nodes(edges_table: pa.Table, valid_node_ids: set) -> pa.Table:
    """Filtre les edges pour ne garder que ceux entre nodes valides."""
    src_col = edges_table.column("src").to_pylist()
    dst_col = edges_table.column("dst").to_pylist()

    mask = [
        src in valid_node_ids and dst in valid_node_ids
        for src, dst in zip(src_col, dst_col)
    ]
    return edges_table.filter(pa.array(mask))


def _load_timeseries_filtered(
    repo_id: str,
    building_ids: Optional[List[int]],
    duration_days: int,
    cache_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Charge les timeseries filtrées par building_id et durée."""
    api = HfApi()

    # Calculer la date de début
    cutoff_date = datetime.now() - timedelta(days=duration_days)
    cutoff_str = cutoff_date.strftime("%Y-%m")

    # Lister les fichiers timeseries disponibles
    try:
        files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
    except Exception:
        return []

    ts_files = [f for f in files if f.startswith("data/timeseries/") and f.endswith(".parquet")]

    # Filtrer par date (format: data/timeseries/2024-01.parquet)
    filtered_files = []
    for f in ts_files:
        # Extraire le mois du nom de fichier
        basename = Path(f).stem  # ex: "2024-01"
        if basename >= cutoff_str:
            filtered_files.append(f)

    # Charger et fusionner
    all_data = []
    for ts_file in filtered_files:
        try:
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=ts_file,
                repo_type="dataset",
                cache_dir=cache_dir,
            )
            table = pq.read_table(local_path)
            filtered = _filter_by_building_id(table, building_ids)
            all_data.extend(filtered.to_pylist())
        except Exception:
            continue

    return all_data


# =============================================================================
# Export vers Parquet (avec building_id)
# =============================================================================

def export_to_parquet(
    nodes: List[Dict],
    edges: List[Dict],
    timeseries: List[Dict],
    output_dir: Path,
    partition_by_month: bool = True,
) -> Path:
    """
    Exporte le dataset en format Parquet pour HuggingFace.

    Args:
        nodes: Liste des noeuds (avec scale_tier)
        edges: Liste des relations
        timeseries: Liste des points timeseries
        output_dir: Rpertoire de sortie
        partition_by_month: Si True, partitionne les timeseries par mois

    Returns:
        Chemin vers le rpertoire d'export
    """
    if not PYARROW_AVAILABLE:
        raise ImportError("pyarrow n'est pas install")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export nodes
    graph_dir = output_dir / "data" / "graph"
    graph_dir.mkdir(parents=True, exist_ok=True)

    nodes_table = pa.Table.from_pylist(nodes)
    pq.write_table(nodes_table, graph_dir / "nodes.parquet", compression="snappy")

    # Export edges
    edges_table = pa.Table.from_pylist(edges)
    pq.write_table(edges_table, graph_dir / "edges.parquet", compression="snappy")

    # Export timeseries
    ts_dir = output_dir / "data" / "timeseries"
    ts_dir.mkdir(parents=True, exist_ok=True)

    if partition_by_month and timeseries:
        _export_timeseries_partitioned(timeseries, ts_dir)
    elif timeseries:
        ts_table = pa.Table.from_pylist(timeseries)
        pq.write_table(ts_table, ts_dir / "all.parquet", compression="snappy")

    return output_dir


def _export_timeseries_partitioned(timeseries: List[Dict], output_dir: Path) -> None:
    """Exporte les timeseries partitionnes par mois."""
    from collections import defaultdict

    # Grouper par mois
    by_month: Dict[str, List[Dict]] = defaultdict(list)

    for ts in timeseries:
        timestamp = ts.get("timestamp")
        if timestamp:
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp)
            else:
                dt = timestamp
            month_key = dt.strftime("%Y-%m")
            ts_copy = dict(ts)
            ts_copy["year_month"] = month_key
            by_month[month_key].append(ts_copy)

    # crire chaque partition
    for month, data in by_month.items():
        table = pa.Table.from_pylist(data)
        pq.write_table(
            table,
            output_dir / f"{month}.parquet",
            compression="snappy"
        )


# =============================================================================
# Gnration du README (Dataset Card)
# =============================================================================

def generate_dataset_card(
    output_path: Path,
    repo_id: str = DEFAULT_REPO_ID,
    zenodo_doi: Optional[str] = None,
    author_name: str = "Antoine Debienne",
    author_orcid: Optional[str] = None,
) -> None:
    """
    Génère le README.md (Dataset Card) pour HuggingFace.

    Args:
        output_path: Chemin de sortie
        repo_id: ID du repo HuggingFace
        zenodo_doi: DOI Zenodo de l'article associé
        author_name: Nom de l'auteur
        author_orcid: ORCID de l'auteur (ex: "0000-0002-1234-5678")
    """
    zenodo_link = f"[{zenodo_doi}](https://doi.org/{zenodo_doi})" if zenodo_doi else "TBD"
    orcid_link = f"[{author_orcid}](https://orcid.org/{author_orcid})" if author_orcid else ""
    author_line = f"{author_name}" + (f" ({orcid_link})" if orcid_link else "")

    card_content = f'''---
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

{zenodo_link}

## Quick Start

```python
from basetype_benchmark.dataset.huggingface import load_benchmark_data

# Load a specific profile
data = load_benchmark_data(scale="medium", duration="1m")

print(f"Nodes: {{len(data['nodes'])}}")
print(f"Edges: {{len(data['edges'])}}")
print(f"Timeseries points: {{len(data['timeseries'])}}")
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

{author_line}

## Citation

```bibtex
@dataset{{basetype_benchmark_2025,
  author = {{{author_name}}},
  title = {{BaseType Benchmark Dataset}},
  year = {{2025}},
  publisher = {{Hugging Face}},
  url = {{https://huggingface.co/datasets/{repo_id}}}
}}
```

## License

CC-BY-4.0
'''

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(card_content, encoding="utf-8")


# =============================================================================
# Utilitaires
# =============================================================================

def check_dependencies() -> Dict[str, bool]:
    """Vrifie les dpendances requises."""
    return {
        "huggingface_hub": HF_AVAILABLE,
        "pyarrow": PYARROW_AVAILABLE,
    }


def get_dataset_info(repo_id: str = DEFAULT_REPO_ID) -> Dict[str, Any]:
    """Rcupre les informations sur le dataset HuggingFace."""
    if not HF_AVAILABLE:
        raise ImportError("huggingface_hub n'est pas install")

    api = HfApi()
    try:
        info = api.dataset_info(repo_id=repo_id)
        return {
            "id": info.id,
            "sha": info.sha,
            "downloads": info.downloads,
            "tags": info.tags,
            "created_at": str(info.created_at) if info.created_at else None,
            "last_modified": str(info.last_modified) if info.last_modified else None,
        }
    except Exception as e:
        return {"error": str(e)}
