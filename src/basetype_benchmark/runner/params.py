"""Query parameter management for benchmark execution.

This module handles:
- Extracting available IDs from loaded datasets (floors, buildings, equipment, etc.)
- Generating deterministic query variants with different parameter values
- Substituting $PARAM placeholders in query text
"""

import csv
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


# Query parameters by query ID
QUERY_PARAMS = {
    "Q1": ["meter_id"],
    "Q2": ["equipment_id"],
    "Q3": ["space_id"],
    "Q4": ["floor_id"],
    "Q5": [],  # No parameters
    "Q6": ["building_id", "date_start", "date_end"],
    "Q7": ["building_id", "date_start", "date_end"],
    "Q8": ["tenant_id", "date_start", "date_end"],
    "Q9": ["tenant_id", "date_start", "date_end"],
    "Q10": ["building_id"],
    "Q11": ["building_id"],
    "Q12": ["building_id", "date_start", "date_end"],
    "Q13": ["building_id", "space_type", "date_start", "date_end"],
}


def extract_dataset_info(nodes_csv: Path, scenario: str = "P1") -> Dict[str, List[str]]:
    """Extract available IDs from dataset for query parameterization.

    Reads the nodes CSV file to extract meters, equipment, spaces, floors, etc.
    for generating query variants with realistic parameters.

    Args:
        nodes_csv: Path to the nodes CSV file (pg_nodes.csv, mg_nodes.csv, etc.)
        scenario: Scenario code (P1, P2, M1, M2, O1, O2)

    Returns:
        Dict with lists of IDs by type:
        {
            "meters": ["meter_001", ...],
            "equipment": ["eq_001", ...],
            "spaces": ["space_001", ...],
            "floors": ["floor_001", ...],
            "buildings": ["bldg_001", ...],
            "tenants": ["tenant_001", ...],
            "points": ["point_001", ...],
            "ts_start": 1704067200,  # Unix timestamp
            "ts_end": 1704153600,
        }
    """
    info: Dict[str, List[str]] = {
        "meters": [],
        "equipment": [],
        "spaces": [],
        "floors": [],
        "buildings": [],
        "tenants": [],
        "points": [],
        "zones": [],
    }

    if not nodes_csv.exists():
        print(f"  [WARN] Nodes file not found: {nodes_csv}")
        return info

    try:
        with open(nodes_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_type = row.get("type", "")
                node_id = row.get("id", "")
                equipment_type = row.get("equipment_type", "")

                if not node_id:
                    continue

                if node_type == "Meter":
                    info["meters"].append(node_id)
                elif node_type == "Equipment":
                    info["equipment"].append(node_id)
                    # Also detect meters from equipment_type (MainMeter, SubMeter)
                    if equipment_type in ("MainMeter", "SubMeter"):
                        info["meters"].append(node_id)
                elif node_type == "Space":
                    info["spaces"].append(node_id)
                elif node_type == "Floor":
                    info["floors"].append(node_id)
                elif node_type == "Building":
                    info["buildings"].append(node_id)
                elif node_type == "Tenant":
                    info["tenants"].append(node_id)
                elif node_type == "Point":
                    info["points"].append(node_id)
                elif node_type == "Zone":
                    info["zones"].append(node_id)

    except Exception as e:
        print(f"  [WARN] Failed to read nodes file: {e}")

    # Log extraction stats
    counts = {k: len(v) for k, v in info.items() if isinstance(v, list) and v}
    if counts:
        print(f"  [INFO] Dataset IDs: {counts}")

    return info


def extract_dataset_info_from_parquet(nodes_parquet: Path) -> Dict[str, List[str]]:
    """Extract available IDs from Parquet nodes file.

    This is used for scenarios that don't have a convenient nodes CSV (e.g., O1/O2),
    while still keeping parameter generation deterministic and reproducible.
    """
    info: Dict[str, List[str]] = {
        "meters": [],
        "equipment": [],
        "spaces": [],
        "floors": [],
        "buildings": [],
        "tenants": [],
        "points": [],
        "zones": [],
    }

    if not nodes_parquet.exists():
        print(f"  [WARN] Nodes parquet not found: {nodes_parquet}")
        return info

    try:
        import pandas as pd

        # nodes.parquet schema can vary by exporter version; only request columns that exist.
        probe = pd.read_parquet(nodes_parquet, columns=["id", "type"])  # minimal
        available_cols = set(probe.columns)
        # Try to include building_id / equipment_type / properties if present
        cols = ["id", "type"]
        for c in ("building_id", "equipment_type", "properties"):
            try:
                df_col = pd.read_parquet(nodes_parquet, columns=[c])
                available_cols.update(df_col.columns)
                cols.append(c)
            except Exception:
                pass

        # De-duplicate while preserving order
        cols = list(dict.fromkeys(cols))
        df = pd.read_parquet(nodes_parquet, columns=cols)

        for node_type, group in df.groupby("type"):
            ids = group["id"].dropna().astype(str).tolist()
            if node_type == "Meter":
                info["meters"].extend(ids)
            elif node_type == "Equipment":
                info["equipment"].extend(ids)
                if "equipment_type" in group.columns:
                    meters_from_eq = group[group["equipment_type"].isin(["MainMeter", "SubMeter"])]["id"].dropna().astype(str).tolist()
                    info["meters"].extend(meters_from_eq)
                elif "properties" in group.columns:
                    # Parse equipment_type from JSON properties for a small equipment set
                    try:
                        try:
                            import orjson as _json  # type: ignore
                            _loads = _json.loads
                        except Exception:
                            import json as _json
                            _loads = _json.loads

                        meters_from_props: List[str] = []
                        for _, row in group[["id", "properties"]].iterrows():
                            raw = row.get("properties")
                            if not raw:
                                continue
                            try:
                                props = _loads(raw) if isinstance(raw, str) else raw
                                et = props.get("equipment_type") if isinstance(props, dict) else None
                                if et in ("MainMeter", "SubMeter"):
                                    meters_from_props.append(str(row["id"]))
                            except Exception:
                                continue
                        info["meters"].extend(meters_from_props)
                    except Exception:
                        pass
            elif node_type == "Space":
                info["spaces"].extend(ids)
            elif node_type == "Floor":
                info["floors"].extend(ids)
            elif node_type == "Building":
                info["buildings"].extend(ids)
            elif node_type == "Tenant":
                info["tenants"].extend(ids)
            elif node_type == "Point":
                info["points"].extend(ids)
            elif node_type == "Zone":
                info["zones"].extend(ids)
    except Exception as e:
        print(f"  [WARN] Failed to read nodes.parquet: {e}")
        return info

    counts = {k: len(v) for k, v in info.items() if isinstance(v, list) and v}
    if counts:
        print(f"  [INFO] Dataset IDs (parquet): {counts}")

    return info


def extract_timeseries_range_from_parquet(ts_parquet: Path) -> Dict[str, int]:
    """Extract timestamp range from timeseries.parquet metadata when possible."""
    result = {"ts_start": 0, "ts_end": 0}
    if not ts_parquet.exists():
        return result

    try:
        import pyarrow.parquet as pq

        pf = pq.ParquetFile(ts_parquet)
        # Try to find stats for timestamp column
        min_ts = None
        max_ts = None

        schema = pf.schema_arrow
        # column can be timestamp or time depending on exporter version
        ts_col = None
        for name in ("timestamp", "time"):
            if name in schema.names:
                ts_col = name
                break
        if ts_col is None:
            return result

        col_idx = schema.get_field_index(ts_col)
        if col_idx < 0:
            return result

        for rg in range(pf.metadata.num_row_groups):
            col = pf.metadata.row_group(rg).column(col_idx)
            stats = col.statistics
            if stats is None:
                continue
            if stats.min is not None:
                min_ts = stats.min if min_ts is None else min(min_ts, stats.min)
            if stats.max is not None:
                max_ts = stats.max if max_ts is None else max(max_ts, stats.max)

        # stats.min/max can be datetime-like or int; normalize via datetime
        def _to_unix(x) -> Optional[int]:
            try:
                if hasattr(x, "timestamp"):
                    return int(x.timestamp())
                return int(x)
            except Exception:
                return None

        if min_ts is not None:
            v = _to_unix(min_ts)
            if v is not None:
                result["ts_start"] = v
        if max_ts is not None:
            v = _to_unix(max_ts)
            if v is not None:
                result["ts_end"] = v
    except Exception as e:
        print(f"  [WARN] Failed to read timeseries.parquet range: {e}")

    return result


def extract_timeseries_range(ts_csv: Path) -> Dict[str, int]:
    """Extract timestamp range from timeseries CSV.

    Args:
        ts_csv: Path to timeseries.csv

    Returns:
        Dict with ts_start and ts_end as Unix timestamps
    """
    result = {"ts_start": 0, "ts_end": 0}

    if not ts_csv.exists():
        return result

    try:
        # Read first and last lines to get time range (assumes sorted by time)
        with open(ts_csv, "r", encoding="utf-8") as f:
            header = f.readline()
            first_line = f.readline()

            # Seek to end and read backwards for last line
            f.seek(0, 2)  # End of file
            file_size = f.tell()

            # Read last chunk
            chunk_size = min(1024, file_size)
            f.seek(file_size - chunk_size)
            last_chunk = f.read()
            lines = last_chunk.strip().split('\n')
            last_line = lines[-1] if lines else ""

        # Parse timestamps (format: point_id,time,value)
        if first_line:
            parts = first_line.strip().split(',')
            if len(parts) >= 2:
                try:
                    ts = datetime.fromisoformat(parts[1].replace('Z', '+00:00'))
                    result["ts_start"] = int(ts.timestamp())
                except:
                    pass

        if last_line and ',' in last_line:
            parts = last_line.strip().split(',')
            if len(parts) >= 2:
                try:
                    ts = datetime.fromisoformat(parts[1].replace('Z', '+00:00'))
                    result["ts_end"] = int(ts.timestamp())
                except:
                    pass

    except Exception as e:
        print(f"  [WARN] Failed to read timeseries range: {e}")

    return result


def get_query_variants(
    query_id: str,
    profile: str,
    dataset_info: Dict,
    seed: int = 42,
    scenario: str = "P1",
    n_variants: int = None,
) -> List[Dict]:
    """Generate parameter variants for a query (deterministic).

    Args:
        query_id: Q1, Q2, etc.
        profile: small-2d, medium-1w, etc. (used for default n_variants if not specified)
        dataset_info: Dict from extract_dataset_info()
        seed: Random seed for reproducibility
        scenario: P1, P2, M1, M2, O1, O2 (affects date format)
        n_variants: Number of variants to generate (overrides profile default)

    Returns:
        List of dicts, each containing parameter values for one variant
    """
    params = QUERY_PARAMS.get(query_id, [])
    if not params:
        return [{}]  # No parameters needed

    # Determine number of variants from profile if not specified
    if n_variants is None:
        scale = profile.split("-")[0] if "-" in profile else profile
        n_variants = {"small": 3, "medium": 5, "large": 10}.get(scale, 3)

    # Determine date format based on scenario
    # SQL (P1, P2): ISO format
    # Cypher (M1, M2): Unix timestamp
    # SPARQL (O1, O2): xsd:date format
    scenario_upper = scenario.upper()
    if scenario_upper in ("M1", "M2"):
        date_format = "unix"
    elif scenario_upper in ("O1", "O2"):
        date_format = "xsd_date"
    else:
        date_format = "iso"

    # Get timestamp range
    ts_start = dataset_info.get("ts_start", 0)
    ts_end = dataset_info.get("ts_end", 0)

    # Default to reasonable range if not found
    if ts_end == 0:
        ts_end = int(datetime.now(timezone.utc).timestamp())
    if ts_start == 0:
        ts_start = ts_end - 7 * 86400  # 7 days back

    rng = random.Random(seed)
    variants = []

    for i in range(n_variants):
        variant = {}

        for param in params:
            if param == "meter_id":
                meters = dataset_info.get("meters", [])
                variant[param] = rng.choice(meters) if meters else "meter_default"

            elif param == "equipment_id":
                equipment = dataset_info.get("equipment", [])
                variant[param] = rng.choice(equipment) if equipment else "eq_default"

            elif param == "space_id":
                spaces = dataset_info.get("spaces", [])
                variant[param] = rng.choice(spaces) if spaces else "space_default"

            elif param == "floor_id":
                floors = dataset_info.get("floors", [])
                variant[param] = rng.choice(floors) if floors else "floor_default"

            elif param == "building_id":
                buildings = dataset_info.get("buildings", [])
                variant[param] = rng.choice(buildings) if buildings else "bldg_default"

            elif param == "tenant_id":
                tenants = dataset_info.get("tenants", [])
                variant[param] = rng.choice(tenants) if tenants else "tenant_default"

            elif param == "zone_id":
                zones = dataset_info.get("zones", [])
                variant[param] = rng.choice(zones) if zones else "zone_default"

            elif param == "point_id":
                points = dataset_info.get("points", [])
                variant[param] = rng.choice(points) if points else "point_default"

            elif param == "space_type":
                space_types = ["office_open", "office_closed", "meeting_large", "conference"]
                variant[param] = rng.choice(space_types)

            elif param == "date_start":
                # Calculate available data range
                data_duration_days = (ts_end - ts_start) / 86400 if ts_end > ts_start else 2

                # Adapt window to available data
                # For analytics queries (Q7, Q12, Q13), use smaller windows to avoid full scans
                # Q7: drift detection needs enough samples but not full dataset
                # Q12: dashboard analytics, 1 day is typical
                # Q6: aggregation query, 1 day typical
                if query_id == "Q7":
                    # For drift detection: use 6-12 hours (enough samples, not full scan)
                    ideal_window_hours = 12 if data_duration_days <= 2 else 24 * 7
                    ideal_window = ideal_window_hours / 24
                elif query_id in ["Q6", "Q12", "Q13"]:
                    # For dashboard queries: use 6 hours for small datasets
                    ideal_window_hours = 6 if data_duration_days <= 2 else 24
                    ideal_window = ideal_window_hours / 24
                else:
                    ideal_window = 30  # Default for other queries
                    
                window_days = min(ideal_window, max(0.25, data_duration_days - 0.1))

                # Sliding offset: divide available range by n_variants
                max_offset = max(0, data_duration_days - window_days)
                offset_days = (max_offset / max(1, n_variants - 1)) * i if n_variants > 1 else 0

                ts = ts_start + offset_days * 86400

                if date_format == "unix":
                    variant[param] = int(ts)
                elif date_format == "xsd_date":
                    variant[param] = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                else:  # iso
                    variant[param] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

            elif param == "date_end":
                # Calculate available data range
                data_duration_days = (ts_end - ts_start) / 86400 if ts_end > ts_start else 2

                ideal_window = 7 if query_id in ["Q7"] else 1 if query_id in ["Q6", "Q12"] else 30
                window_days = min(ideal_window, max(1, data_duration_days - 0.5))

                max_offset = max(0, data_duration_days - window_days)
                offset_days = (max_offset / max(1, n_variants - 1)) * i if n_variants > 1 else 0

                ts = ts_start + (offset_days + window_days) * 86400

                if date_format == "unix":
                    variant[param] = int(ts)
                elif date_format == "xsd_date":
                    variant[param] = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                else:  # iso
                    variant[param] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

        variants.append(variant)

    return variants


def substitute_params(query_text: str, params: Dict) -> str:
    """Substitute $PARAM placeholders in query text.

    Args:
        query_text: Query with $PARAM placeholders
        params: Dict of param_name -> value

    Returns:
        Query with substituted values
    """
    result = query_text
    for key, value in params.items():
        placeholder = f"${key.upper()}"
        # Also try lowercase
        placeholder_lower = f"${key.lower()}"

        str_value = str(value)
        result = result.replace(placeholder, str_value)
        result = result.replace(placeholder_lower, str_value)

    return result


def get_nodes_csv_path(export_dir: Path, scenario: str) -> Path:
    """Get the path to nodes CSV for a scenario.

    Args:
        export_dir: Export directory
        scenario: P1, P2, M1, M2, O1, O2

    Returns:
        Path to nodes CSV file
    """
    scenario = scenario.upper()
    scenario_dir = export_dir / scenario.lower()

    if scenario == "P1":
        return scenario_dir / "pg_nodes.csv"
    elif scenario == "P2":
        return scenario_dir / "pg_jsonb_nodes.csv"
    elif scenario in ("M1", "M2"):
        return scenario_dir / "mg_nodes.csv"
    elif scenario in ("O1", "O2"):
        # O1/O2 use N-Triples; prefer P1 nodes CSV if present (for easy ID extraction)
        p1_dir = export_dir / "p1"
        if (p1_dir / "pg_nodes.csv").exists():
            return p1_dir / "pg_nodes.csv"
        # Otherwise return a non-existent path; caller should fall back to parquet extraction.
        return scenario_dir / "pg_nodes.csv"
    else:
        return scenario_dir / "pg_nodes.csv"
