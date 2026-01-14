"""Semantic validation for cross-paradigm query comparison.

BaseType Benchmark V3

This module compares the INFORMATION (not the rows) between paradigms.
For the same dataset and the same question, all paradigms must return
the same semantic answer.

Key concepts:
- SemanticAnswer: Normalized representation of a query result
- SemanticNormalizer: Extracts semantic information from raw results
- SemanticValidator: Compares semantic answers between paradigms
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

import yaml

from ..benchmark.results import QueryResult


class SemanticStatus(str, Enum):
    """Status of semantic comparison."""
    EQUIVALENT = "EQUIVALENT"      # Same information
    MISMATCH = "MISMATCH"          # Different information (bug!)
    DEGRADED = "DEGRADED"          # Partial/approximate information (expected)
    IMPOSSIBLE = "IMPOSSIBLE"      # Query impossible for paradigm
    NO_DATA = "NO_DATA"            # No results to compare


AnswerType = Literal["set", "value", "aggregate", "ordered_set", "path", "paths_with_spof", "document"]


@dataclass
class SemanticAnswer:
    """Normalized representation of a query answer.

    This represents the INFORMATION, not the raw rows.
    """
    query_id: str
    answer_type: AnswerType
    data: Any  # The normalized content (set, dict, list, etc.)
    metadata: dict = field(default_factory=dict)  # Non-compared info (depth, etc.)

    def __repr__(self) -> str:
        if self.answer_type == "set":
            return f"SemanticAnswer({self.query_id}, set[{len(self.data)}])"
        elif self.answer_type == "value":
            return f"SemanticAnswer({self.query_id}, value={self.data})"
        else:
            return f"SemanticAnswer({self.query_id}, {self.answer_type})"


@dataclass
class SemanticComparison:
    """Result of comparing two semantic answers."""
    query_id: str
    ref_paradigm: str
    cmp_paradigm: str
    status: SemanticStatus
    reason: str = ""
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "ref_paradigm": self.ref_paradigm,
            "cmp_paradigm": self.cmp_paradigm,
            "status": self.status.value,
            "reason": self.reason,
            "details": self.details,
        }


@dataclass
class QueryDefinition:
    """Semantic definition for a query."""
    query_id: str
    question: str
    answer_type: AnswerType
    semantic_key: str | list[str]
    exclude_parameter: bool = False
    parameter_name: str | None = None
    info_columns: list[str] = field(default_factory=list)
    value_columns: list[str] = field(default_factory=list)
    tolerance: dict = field(default_factory=dict)
    paradigm_status: dict = field(default_factory=dict)
    # For ordered_set
    order_by: str | None = None
    order_direction: str = "desc"
    limit: int | None = None
    rank_tolerance: int = 0
    # For path
    validation: dict = field(default_factory=dict)
    # For document
    structure: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, query_id: str, data: dict) -> "QueryDefinition":
        return cls(
            query_id=query_id,
            question=data.get("question", ""),
            answer_type=data.get("answer_type", "set"),
            semantic_key=data.get("semantic_key", "id"),
            exclude_parameter=data.get("exclude_parameter", False),
            parameter_name=data.get("parameter_name"),
            info_columns=data.get("info_columns", []),
            value_columns=data.get("value_columns", []),
            tolerance=data.get("tolerance", {}),
            paradigm_status=data.get("paradigm_status", {}),
            order_by=data.get("order_by"),
            order_direction=data.get("order_direction", "desc"),
            limit=data.get("limit"),
            rank_tolerance=data.get("rank_tolerance", 0),
            validation=data.get("validation", {}),
            structure=data.get("structure", {}),
        )

    def get_tolerance(self, paradigm: str) -> float:
        """Get tolerance for a paradigm."""
        if isinstance(self.tolerance, dict):
            return self.tolerance.get(paradigm, self.tolerance.get("default", 0.01))
        return 0.01

    def get_paradigm_status(self, paradigm: str) -> tuple[str | None, str | None]:
        """Get status and reason for a paradigm."""
        status_info = self.paradigm_status.get(paradigm, {})
        if isinstance(status_info, dict):
            return status_info.get("status"), status_info.get("reason")
        return None, None


class SemanticNormalizer:
    """Extracts semantic information from query results."""

    # Column name aliases for cross-paradigm normalization
    COLUMN_ALIASES: dict[str, list[str]] = {
        "time_bucket": ["time_bucket", "hour_bucket", "bucket", "hour", "ts"],
        "id": ["id", "node_id", "equipment_id", "eq_id", "n_id"],
        "depth": ["depth", "hop_distance", "distance", "level", "hops"],
        "node_id": ["node_id", "id", "n_id"],
        "point_id": ["point_id", "p_id"],
        "space_id": ["space_id", "s_id"],
    }

    def __init__(self, definitions: dict[str, QueryDefinition]):
        self.definitions = definitions
        # Build reverse lookup: alias -> canonical name
        self._alias_to_canonical: dict[str, str] = {}
        for canonical, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                self._alias_to_canonical[alias] = canonical

    def _get_column_value(self, row: dict, canonical_name: str) -> Any:
        """Get column value using canonical name or any alias."""
        # Try canonical name first
        if canonical_name in row:
            return row[canonical_name]
        # Try aliases
        aliases = self.COLUMN_ALIASES.get(canonical_name, [])
        for alias in aliases:
            if alias in row:
                return row[alias]
        return None

    def normalize(
        self,
        query_id: str,
        result: QueryResult,
        paradigm: str,
        parameters: dict | None = None
    ) -> SemanticAnswer:
        """Normalize a query result to its semantic representation."""
        if query_id not in self.definitions:
            # Fallback: use row_count as answer
            return SemanticAnswer(
                query_id=query_id,
                answer_type="value",
                data=result.row_count if result else 0,
            )

        defn = self.definitions[query_id]
        parameters = parameters or {}

        # Check paradigm status
        status, reason = defn.get_paradigm_status(paradigm)
        if status == "IMPOSSIBLE":
            return SemanticAnswer(
                query_id=query_id,
                answer_type=defn.answer_type,
                data=None,
                metadata={"status": "IMPOSSIBLE", "reason": reason},
            )

        # No result data
        if not result or not result.sample_rows:
            return SemanticAnswer(
                query_id=query_id,
                answer_type=defn.answer_type,
                data=None,
                metadata={"status": "NO_DATA"},
            )

        # Normalize based on answer type
        if defn.answer_type == "set":
            return self._normalize_set(query_id, result, defn, parameters)
        elif defn.answer_type == "value":
            return self._normalize_value(query_id, result, defn)
        elif defn.answer_type == "aggregate":
            return self._normalize_aggregate(query_id, result, defn)
        elif defn.answer_type == "ordered_set":
            return self._normalize_ordered_set(query_id, result, defn, parameters)
        elif defn.answer_type == "path":
            return self._normalize_path(query_id, result, defn)
        elif defn.answer_type == "document":
            return self._normalize_document(query_id, result, defn)
        elif defn.answer_type == "paths_with_spof":
            return self._normalize_paths_with_spof(query_id, result, defn)
        else:
            # Fallback
            return SemanticAnswer(
                query_id=query_id,
                answer_type="set",
                data=set(),
            )

    def _extract_key(self, row: dict, semantic_key: str | list[str]) -> Any:
        """Extract key from row, using column aliases for normalization."""
        if isinstance(semantic_key, list):
            # Composite key (tuple)
            return tuple(self._get_column_value(row, k) for k in semantic_key)
        else:
            return self._get_column_value(row, semantic_key)

    def _normalize_set(
        self,
        query_id: str,
        result: QueryResult,
        defn: QueryDefinition,
        parameters: dict
    ) -> SemanticAnswer:
        """Normalize to a set of IDs."""
        data = set()
        excluded = set()

        # Get parameter value to exclude if configured
        exclude_value = None
        if defn.exclude_parameter and defn.parameter_name:
            exclude_value = parameters.get(defn.parameter_name)

        for row in result.sample_rows:
            key = self._extract_key(row, defn.semantic_key)
            if key is None:
                continue

            # Exclude parameter source if configured
            if exclude_value is not None and key == exclude_value:
                excluded.add(key)
                continue

            data.add(key)

        return SemanticAnswer(
            query_id=query_id,
            answer_type="set",
            data=data,
            metadata={
                "excluded": list(excluded),
                "total_rows": result.row_count,
            },
        )

    def _normalize_value(
        self,
        query_id: str,
        result: QueryResult,
        defn: QueryDefinition
    ) -> SemanticAnswer:
        """Normalize to a single value or dict of values."""
        if not result.sample_rows:
            return SemanticAnswer(query_id=query_id, answer_type="value", data=None)

        row = result.sample_rows[0]

        if isinstance(defn.semantic_key, list):
            # Multiple values
            data = {k: row.get(k) for k in defn.semantic_key}
        else:
            data = row.get(defn.semantic_key)

        return SemanticAnswer(
            query_id=query_id,
            answer_type="value",
            data=data,
        )

    def _normalize_aggregate(
        self,
        query_id: str,
        result: QueryResult,
        defn: QueryDefinition
    ) -> SemanticAnswer:
        """Normalize to a dict of key -> values."""
        data = {}

        for row in result.sample_rows:
            key = self._extract_key(row, defn.semantic_key)
            if key is None:
                continue

            # Use column aliases for value extraction
            values = {col: self._get_column_value(row, col) for col in defn.value_columns}
            data[key] = values

        return SemanticAnswer(
            query_id=query_id,
            answer_type="aggregate",
            data=data,
        )

    def _normalize_ordered_set(
        self,
        query_id: str,
        result: QueryResult,
        defn: QueryDefinition,
        parameters: dict
    ) -> SemanticAnswer:
        """Normalize to an ordered list (for top-N queries)."""
        items = []

        for row in result.sample_rows:
            key = self._extract_key(row, defn.semantic_key)
            if key is None:
                continue

            order_value = row.get(defn.order_by) if defn.order_by else None
            items.append((key, order_value))

        # Sort by order value
        reverse = defn.order_direction == "desc"
        items.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=reverse)

        # Apply limit
        if defn.limit:
            items = items[:defn.limit]

        return SemanticAnswer(
            query_id=query_id,
            answer_type="ordered_set",
            data=items,
            metadata={
                "order_by": defn.order_by,
                "limit": defn.limit,
                "rank_tolerance": defn.rank_tolerance,
            },
        )

    def _normalize_path(
        self,
        query_id: str,
        result: QueryResult,
        defn: QueryDefinition
    ) -> SemanticAnswer:
        """Normalize to a path (list of node IDs)."""
        # Extract path nodes in order
        path_nodes = []

        # Sort by path_index if available
        rows = sorted(result.sample_rows, key=lambda r: r.get("path_index", 0))

        for row in rows:
            node_id = row.get("node_id") or row.get("id")
            if node_id:
                path_nodes.append(node_id)

        return SemanticAnswer(
            query_id=query_id,
            answer_type="path",
            data=path_nodes,
            metadata={
                "length": len(path_nodes),
                "validation": defn.validation,
            },
        )

    def _normalize_document(
        self,
        query_id: str,
        result: QueryResult,
        defn: QueryDefinition
    ) -> SemanticAnswer:
        """Normalize to a document structure."""
        if not result.sample_rows:
            return SemanticAnswer(query_id=query_id, answer_type="document", data=None)

        # For document type, use first row or aggregate
        row = result.sample_rows[0]

        # Extract required fields
        data = {}
        structure = defn.structure

        for field_name in structure.get("required", []):
            data[field_name] = row.get(field_name)

        for field_name in structure.get("optional", []):
            if field_name in row:
                data[field_name] = row.get(field_name)

        return SemanticAnswer(
            query_id=query_id,
            answer_type="document",
            data=data,
        )

    def _normalize_paths_with_spof(
        self,
        query_id: str,
        result: QueryResult,
        defn: QueryDefinition
    ) -> SemanticAnswer:
        """Normalize paths with SPOF detection."""
        paths = []
        spof_nodes = set()

        # Group by path_id
        paths_by_id = {}
        for row in result.sample_rows:
            path_id = row.get("path_id", 0)
            if path_id not in paths_by_id:
                paths_by_id[path_id] = []

            path_nodes = row.get("path_nodes", [])
            if path_nodes:
                paths_by_id[path_id] = path_nodes

            # Collect SPOF nodes if present
            spof = row.get("spof_nodes", [])
            if spof:
                spof_nodes.update(spof)

        paths = list(paths_by_id.values())

        return SemanticAnswer(
            query_id=query_id,
            answer_type="paths_with_spof",
            data={
                "paths": paths,
                "spof_nodes": spof_nodes,
            },
        )


class SemanticValidator:
    """Compares semantic answers between paradigms."""

    def __init__(self, definitions_path: Path | None = None):
        self.definitions: dict[str, QueryDefinition] = {}
        self.global_config: dict = {}

        if definitions_path and definitions_path.exists():
            self._load_definitions(definitions_path)

        self.normalizer = SemanticNormalizer(self.definitions)

    def _load_definitions(self, path: Path) -> None:
        """Load definitions from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.global_config = data.get("global", {})

        for query_id, query_data in data.get("queries", {}).items():
            self.definitions[query_id] = QueryDefinition.from_dict(query_id, query_data)

    def validate(
        self,
        query_id: str,
        ref_result: QueryResult | None,
        ref_paradigm: str,
        cmp_result: QueryResult | None,
        cmp_paradigm: str,
        parameters: dict | None = None
    ) -> SemanticComparison:
        """Compare semantic answers between two paradigms."""
        parameters = parameters or {}

        # Check paradigm status
        if query_id in self.definitions:
            defn = self.definitions[query_id]

            ref_status, ref_reason = defn.get_paradigm_status(ref_paradigm)
            cmp_status, cmp_reason = defn.get_paradigm_status(cmp_paradigm)

            if ref_status == "IMPOSSIBLE":
                return SemanticComparison(
                    query_id=query_id,
                    ref_paradigm=ref_paradigm,
                    cmp_paradigm=cmp_paradigm,
                    status=SemanticStatus.IMPOSSIBLE,
                    reason=f"{ref_paradigm}: {ref_reason}",
                )

            if cmp_status == "IMPOSSIBLE":
                return SemanticComparison(
                    query_id=query_id,
                    ref_paradigm=ref_paradigm,
                    cmp_paradigm=cmp_paradigm,
                    status=SemanticStatus.IMPOSSIBLE,
                    reason=f"{cmp_paradigm}: {cmp_reason}",
                )

        # Normalize both results
        ref_answer = self.normalizer.normalize(query_id, ref_result, ref_paradigm, parameters)
        cmp_answer = self.normalizer.normalize(query_id, cmp_result, cmp_paradigm, parameters)

        # Check for NO_DATA
        if ref_answer.data is None and cmp_answer.data is None:
            return SemanticComparison(
                query_id=query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.NO_DATA,
                reason="No data in either paradigm",
            )

        if ref_answer.data is None:
            return SemanticComparison(
                query_id=query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.NO_DATA,
                reason=f"No data in reference ({ref_paradigm})",
            )

        if cmp_answer.data is None:
            return SemanticComparison(
                query_id=query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.NO_DATA,
                reason=f"No data in compared ({cmp_paradigm})",
            )

        # Compare based on answer type
        return self._compare(ref_answer, cmp_answer, ref_paradigm, cmp_paradigm)

    def _compare(
        self,
        ref: SemanticAnswer,
        cmp: SemanticAnswer,
        ref_paradigm: str,
        cmp_paradigm: str
    ) -> SemanticComparison:
        """Compare two semantic answers."""
        if ref.answer_type != cmp.answer_type:
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.MISMATCH,
                reason=f"Answer type mismatch: {ref.answer_type} vs {cmp.answer_type}",
            )

        if ref.answer_type == "set":
            return self._compare_sets(ref, cmp, ref_paradigm, cmp_paradigm)
        elif ref.answer_type == "value":
            return self._compare_values(ref, cmp, ref_paradigm, cmp_paradigm)
        elif ref.answer_type == "aggregate":
            return self._compare_aggregates(ref, cmp, ref_paradigm, cmp_paradigm)
        elif ref.answer_type == "ordered_set":
            return self._compare_ordered_sets(ref, cmp, ref_paradigm, cmp_paradigm)
        elif ref.answer_type == "path":
            return self._compare_paths(ref, cmp, ref_paradigm, cmp_paradigm)
        elif ref.answer_type == "document":
            return self._compare_documents(ref, cmp, ref_paradigm, cmp_paradigm)
        elif ref.answer_type == "paths_with_spof":
            return self._compare_paths_with_spof(ref, cmp, ref_paradigm, cmp_paradigm)
        else:
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.MISMATCH,
                reason=f"Unknown answer type: {ref.answer_type}",
            )

    def _compare_sets(
        self,
        ref: SemanticAnswer,
        cmp: SemanticAnswer,
        ref_paradigm: str,
        cmp_paradigm: str
    ) -> SemanticComparison:
        """Compare two sets."""
        ref_set = ref.data if isinstance(ref.data, set) else set(ref.data)
        cmp_set = cmp.data if isinstance(cmp.data, set) else set(cmp.data)

        if ref_set == cmp_set:
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.EQUIVALENT,
                reason=f"Identical sets ({len(ref_set)} items)",
                details={"count": len(ref_set)},
            )

        common = ref_set & cmp_set
        only_ref = ref_set - cmp_set
        only_cmp = cmp_set - ref_set

        return SemanticComparison(
            query_id=ref.query_id,
            ref_paradigm=ref_paradigm,
            cmp_paradigm=cmp_paradigm,
            status=SemanticStatus.MISMATCH,
            reason=f"Set difference: {len(only_ref)} only in {ref_paradigm}, {len(only_cmp)} only in {cmp_paradigm}",
            details={
                "common": len(common),
                "only_in_ref": list(only_ref)[:10],  # Limit to 10
                "only_in_cmp": list(only_cmp)[:10],
            },
        )

    def _compare_values(
        self,
        ref: SemanticAnswer,
        cmp: SemanticAnswer,
        ref_paradigm: str,
        cmp_paradigm: str
    ) -> SemanticComparison:
        """Compare single values or dict of values."""
        defn = self.definitions.get(ref.query_id)
        tolerance = defn.get_tolerance(cmp_paradigm) if defn else 0.01

        if isinstance(ref.data, dict) and isinstance(cmp.data, dict):
            # Compare dict values
            mismatches = []
            for key in ref.data:
                ref_val = ref.data.get(key)
                cmp_val = cmp.data.get(key)
                if not self._values_match(ref_val, cmp_val, tolerance):
                    mismatches.append({
                        "key": key,
                        "ref": ref_val,
                        "cmp": cmp_val,
                    })

            if not mismatches:
                return SemanticComparison(
                    query_id=ref.query_id,
                    ref_paradigm=ref_paradigm,
                    cmp_paradigm=cmp_paradigm,
                    status=SemanticStatus.EQUIVALENT,
                    reason="All values match within tolerance",
                )

            # Check if DEGRADED
            cmp_status, _ = defn.get_paradigm_status(cmp_paradigm) if defn else (None, None)
            if cmp_status == "DEGRADED":
                return SemanticComparison(
                    query_id=ref.query_id,
                    ref_paradigm=ref_paradigm,
                    cmp_paradigm=cmp_paradigm,
                    status=SemanticStatus.DEGRADED,
                    reason=f"Values differ but {cmp_paradigm} is DEGRADED",
                    details={"mismatches": mismatches},
                )

            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.MISMATCH,
                reason="Value mismatch",
                details={"mismatches": mismatches},
            )
        else:
            # Single value comparison
            if self._values_match(ref.data, cmp.data, tolerance):
                return SemanticComparison(
                    query_id=ref.query_id,
                    ref_paradigm=ref_paradigm,
                    cmp_paradigm=cmp_paradigm,
                    status=SemanticStatus.EQUIVALENT,
                    reason=f"Values match: {ref.data}",
                )

            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.MISMATCH,
                reason=f"Value mismatch: {ref.data} vs {cmp.data}",
            )

    def _compare_aggregates(
        self,
        ref: SemanticAnswer,
        cmp: SemanticAnswer,
        ref_paradigm: str,
        cmp_paradigm: str
    ) -> SemanticComparison:
        """Compare aggregate results (key -> values)."""
        defn = self.definitions.get(ref.query_id)
        tolerance = defn.get_tolerance(cmp_paradigm) if defn else 0.01

        ref_keys = set(ref.data.keys())
        cmp_keys = set(cmp.data.keys())

        if ref_keys != cmp_keys:
            only_ref = ref_keys - cmp_keys
            only_cmp = cmp_keys - ref_keys
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.MISMATCH,
                reason=f"Key mismatch: {len(only_ref)} only in {ref_paradigm}, {len(only_cmp)} only in {cmp_paradigm}",
                details={
                    "only_in_ref": list(only_ref)[:10],
                    "only_in_cmp": list(only_cmp)[:10],
                },
            )

        # Compare values for each key
        mismatches = []
        for key in ref_keys:
            ref_vals = ref.data[key]
            cmp_vals = cmp.data[key]

            for col in ref_vals:
                if not self._values_match(ref_vals.get(col), cmp_vals.get(col), tolerance):
                    mismatches.append({
                        "key": key,
                        "column": col,
                        "ref": ref_vals.get(col),
                        "cmp": cmp_vals.get(col),
                    })

        if not mismatches:
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.EQUIVALENT,
                reason=f"All aggregates match ({len(ref_keys)} keys)",
            )

        return SemanticComparison(
            query_id=ref.query_id,
            ref_paradigm=ref_paradigm,
            cmp_paradigm=cmp_paradigm,
            status=SemanticStatus.MISMATCH,
            reason=f"{len(mismatches)} aggregate value mismatches",
            details={"mismatches": mismatches[:10]},
        )

    def _compare_ordered_sets(
        self,
        ref: SemanticAnswer,
        cmp: SemanticAnswer,
        ref_paradigm: str,
        cmp_paradigm: str
    ) -> SemanticComparison:
        """Compare ordered sets (top-N with rank tolerance)."""
        defn = self.definitions.get(ref.query_id)
        rank_tolerance = ref.metadata.get("rank_tolerance", 0)

        ref_items = [item[0] for item in ref.data]
        cmp_items = [item[0] for item in cmp.data]

        # Check if same items (ignoring order)
        ref_set = set(ref_items)
        cmp_set = set(cmp_items)

        if ref_set != cmp_set:
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.MISMATCH,
                reason="Different items in top-N",
                details={
                    "only_in_ref": list(ref_set - cmp_set),
                    "only_in_cmp": list(cmp_set - ref_set),
                },
            )

        # Check order with tolerance
        rank_diff = 0
        for i, item in enumerate(ref_items):
            if item in cmp_items:
                cmp_rank = cmp_items.index(item)
                rank_diff = max(rank_diff, abs(i - cmp_rank))

        if rank_diff <= rank_tolerance:
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.EQUIVALENT,
                reason=f"Same items, rank diff {rank_diff} within tolerance {rank_tolerance}",
            )

        return SemanticComparison(
            query_id=ref.query_id,
            ref_paradigm=ref_paradigm,
            cmp_paradigm=cmp_paradigm,
            status=SemanticStatus.MISMATCH,
            reason=f"Rank diff {rank_diff} exceeds tolerance {rank_tolerance}",
        )

    def _compare_paths(
        self,
        ref: SemanticAnswer,
        cmp: SemanticAnswer,
        ref_paradigm: str,
        cmp_paradigm: str
    ) -> SemanticComparison:
        """Compare paths."""
        ref_path = ref.data
        cmp_path = cmp.data
        validation = ref.metadata.get("validation", {})

        issues = []

        # Check length
        if validation.get("same_length", True) and len(ref_path) != len(cmp_path):
            issues.append(f"Length: {len(ref_path)} vs {len(cmp_path)}")

        # Check start
        if validation.get("same_start", True) and ref_path and cmp_path:
            if ref_path[0] != cmp_path[0]:
                issues.append(f"Start: {ref_path[0]} vs {cmp_path[0]}")

        # Check end
        if validation.get("same_end", True) and ref_path and cmp_path:
            if ref_path[-1] != cmp_path[-1]:
                issues.append(f"End: {ref_path[-1]} vs {cmp_path[-1]}")

        # Check intermediates (optional)
        if validation.get("same_intermediates", False):
            if ref_path != cmp_path:
                issues.append("Path nodes differ")

        if not issues:
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.EQUIVALENT,
                reason=f"Valid path of length {len(ref_path)}",
            )

        return SemanticComparison(
            query_id=ref.query_id,
            ref_paradigm=ref_paradigm,
            cmp_paradigm=cmp_paradigm,
            status=SemanticStatus.MISMATCH,
            reason="; ".join(issues),
        )

    def _compare_documents(
        self,
        ref: SemanticAnswer,
        cmp: SemanticAnswer,
        ref_paradigm: str,
        cmp_paradigm: str
    ) -> SemanticComparison:
        """Compare document structures."""
        defn = self.definitions.get(ref.query_id)
        structure = defn.structure if defn else {}

        # Compare required fields
        mismatches = []
        for field_name in structure.get("required", []):
            ref_val = ref.data.get(field_name) if ref.data else None
            cmp_val = cmp.data.get(field_name) if cmp.data else None
            if ref_val != cmp_val:
                mismatches.append({
                    "field": field_name,
                    "ref": ref_val,
                    "cmp": cmp_val,
                })

        if not mismatches:
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.EQUIVALENT,
                reason="Document structures match",
            )

        return SemanticComparison(
            query_id=ref.query_id,
            ref_paradigm=ref_paradigm,
            cmp_paradigm=cmp_paradigm,
            status=SemanticStatus.MISMATCH,
            reason=f"{len(mismatches)} field mismatches",
            details={"mismatches": mismatches},
        )

    def _compare_paths_with_spof(
        self,
        ref: SemanticAnswer,
        cmp: SemanticAnswer,
        ref_paradigm: str,
        cmp_paradigm: str
    ) -> SemanticComparison:
        """Compare paths with SPOF detection."""
        ref_spof = ref.data.get("spof_nodes", set())
        cmp_spof = cmp.data.get("spof_nodes", set())

        if ref_spof == cmp_spof:
            return SemanticComparison(
                query_id=ref.query_id,
                ref_paradigm=ref_paradigm,
                cmp_paradigm=cmp_paradigm,
                status=SemanticStatus.EQUIVALENT,
                reason=f"Same SPOF nodes: {ref_spof}",
            )

        return SemanticComparison(
            query_id=ref.query_id,
            ref_paradigm=ref_paradigm,
            cmp_paradigm=cmp_paradigm,
            status=SemanticStatus.MISMATCH,
            reason=f"SPOF mismatch: {ref_spof} vs {cmp_spof}",
        )

    def _values_match(self, ref_val: Any, cmp_val: Any, tolerance: float) -> bool:
        """Check if two values match with tolerance for floats."""
        if ref_val is None and cmp_val is None:
            return True

        if ref_val is None or cmp_val is None:
            return False

        # Float comparison with tolerance
        if isinstance(ref_val, (int, float)) and isinstance(cmp_val, (int, float)):
            if ref_val == 0 and cmp_val == 0:
                return True
            if ref_val == 0:
                return abs(cmp_val) < tolerance
            if math.isnan(ref_val) or math.isnan(cmp_val):
                return math.isnan(ref_val) and math.isnan(cmp_val)
            rel_diff = abs(ref_val - cmp_val) / abs(ref_val)
            return rel_diff <= tolerance

        # Default: exact match
        return ref_val == cmp_val


def validate_semantically(
    results_path: Path,
    definitions_path: Path,
    reference: str = "P1",
) -> dict:
    """Convenience function to run semantic validation on results.

    Args:
        results_path: Path to benchmark results JSON
        definitions_path: Path to semantic definitions YAML
        reference: Reference paradigm

    Returns:
        dict with validation summary
    """
    from ..benchmark.results import BenchmarkResults

    results = BenchmarkResults.from_json(results_path)
    validator = SemanticValidator(definitions_path)

    summary = {
        "reference": reference,
        "paradigms": [],
        "queries": {},
        "totals": {
            "equivalent": 0,
            "mismatch": 0,
            "degraded": 0,
            "impossible": 0,
            "no_data": 0,
        },
    }

    paradigms = list(results.results.keys())
    summary["paradigms"] = paradigms

    # Get query IDs
    query_ids = set()
    for paradigm in results.results.values():
        for level in paradigm.levels:
            if level.status == "success":
                query_ids.update(level.queries.keys())
                break

    for query_id in sorted(query_ids):
        summary["queries"][query_id] = {}

        for cmp_paradigm in paradigms:
            if cmp_paradigm == reference:
                continue

            # Get results
            ref_result = None
            cmp_result = None

            for level in results.results[reference].levels:
                if level.status == "success" and query_id in level.queries:
                    ref_result = level.queries[query_id]
                    break

            for level in results.results[cmp_paradigm].levels:
                if level.status == "success" and query_id in level.queries:
                    cmp_result = level.queries[query_id]
                    break

            # Validate
            comparison = validator.validate(
                query_id, ref_result, reference,
                cmp_result, cmp_paradigm
            )

            summary["queries"][query_id][cmp_paradigm] = comparison.to_dict()
            summary["totals"][comparison.status.value.lower()] += 1

    return summary
