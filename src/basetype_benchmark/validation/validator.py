"""Validation engine for cross-paradigm correctness.

Two validators:
1. AnswerValidator: Validates paradigm results against Expected Answers (Q1-Q23)
2. ComparativeValidator: Validates write queries by comparing between paradigms (QW*)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .models import (
    ExpectedAnswer,
    NormalizedResult,
    SemanticType,
    ValidationResult,
    ValidationStatus,
)
from .expected_store import ExpectedAnswerStore
from .normalizer import FullResultNormalizer


@dataclass
class ValidationRules:
    """Validation rules loaded from YAML config."""

    impossible: dict[str, dict[str, str]] = field(default_factory=dict)
    degraded: dict[str, dict[str, str]] = field(default_factory=dict)
    tolerance: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: Path) -> "ValidationRules":
        """Load rules from YAML file."""
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(
            impossible=data.get("impossible", {}),
            degraded=data.get("degraded", {}),
            tolerance=data.get("tolerance", {}),
        )

    def is_impossible(self, query_id: str, paradigm: str) -> bool:
        """Check if query is impossible for paradigm."""
        return query_id in self.impossible.get(paradigm, {})

    def is_degraded(self, query_id: str, paradigm: str) -> bool:
        """Check if query is expected to be degraded for paradigm."""
        return query_id in self.degraded.get(paradigm, {})

    def get_reason(self, query_id: str, paradigm: str) -> str:
        """Get reason for impossible/degraded status."""
        if query_id in self.impossible.get(paradigm, {}):
            return self.impossible[paradigm][query_id]
        if query_id in self.degraded.get(paradigm, {}):
            return self.degraded[paradigm][query_id]
        return ""

    def get_tolerance(self, query_id: str, paradigm: str) -> float:
        """Get numeric tolerance for comparison."""
        # Check paradigm-specific tolerance
        paradigm_key = f"{paradigm}_{query_id}"
        if paradigm_key in self.tolerance.get("float", {}):
            return self.tolerance["float"][paradigm_key]

        # Check paradigm default
        if paradigm in self.tolerance.get("float", {}):
            return self.tolerance["float"][paradigm]

        # Global default
        return self.tolerance.get("float", {}).get("default", 0.01)


class AnswerValidator:
    """Validate paradigm results against Expected Answers."""

    def __init__(
        self,
        expected_store: ExpectedAnswerStore,
        definitions_path: Path | None = None,
        rules_path: Path | None = None,
    ):
        """Initialize validator.

        Args:
            expected_store: Store with Expected Answers
            definitions_path: Path to semantic_definitions.yaml
            rules_path: Path to validation_rules.yaml
        """
        self.expected_store = expected_store
        self.normalizer = FullResultNormalizer(definitions_path=definitions_path)
        self.rules = ValidationRules.from_yaml(rules_path) if rules_path else ValidationRules()

        # Load semantic definitions for query info
        self.definitions: dict[str, Any] = {}
        if definitions_path and Path(definitions_path).exists():
            with open(definitions_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.definitions = data.get("queries", {})

    def validate_query(
        self,
        query_id: str,
        paradigm: str,
        rows: list[dict],
        parameters: dict[str, Any],
    ) -> ValidationResult:
        """Validate a single query result against Expected.

        Args:
            query_id: Query ID (Q1, Q2, etc.)
            paradigm: Paradigm name (P1, M1, O2)
            rows: ALL result rows from paradigm (not sample!)
            parameters: Query parameters used

        Returns:
            ValidationResult with status and details
        """
        # 1. Check IMPOSSIBLE
        if self.rules.is_impossible(query_id, paradigm):
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.IMPOSSIBLE,
                reason=self.rules.get_reason(query_id, paradigm),
            )

        # 2. Get Expected Answer
        expected = self.expected_store.get(query_id)
        if not expected:
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.MISMATCH,
                reason=f"No Expected Answer for {query_id}",
            )

        # 3. Normalize paradigm result
        normalized = self.normalizer.normalize(
            rows, query_id, paradigm, parameters
        )

        # 4. Quick hash comparison
        if normalized.content_hash == expected.content_hash:
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.MATCH,
                reason="Exact hash match",
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                hash_match=True,
                semantic_match=True,
            )

        # 5. Detailed semantic comparison
        return self._compare_semantic(
            query_id, paradigm, expected, normalized, parameters
        )

    def _compare_semantic(
        self,
        query_id: str,
        paradigm: str,
        expected: ExpectedAnswer,
        normalized: NormalizedResult,
        parameters: dict[str, Any],
    ) -> ValidationResult:
        """Compare semantic content in detail.

        Args:
            query_id: Query ID
            paradigm: Paradigm name
            expected: Expected Answer
            normalized: Normalized paradigm result
            parameters: Query parameters

        Returns:
            ValidationResult
        """
        semantic_type = expected.semantic_type

        if semantic_type == SemanticType.SET:
            return self._compare_sets(query_id, paradigm, expected, normalized)
        elif semantic_type == SemanticType.VALUE:
            return self._compare_values(query_id, paradigm, expected, normalized)
        elif semantic_type == SemanticType.AGGREGATE:
            return self._compare_aggregates(query_id, paradigm, expected, normalized)
        elif semantic_type == SemanticType.ORDERED_SET:
            return self._compare_ordered_sets(query_id, paradigm, expected, normalized)
        elif semantic_type == SemanticType.PATH:
            return self._compare_paths(query_id, paradigm, expected, normalized)
        elif semantic_type == SemanticType.DOCUMENT:
            return self._compare_documents(query_id, paradigm, expected, normalized)
        else:
            # Default: treat as set
            return self._compare_sets(query_id, paradigm, expected, normalized)

    def _compare_sets(
        self,
        query_id: str,
        paradigm: str,
        expected: ExpectedAnswer,
        normalized: NormalizedResult,
    ) -> ValidationResult:
        """Compare two sets."""
        expected_set = expected.semantic_content
        paradigm_set = normalized.semantic_content

        if not isinstance(expected_set, set):
            expected_set = set(expected_set) if expected_set else set()
        if not isinstance(paradigm_set, set):
            paradigm_set = set(paradigm_set) if paradigm_set else set()

        if expected_set == paradigm_set:
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.MATCH,
                reason=f"Identical sets ({len(expected_set)} items)",
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                semantic_match=True,
            )

        missing = expected_set - paradigm_set
        extra = paradigm_set - expected_set

        # Check if DEGRADED is expected
        if self.rules.is_degraded(query_id, paradigm):
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.DEGRADED,
                reason=self.rules.get_reason(query_id, paradigm),
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                missing_items=list(missing)[:10],
                extra_items=list(extra)[:10],
            )

        # MISMATCH - bug!
        return ValidationResult(
            query_id=query_id,
            paradigm=paradigm,
            status=ValidationStatus.MISMATCH,
            reason=f"Set difference: {len(missing)} missing, {len(extra)} extra",
            expected_row_count=expected.row_count,
            paradigm_row_count=normalized.row_count,
            missing_items=list(missing)[:10],
            extra_items=list(extra)[:10],
        )

    def _compare_values(
        self,
        query_id: str,
        paradigm: str,
        expected: ExpectedAnswer,
        normalized: NormalizedResult,
    ) -> ValidationResult:
        """Compare single values or value dicts."""
        expected_val = expected.semantic_content
        paradigm_val = normalized.semantic_content
        tolerance = self.rules.get_tolerance(query_id, paradigm)

        # Compare dicts
        if isinstance(expected_val, dict) and isinstance(paradigm_val, dict):
            differences = {}
            for key in expected_val:
                g_v = expected_val.get(key)
                p_v = paradigm_val.get(key)

                if not self._values_equal(g_v, p_v, tolerance):
                    differences[key] = {"expected": g_v, "paradigm": p_v}

            if not differences:
                return ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.MATCH,
                    reason="Values match within tolerance",
                    expected_row_count=expected.row_count,
                    paradigm_row_count=normalized.row_count,
                    semantic_match=True,
                )

            # Check if DEGRADED expected
            if self.rules.is_degraded(query_id, paradigm):
                return ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.DEGRADED,
                    reason=self.rules.get_reason(query_id, paradigm),
                    expected_row_count=expected.row_count,
                    paradigm_row_count=normalized.row_count,
                    value_differences=differences,
                )

            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.MISMATCH,
                reason=f"Value differences in {len(differences)} fields",
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                value_differences=differences,
            )

        # Compare single values
        if self._values_equal(expected_val, paradigm_val, tolerance):
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.MATCH,
                reason="Value matches within tolerance",
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                semantic_match=True,
            )

        if self.rules.is_degraded(query_id, paradigm):
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.DEGRADED,
                reason=self.rules.get_reason(query_id, paradigm),
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                value_differences={"value": {"expected": expected_val, "paradigm": paradigm_val}},
            )

        return ValidationResult(
            query_id=query_id,
            paradigm=paradigm,
            status=ValidationStatus.MISMATCH,
            reason=f"Value mismatch: {expected_val} vs {paradigm_val}",
            expected_row_count=expected.row_count,
            paradigm_row_count=normalized.row_count,
            value_differences={"value": {"expected": expected_val, "paradigm": paradigm_val}},
        )

    def _compare_aggregates(
        self,
        query_id: str,
        paradigm: str,
        expected: ExpectedAnswer,
        normalized: NormalizedResult,
    ) -> ValidationResult:
        """Compare aggregate results (keyed by grouping)."""
        expected_agg = expected.semantic_content or {}
        paradigm_agg = normalized.semantic_content or {}
        tolerance = self.rules.get_tolerance(query_id, paradigm)

        # Compare keys
        expected_keys = set(str(k) for k in expected_agg.keys())
        paradigm_keys = set(str(k) for k in paradigm_agg.keys())

        missing_keys = expected_keys - paradigm_keys
        extra_keys = paradigm_keys - expected_keys

        # Compare values for matching keys
        value_diffs = {}
        for key in expected_keys & paradigm_keys:
            g_vals = expected_agg.get(key) or expected_agg.get(str(key)) or {}
            p_vals = paradigm_agg.get(key) or paradigm_agg.get(str(key)) or {}

            if isinstance(g_vals, dict) and isinstance(p_vals, dict):
                for vkey in g_vals:
                    g_v = g_vals.get(vkey)
                    p_v = p_vals.get(vkey)
                    if not self._values_equal(g_v, p_v, tolerance):
                        if key not in value_diffs:
                            value_diffs[key] = {}
                        value_diffs[key][vkey] = {"expected": g_v, "paradigm": p_v}

        if not missing_keys and not extra_keys and not value_diffs:
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.MATCH,
                reason=f"Aggregates match ({len(expected_keys)} groups)",
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                semantic_match=True,
            )

        if self.rules.is_degraded(query_id, paradigm):
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.DEGRADED,
                reason=self.rules.get_reason(query_id, paradigm),
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                missing_items=list(missing_keys)[:10],
                extra_items=list(extra_keys)[:10],
                value_differences=value_diffs,
            )

        return ValidationResult(
            query_id=query_id,
            paradigm=paradigm,
            status=ValidationStatus.MISMATCH,
            reason=f"Aggregate mismatch: {len(missing_keys)} missing groups, {len(value_diffs)} value diffs",
            expected_row_count=expected.row_count,
            paradigm_row_count=normalized.row_count,
            missing_items=list(missing_keys)[:10],
            extra_items=list(extra_keys)[:10],
            value_differences=value_diffs,
        )

    def _compare_ordered_sets(
        self,
        query_id: str,
        paradigm: str,
        expected: ExpectedAnswer,
        normalized: NormalizedResult,
    ) -> ValidationResult:
        """Compare ordered lists (Top-N)."""
        expected_list = expected.semantic_content or []
        paradigm_list = normalized.semantic_content or []

        query_def = self.definitions.get(query_id, {})
        rank_tolerance = query_def.get("rank_tolerance", 0)

        # Check exact match first
        if expected_list == paradigm_list:
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.MATCH,
                reason=f"Exact order match ({len(expected_list)} items)",
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                semantic_match=True,
            )

        # Check with rank tolerance
        if rank_tolerance > 0:
            matches = 0
            for i, g_item in enumerate(expected_list):
                # Check if item exists within tolerance window
                window_start = max(0, i - rank_tolerance)
                window_end = min(len(paradigm_list), i + rank_tolerance + 1)
                if g_item in paradigm_list[window_start:window_end]:
                    matches += 1

            if matches >= len(expected_list) * 0.8:  # 80% threshold
                return ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.MATCH,
                    reason=f"Order matches within tolerance ({matches}/{len(expected_list)})",
                    expected_row_count=expected.row_count,
                    paradigm_row_count=normalized.row_count,
                    semantic_match=True,
                )

        # Check set equality (order differs but same items)
        if set(expected_list) == set(paradigm_list):
            if self.rules.is_degraded(query_id, paradigm):
                return ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.DEGRADED,
                    reason=f"Same items, different order - {self.rules.get_reason(query_id, paradigm)}",
                    expected_row_count=expected.row_count,
                    paradigm_row_count=normalized.row_count,
                )

            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.MISMATCH,
                reason="Same items but different order",
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
            )

        # Different items
        missing = set(expected_list) - set(paradigm_list)
        extra = set(paradigm_list) - set(expected_list)

        if self.rules.is_degraded(query_id, paradigm):
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.DEGRADED,
                reason=self.rules.get_reason(query_id, paradigm),
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                missing_items=list(missing)[:10],
                extra_items=list(extra)[:10],
            )

        return ValidationResult(
            query_id=query_id,
            paradigm=paradigm,
            status=ValidationStatus.MISMATCH,
            reason=f"Ordered set mismatch: {len(missing)} missing, {len(extra)} extra",
            expected_row_count=expected.row_count,
            paradigm_row_count=normalized.row_count,
            missing_items=list(missing)[:10],
            extra_items=list(extra)[:10],
        )

    def _compare_paths(
        self,
        query_id: str,
        paradigm: str,
        expected: ExpectedAnswer,
        normalized: NormalizedResult,
    ) -> ValidationResult:
        """Compare graph paths."""
        expected_paths = expected.semantic_content or []
        paradigm_paths = normalized.semantic_content or []

        query_def = self.definitions.get(query_id, {})
        validation = query_def.get("validation", {})

        # Check path lengths
        if validation.get("same_length", True):
            g_lengths = sorted(len(p) for p in expected_paths)
            p_lengths = sorted(len(p) for p in paradigm_paths)
            if g_lengths != p_lengths:
                if self.rules.is_degraded(query_id, paradigm):
                    return ValidationResult(
                        query_id=query_id,
                        paradigm=paradigm,
                        status=ValidationStatus.DEGRADED,
                        reason=self.rules.get_reason(query_id, paradigm),
                        expected_row_count=expected.row_count,
                        paradigm_row_count=normalized.row_count,
                    )
                return ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.MISMATCH,
                    reason=f"Path lengths differ: {g_lengths} vs {p_lengths}",
                    expected_row_count=expected.row_count,
                    paradigm_row_count=normalized.row_count,
                )

        # Check start/end nodes if required
        if expected_paths and paradigm_paths:
            g_start = expected_paths[0][0] if expected_paths[0] else None
            p_start = paradigm_paths[0][0] if paradigm_paths[0] else None
            g_end = expected_paths[0][-1] if expected_paths[0] else None
            p_end = paradigm_paths[0][-1] if paradigm_paths[0] else None

            if validation.get("same_start", True) and g_start != p_start:
                return ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.MISMATCH,
                    reason=f"Path start differs: {g_start} vs {p_start}",
                    expected_row_count=expected.row_count,
                    paradigm_row_count=normalized.row_count,
                )

            if validation.get("same_end", True) and g_end != p_end:
                return ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.MISMATCH,
                    reason=f"Path end differs: {g_end} vs {p_end}",
                    expected_row_count=expected.row_count,
                    paradigm_row_count=normalized.row_count,
                )

        return ValidationResult(
            query_id=query_id,
            paradigm=paradigm,
            status=ValidationStatus.MATCH,
            reason=f"Paths match ({len(expected_paths)} paths)",
            expected_row_count=expected.row_count,
            paradigm_row_count=normalized.row_count,
            semantic_match=True,
        )

    def _compare_documents(
        self,
        query_id: str,
        paradigm: str,
        expected: ExpectedAnswer,
        normalized: NormalizedResult,
    ) -> ValidationResult:
        """Compare document (nested JSON)."""
        expected_doc = expected.semantic_content or {}
        paradigm_doc = normalized.semantic_content or {}

        query_def = self.definitions.get(query_id, {})
        structure = query_def.get("structure", {})
        required_fields = structure.get("required", [])

        # Check required fields
        missing_required = []
        for field in required_fields:
            if field not in paradigm_doc:
                missing_required.append(field)

        if missing_required:
            if self.rules.is_degraded(query_id, paradigm):
                return ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.DEGRADED,
                    reason=self.rules.get_reason(query_id, paradigm),
                    expected_row_count=expected.row_count,
                    paradigm_row_count=normalized.row_count,
                    missing_items=missing_required,
                )
            return ValidationResult(
                query_id=query_id,
                paradigm=paradigm,
                status=ValidationStatus.MISMATCH,
                reason=f"Missing required fields: {missing_required}",
                expected_row_count=expected.row_count,
                paradigm_row_count=normalized.row_count,
                missing_items=missing_required,
            )

        return ValidationResult(
            query_id=query_id,
            paradigm=paradigm,
            status=ValidationStatus.MATCH,
            reason="Document structure valid",
            expected_row_count=expected.row_count,
            paradigm_row_count=normalized.row_count,
            semantic_match=True,
        )

    def _values_equal(
        self,
        val1: Any,
        val2: Any,
        tolerance: float,
    ) -> bool:
        """Compare values with tolerance for floats.

        Args:
            val1: First value
            val2: Second value
            tolerance: Relative tolerance for floats

        Returns:
            True if values are equal within tolerance
        """
        if val1 is None and val2 is None:
            return True
        if val1 is None or val2 is None:
            return False

        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            if val1 == 0 and val2 == 0:
                return True
            if val1 == 0 or val2 == 0:
                return abs(val1 - val2) < tolerance
            return abs(val1 - val2) / max(abs(val1), abs(val2)) < tolerance

        return val1 == val2

    def validate_all(
        self,
        paradigm: str,
        results: dict[str, list[dict]],
        parameters: dict[str, Any],
    ) -> dict[str, ValidationResult]:
        """Validate all queries for a paradigm.

        Args:
            paradigm: Paradigm name
            results: Dict mapping query_id to full rows
            parameters: Query parameters used

        Returns:
            Dict mapping query_id to ValidationResult
        """
        validations = {}
        for query_id, rows in results.items():
            validations[query_id] = self.validate_query(
                query_id, paradigm, rows, parameters
            )
        return validations


class ComparativeValidator:
    """Validate write queries by comparing between paradigms.

    For QW* queries that modify data, we can't use Expected Answers.
    Instead, we compare results between paradigms.
    """

    def __init__(
        self,
        definitions_path: Path | None = None,
        rules_path: Path | None = None,
    ):
        """Initialize validator.

        Args:
            definitions_path: Path to semantic_definitions.yaml
            rules_path: Path to validation_rules.yaml
        """
        self.normalizer = FullResultNormalizer(definitions_path=definitions_path)
        self.rules = ValidationRules.from_yaml(rules_path) if rules_path else ValidationRules()

    def validate_write_query(
        self,
        query_id: str,
        results: dict[str, list[dict]],
        parameters: dict[str, Any],
    ) -> dict[str, ValidationResult]:
        """Validate a write query by comparing paradigms.

        Args:
            query_id: Query ID (QW1, QW2, etc.)
            results: Dict mapping paradigm -> full rows
            parameters: Query parameters used

        Returns:
            Dict mapping paradigm -> ValidationResult
        """
        if len(results) < 2:
            # Need at least 2 paradigms to compare
            paradigm = list(results.keys())[0] if results else "unknown"
            return {
                paradigm: ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.MATCH,
                    reason="Single paradigm - no comparison possible",
                )
            }

        # Normalize all results
        normalized: dict[str, NormalizedResult] = {}
        for paradigm, rows in results.items():
            normalized[paradigm] = self.normalizer.normalize(
                rows, query_id, paradigm, parameters
            )

        # Compare row counts
        counts = {p: n.row_count for p, n in normalized.items()}
        unique_counts = set(counts.values())

        validations = {}

        if len(unique_counts) == 1:
            # All paradigms have same row count
            count = list(unique_counts)[0]

            # Compare content hashes
            hashes = {p: n.content_hash for p, n in normalized.items()}
            unique_hashes = set(hashes.values())

            if len(unique_hashes) == 1:
                # Perfect match
                for paradigm in results:
                    validations[paradigm] = ValidationResult(
                        query_id=query_id,
                        paradigm=paradigm,
                        status=ValidationStatus.MATCH,
                        reason=f"All paradigms match ({count} rows)",
                        paradigm_row_count=count,
                        hash_match=True,
                        semantic_match=True,
                    )
            else:
                # Same count but different content
                for paradigm in results:
                    validations[paradigm] = ValidationResult(
                        query_id=query_id,
                        paradigm=paradigm,
                        status=ValidationStatus.MISMATCH,
                        reason=f"Same row count ({count}) but content differs",
                        paradigm_row_count=counts[paradigm],
                    )
        else:
            # Different row counts
            for paradigm in results:
                validations[paradigm] = ValidationResult(
                    query_id=query_id,
                    paradigm=paradigm,
                    status=ValidationStatus.MISMATCH,
                    reason=f"Row count mismatch: {counts}",
                    paradigm_row_count=counts[paradigm],
                )

        return validations
