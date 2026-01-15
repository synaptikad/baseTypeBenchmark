"""Full result normalizer for cross-paradigm validation.

Normalizes paradigm-specific results to a canonical form for comparison:
1. Map column names to canonical names (id vs n.id vs equipment_id)
2. Extract semantic content based on query type (set, value, aggregate...)
3. Compute content hash for fast comparison
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .models import NormalizedResult, SemanticType, compute_content_hash


# Regex to detect PostgreSQL timestamp formats:
# "2024-01-15 00:00:00+00" or "2024-01-15 00:00:00" (with space instead of T)
_POSTGRES_TIMESTAMP_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})(\+\d{2})?$"
)


def normalize_timestamp(value: Any) -> Any:
    """Normalize timestamp to ISO format for consistent comparison.

    Handles PostgreSQL time_bucket format differences:
    - Expected (Python isoformat): "2024-01-15T00:00:00"
    - PostgreSQL time_bucket:      "2024-01-15 00:00:00+00"

    Args:
        value: Value to normalize (may be string timestamp or other)

    Returns:
        ISO-formatted timestamp string if input is a timestamp, otherwise original value
    """
    if not isinstance(value, str):
        return value

    # Check for PostgreSQL timestamp format (space instead of T, optional timezone)
    match = _POSTGRES_TIMESTAMP_RE.match(value)
    if match:
        date_part = match.group(1)
        time_part = match.group(2)
        # Return ISO format without timezone (matches Python isoformat())
        return f"{date_part}T{time_part}"

    return value


# Default column mappings: canonical -> variants
DEFAULT_COLUMN_MAPPINGS = {
    "id": ["id", "node_id", "n.id", "equipment_id", "eq.id", "e.id", "n_id"],
    "type": ["type", "node_type", "n.type", "equipment_type", "labels(n)[0]", "n_type"],
    "name": ["name", "node_name", "n.name", "equipment_name", "n_name"],
    "depth": ["depth", "hop_distance", "distance", "level", "hops"],
    "point_id": ["point_id", "p.id", "sensor_id", "p_id"],
    "space_id": ["space_id", "s.id", "room_id", "s_id"],
    "equipment_id": ["equipment_id", "eq.id", "e.id", "eq_id"],
    "sibling_id": ["sibling_id", "sib.id", "sibling_node_id"],
    "parent_id": ["parent_id", "parent.id", "p_id"],
    "time_bucket": ["time_bucket", "hour", "bucket", "time", "ts"],
    "avg_value": ["avg_value", "avg", "mean", "average"],
    "min_value": ["min_value", "min", "minimum"],
    "max_value": ["max_value", "max", "maximum"],
    "variance": ["variance", "var", "stddev_squared"],
    "sample_count": ["sample_count", "count", "n", "cnt"],
    "total_energy_kwh": ["total_energy_kwh", "total_energy", "energy_kwh", "sum_energy"],
    "carbon_kg_co2": ["carbon_kg_co2", "carbon_kg", "co2_kg"],
}


class FullResultNormalizer:
    """Normalize full paradigm results to canonical form."""

    def __init__(
        self,
        definitions_path: Path | None = None,
        column_mappings: dict[str, list[str]] | None = None,
    ):
        """Initialize normalizer.

        Args:
            definitions_path: Path to semantic_definitions.yaml
            column_mappings: Custom column mappings (canonical -> variants)
        """
        self.column_mappings = column_mappings or DEFAULT_COLUMN_MAPPINGS
        self.definitions: dict[str, Any] = {}

        if definitions_path and Path(definitions_path).exists():
            with open(definitions_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.definitions = data.get("queries", {})

    def normalize(
        self,
        rows: list[dict],
        query_id: str,
        paradigm: str,
        parameters: dict[str, Any],
    ) -> NormalizedResult:
        """Normalize paradigm results to canonical form.

        Args:
            rows: All result rows from paradigm
            query_id: Query ID (Q1, Q2, etc.)
            paradigm: Paradigm name (P1, P2, M1, M2)
            parameters: Query parameters used

        Returns:
            NormalizedResult with semantic content and hash
        """
        if not rows:
            return NormalizedResult(
                semantic_type="empty",
                semantic_content=set(),
                row_count=0,
                content_hash=compute_content_hash(set()),
                canonical_rows=[],
            )

        # 1. Map column names to canonical
        canonical_rows = self._canonicalize_columns(rows)

        # 2. Get query definition
        query_def = self.definitions.get(query_id, {})
        answer_type = query_def.get("answer_type", "set")

        # 3. Extract semantic content
        semantic_content = self._extract_semantic(
            canonical_rows, query_def, query_id, parameters
        )

        # 4. Compute hash
        content_hash = compute_content_hash(semantic_content)

        return NormalizedResult(
            semantic_type=answer_type,
            semantic_content=semantic_content,
            row_count=len(rows),
            content_hash=content_hash,
            canonical_rows=canonical_rows,
        )

    def _canonicalize_columns(self, rows: list[dict]) -> list[dict]:
        """Map column names to canonical names.

        Args:
            rows: Original rows with paradigm-specific columns

        Returns:
            Rows with canonical column names
        """
        if not rows:
            return []

        # Build reverse mapping: variant -> canonical
        variant_to_canonical = {}
        for canonical, variants in self.column_mappings.items():
            for variant in variants:
                # Case-insensitive matching
                variant_to_canonical[variant.lower()] = canonical

        # Detect which mappings apply to this result set
        sample = rows[0]
        column_map = {}
        for col in sample.keys():
            col_lower = col.lower()
            if col_lower in variant_to_canonical:
                column_map[col] = variant_to_canonical[col_lower]
            else:
                column_map[col] = col  # Keep original

        # Apply mapping to all rows
        return [
            {column_map.get(k, k): v for k, v in row.items()}
            for row in rows
        ]

    def _extract_semantic(
        self,
        rows: list[dict],
        query_def: dict[str, Any],
        query_id: str,
        parameters: dict[str, Any],
    ) -> Any:
        """Extract semantic content based on query type.

        Args:
            rows: Canonical rows
            query_def: Query definition from yaml
            query_id: Query ID
            parameters: Query parameters

        Returns:
            Semantic content (set, dict, list, value)
        """
        answer_type = query_def.get("answer_type", "set")
        semantic_key = query_def.get("semantic_key", "id")

        if answer_type == "set":
            return self._extract_set(rows, semantic_key, query_def, parameters)
        elif answer_type == "value":
            return self._extract_value(rows, semantic_key, query_def)
        elif answer_type == "aggregate":
            return self._extract_aggregate(rows, semantic_key, query_def)
        elif answer_type == "ordered_set":
            return self._extract_ordered_set(rows, semantic_key, query_def)
        elif answer_type == "path":
            return self._extract_path(rows, query_def)
        elif answer_type == "document":
            return self._extract_document(rows, query_def)
        else:
            # Default: extract as set of IDs
            return self._extract_set(rows, "id", {}, {})

    def _extract_set(
        self,
        rows: list[dict],
        semantic_key: str | list,
        query_def: dict[str, Any],
        parameters: dict[str, Any],
    ) -> set:
        """Extract unordered set of IDs.

        Args:
            rows: Canonical rows
            semantic_key: Column(s) to extract
            query_def: Query definition
            parameters: Query parameters

        Returns:
            Set of IDs or tuples
        """
        result = set()

        # Value to exclude (source parameter)
        exclude_value = None
        if query_def.get("exclude_parameter"):
            param_name = query_def.get("parameter_name")
            if param_name:
                exclude_value = parameters.get(param_name)

        for row in rows:
            # Extract key (simple or composite)
            if isinstance(semantic_key, list):
                key = tuple(self._get_value(row, k) for k in semantic_key)
            else:
                key = self._get_value(row, semantic_key)

            # Exclude source parameter if configured
            if exclude_value is not None and key == exclude_value:
                continue

            if key is not None:
                result.add(key)

        return result

    def _extract_value(
        self,
        rows: list[dict],
        semantic_key: str | list,
        query_def: dict[str, Any],
    ) -> dict[str, Any] | Any:
        """Extract single value or value dict.

        Args:
            rows: Canonical rows (usually 1 row for value queries)
            semantic_key: Column(s) to extract
            query_def: Query definition

        Returns:
            Single value or dict of values
        """
        if not rows:
            return None

        row = rows[0]

        if isinstance(semantic_key, list):
            # Multiple values -> dict
            return {
                k: self._round_if_float(self._get_value(row, k))
                for k in semantic_key
            }
        else:
            return self._round_if_float(self._get_value(row, semantic_key))

    def _extract_aggregate(
        self,
        rows: list[dict],
        semantic_key: str | list,
        query_def: dict[str, Any],
    ) -> dict[Any, dict]:
        """Extract aggregate results keyed by grouping.

        Args:
            rows: Canonical rows
            semantic_key: Grouping column(s)
            query_def: Query definition

        Returns:
            Dict mapping key -> value dict
        """
        value_columns = query_def.get("value_columns", [])

        result = {}
        for row in rows:
            # Extract key
            if isinstance(semantic_key, list):
                key = tuple(
                    normalize_timestamp(self._get_value(row, k))
                    for k in semantic_key
                )
            else:
                key = self._get_value(row, semantic_key)
                # Normalize timestamp format (PostgreSQL vs ISO)
                key = normalize_timestamp(key)
                # Convert to string for JSON compatibility
                key = str(key) if key is not None else None

            # Extract values
            values = {}
            for col in value_columns:
                val = self._get_value(row, col)
                values[col] = self._round_if_float(val)

            if key is not None:
                result[key] = values

        return result

    def _extract_ordered_set(
        self,
        rows: list[dict],
        semantic_key: str,
        query_def: dict[str, Any],
    ) -> list:
        """Extract ordered list of IDs (Top-N).

        Args:
            rows: Canonical rows (already ordered)
            semantic_key: ID column
            query_def: Query definition

        Returns:
            Ordered list of IDs
        """
        return [self._get_value(row, semantic_key) for row in rows]

    def _extract_path(
        self,
        rows: list[dict],
        query_def: dict[str, Any],
    ) -> list[list]:
        """Extract graph path(s).

        Args:
            rows: Canonical rows with path data
            query_def: Query definition

        Returns:
            List of paths, each path is list of node IDs
        """
        paths = []
        current_path = []
        current_path_idx = None

        for row in rows:
            path_idx = row.get("path_index", 0)
            node_id = row.get("id") or row.get("node_id")

            if path_idx != current_path_idx:
                if current_path:
                    paths.append(current_path)
                current_path = []
                current_path_idx = path_idx

            if node_id:
                current_path.append(node_id)

        if current_path:
            paths.append(current_path)

        return paths

    def _extract_document(
        self,
        rows: list[dict],
        query_def: dict[str, Any],
    ) -> dict:
        """Extract document (nested JSON).

        Args:
            rows: Canonical rows (usually 1 row)
            query_def: Query definition with structure

        Returns:
            Document dict
        """
        if not rows:
            return {}

        # For documents, return the first row as-is
        # The structure validation is done separately
        doc = dict(rows[0])

        # If single column contains nested document (JSONB), extract it
        # This handles P2/M2 queries that return jsonb_build_object(...) AS digital_twin
        if len(doc) == 1:
            single_value = list(doc.values())[0]
            if isinstance(single_value, dict):
                return single_value

        return doc

    def _get_value(self, row: dict, key: str) -> Any:
        """Get value from row, handling nested keys.

        Args:
            row: Row dict
            key: Column name (may be nested like 'a.b')

        Returns:
            Value or None
        """
        if "." in key and key not in row:
            # Try nested access
            parts = key.split(".")
            val = row
            for part in parts:
                if isinstance(val, dict):
                    val = val.get(part)
                else:
                    return None
            return val

        return row.get(key)

    def _round_if_float(self, value: Any, decimals: int = 4) -> Any:
        """Round float values for consistent comparison.

        Args:
            value: Value to potentially round
            decimals: Number of decimal places

        Returns:
            Rounded value if float, original otherwise
        """
        if isinstance(value, float):
            return round(value, decimals)
        return value


def load_normalizer(
    definitions_path: Path | None = None,
) -> FullResultNormalizer:
    """Load normalizer with semantic definitions.

    Args:
        definitions_path: Path to semantic_definitions.yaml

    Returns:
        Configured FullResultNormalizer
    """
    if definitions_path is None:
        # Try default location
        default_path = Path(__file__).parent.parent.parent.parent.parent / "config" / "semantic_definitions.yaml"
        if default_path.exists():
            definitions_path = default_path

    return FullResultNormalizer(definitions_path=definitions_path)


class ParquetNormalizer:
    """Normalize Parquet archive results to JSON format matching Expected Answers.

    This class bridges the gap between:
    - Benchmark results stored in Parquet (compact, efficient)
    - Expected Answers stored in JSON (ground truth from generator)

    The normalization pipeline:
    1. Load Parquet rows from archive
    2. Canonicalize column names (paradigm-specific -> canonical)
    3. Extract semantic content based on query answer_type
    4. Produce JSON comparable to expected_answers/

    Usage:
        normalizer = ParquetNormalizer(archive_path, definitions_path)
        normalized = normalizer.normalize_paradigm("P1")
        # normalized["Q1"] = {"semantic_content": {...}, "row_count": 343, ...}
    """

    def __init__(
        self,
        archive_path: Path,
        definitions_path: Path | None = None,
        rules_path: Path | None = None,
    ):
        """Initialize Parquet normalizer.

        Args:
            archive_path: Path to benchmark archive (contains raw_results/)
            definitions_path: Path to semantic_definitions.yaml
            rules_path: Path to validation_rules.yaml (for IMPOSSIBLE queries)
        """
        self.archive_path = Path(archive_path)
        self.raw_results_path = self.archive_path / "raw_results"

        # Load FullResultNormalizer for semantic extraction
        self._normalizer = load_normalizer(definitions_path)

        # Load validation rules (IMPOSSIBLE queries)
        self.rules: dict[str, Any] = {}
        if rules_path and Path(rules_path).exists():
            with open(rules_path, "r", encoding="utf-8") as f:
                self.rules = yaml.safe_load(f) or {}

    def get_paradigms(self) -> list[str]:
        """Get list of paradigms in archive."""
        if not self.raw_results_path.exists():
            return []
        return sorted([p.name for p in self.raw_results_path.iterdir() if p.is_dir()])

    def get_queries(self, paradigm: str) -> list[str]:
        """Get list of queries for a paradigm."""
        paradigm_dir = self.raw_results_path / paradigm
        if not paradigm_dir.exists():
            return []

        queries = set()
        # Parquet files (new format)
        for f in paradigm_dir.glob("*.parquet"):
            queries.add(f.stem)
        # JSON files (legacy, exclude .meta.json)
        for f in paradigm_dir.glob("*.json"):
            if not f.name.endswith(".meta.json"):
                queries.add(f.stem)

        return sorted(queries, key=lambda x: (x[0], int(x[1:]) if x[1:].isdigit() else 999))

    def is_impossible(self, query_id: str, paradigm: str) -> str | None:
        """Check if query is IMPOSSIBLE for paradigm.

        Returns:
            Reason string if impossible, None otherwise
        """
        impossible = self.rules.get("impossible", {})
        paradigm_impossible = impossible.get(paradigm, {})
        return paradigm_impossible.get(query_id)

    def load_query_rows(self, query_id: str, paradigm: str) -> tuple[list[dict], dict]:
        """Load rows and metadata for a query.

        Supports both Parquet (new) and JSON (legacy) formats.

        Args:
            query_id: Query ID (Q1, Q2, etc.)
            paradigm: Paradigm (P1, P2, M1, M2)

        Returns:
            (rows, metadata) tuple
        """
        import pyarrow.parquet as pq

        paradigm_dir = self.raw_results_path / paradigm

        # Try Parquet format first
        parquet_path = paradigm_dir / f"{query_id}.parquet"
        meta_path = paradigm_dir / f"{query_id}.meta.json"

        if parquet_path.exists():
            table = pq.read_table(parquet_path)
            rows = table.to_pylist()

            metadata = {}
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

            return rows, metadata

        # Fall back to legacy JSON
        json_path = paradigm_dir / f"{query_id}.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("rows", []), data

        return [], {}

    def normalize_query(
        self,
        query_id: str,
        paradigm: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Normalize a single query result to Expected Answer format.

        Args:
            query_id: Query ID
            paradigm: Paradigm
            parameters: Query parameters (from metadata or expected answers)

        Returns:
            Dict matching ExpectedAnswer format:
            {
                "query_id": "Q1",
                "paradigm": "P1",
                "answer_type": "set",
                "semantic_content": [...],
                "row_count": 343,
                "content_hash": "abc123...",
                "status": "NORMALIZED" | "IMPOSSIBLE" | "MISSING"
            }
        """
        # Check if IMPOSSIBLE
        impossible_reason = self.is_impossible(query_id, paradigm)
        if impossible_reason:
            return {
                "query_id": query_id,
                "paradigm": paradigm,
                "status": "IMPOSSIBLE",
                "reason": impossible_reason,
                "semantic_content": None,
                "row_count": 0,
                "content_hash": "",
            }

        # Load rows
        rows, metadata = self.load_query_rows(query_id, paradigm)

        if not rows and not metadata:
            return {
                "query_id": query_id,
                "paradigm": paradigm,
                "status": "MISSING",
                "reason": "No result file found",
                "semantic_content": None,
                "row_count": 0,
                "content_hash": "",
            }

        # Get parameters from metadata if not provided
        if parameters is None:
            parameters = metadata.get("parameters", {})

        # Normalize using FullResultNormalizer
        normalized = self._normalizer.normalize(rows, query_id, paradigm, parameters)

        # Convert semantic_content to JSON-serializable format
        semantic_content = normalized.semantic_content
        if isinstance(semantic_content, (set, frozenset)):
            semantic_content = sorted(list(semantic_content), key=str)

        return {
            "query_id": query_id,
            "paradigm": paradigm,
            "status": "NORMALIZED",
            "answer_type": normalized.semantic_type,
            "semantic_content": semantic_content,
            "row_count": normalized.row_count,
            "content_hash": normalized.content_hash,
            "parameters": parameters,
        }

    def normalize_paradigm(
        self,
        paradigm: str,
        query_ids: list[str] | None = None,
        parameters_store: Any | None = None,
    ) -> dict[str, dict]:
        """Normalize all queries for a paradigm.

        Args:
            paradigm: Paradigm to normalize
            query_ids: Optional list of query IDs to process (default: all)
            parameters_store: Optional ExpectedAnswerStore for parameters

        Returns:
            Dict mapping query_id -> normalized result
        """
        if query_ids is None:
            query_ids = self.get_queries(paradigm)

        results = {}
        for qid in query_ids:
            # Get parameters from store if available
            params = None
            if parameters_store:
                params = parameters_store.get_query_parameters(qid)

            results[qid] = self.normalize_query(qid, paradigm, params)

        return results

    def normalize_all(
        self,
        paradigms: list[str] | None = None,
        query_ids: list[str] | None = None,
        parameters_store: Any | None = None,
    ) -> dict[str, dict[str, dict]]:
        """Normalize all paradigms and queries.

        Args:
            paradigms: Optional list of paradigms (default: all)
            query_ids: Optional list of query IDs (default: all)
            parameters_store: Optional ExpectedAnswerStore for parameters

        Returns:
            Dict mapping paradigm -> query_id -> normalized result
        """
        if paradigms is None:
            paradigms = self.get_paradigms()

        results = {}
        for paradigm in paradigms:
            results[paradigm] = self.normalize_paradigm(
                paradigm, query_ids, parameters_store
            )

        return results

    def save_normalized(
        self,
        output_dir: Path,
        paradigms: list[str] | None = None,
        query_ids: list[str] | None = None,
        parameters_store: Any | None = None,
    ) -> Path:
        """Normalize and save results to JSON files.

        Creates:
            output_dir/
            ├── P1/
            │   ├── Q1.json
            │   ├── Q2.json
            │   └── ...
            ├── M1/
            │   └── ...
            └── summary.json

        Args:
            output_dir: Output directory
            paradigms: Optional list of paradigms
            query_ids: Optional list of query IDs
            parameters_store: Optional ExpectedAnswerStore for parameters

        Returns:
            Path to output directory
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        all_results = self.normalize_all(paradigms, query_ids, parameters_store)

        summary = {
            "archive": str(self.archive_path),
            "paradigms": {},
        }

        for paradigm, queries in all_results.items():
            paradigm_dir = output_dir / paradigm
            paradigm_dir.mkdir(exist_ok=True)

            paradigm_summary = {"total": 0, "normalized": 0, "impossible": 0, "missing": 0}

            for query_id, result in queries.items():
                # Save individual query result
                query_path = paradigm_dir / f"{query_id}.json"
                with open(query_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, default=str)

                # Update summary
                paradigm_summary["total"] += 1
                status = result.get("status", "MISSING")
                if status == "NORMALIZED":
                    paradigm_summary["normalized"] += 1
                elif status == "IMPOSSIBLE":
                    paradigm_summary["impossible"] += 1
                else:
                    paradigm_summary["missing"] += 1

            summary["paradigms"][paradigm] = paradigm_summary

        # Save summary
        summary_path = output_dir / "summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return output_dir
