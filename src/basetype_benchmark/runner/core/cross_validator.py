"""Cross-paradigm validation for academic benchmarking.

Sprint 3 - Benchmark BaseType V3

Provides infrastructure for validating query results across paradigms:
- Row-level comparison with semantic equivalence rules
- Tolerance for floating point values
- Handling of DEGRADED and IMPOSSIBLE query statuses
- Generation of validation reports for publication

Reference paradigm: P1 (PostgreSQL normalized) is considered ground truth.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from ..benchmark.results import BenchmarkResults, QueryResult


class ValidationStatus(str, Enum):
    """Status of cross-paradigm validation for a query."""
    EQUIVALENT = "EQUIVALENT"      # Results match (within tolerance)
    MISMATCH = "MISMATCH"          # Results differ unexpectedly
    DEGRADED = "DEGRADED"          # Known limitation, acceptable difference
    SKIP = "SKIP"                  # Query impossible for one paradigm
    NO_DATA = "NO_DATA"            # No results to compare


# Rules for semantic equivalence
EQUIVALENCE_RULES = {
    # Columns used as keys for row alignment
    "key_columns": [
        "id", "point_id", "equipment_id", "space_id", "tenant_id",
        "node_id", "building_id", "floor_id", "query_id"
    ],

    # Float comparison tolerance (1% relative)
    "float_tolerance": 0.01,

    # Columns to ignore in comparison (metadata, ordering)
    "ignore_columns": ["row_number", "rank", "rn"],

    # Queries known to be DEGRADED per paradigm
    "degraded_queries": {
        "M1": {
            "Q6": "No TimescaleDB - uses TimeseriesChunk",
            "Q7": "No TimescaleDB - uses TimeseriesChunk with UNWIND",
            "Q8": "No TimescaleDB - uses TimeseriesChunk with UNWIND",
            "Q9": "No TimescaleDB - uses TimeseriesChunk with UNWIND",
            "Q12": "No TimescaleDB - uses TimeseriesChunk with UNWIND",
            "Q13": "No TimescaleDB - uses TimeseriesChunk with UNWIND",
        },
        "O2": {
            "Q6": "SPARQL lacks time_bucket aggregation",
            "Q15": "Date arithmetic approximation (365/30 days)",
            "Q23": "Fixed 3-hop limit (can't parameterize depth)",
        },
    },

    # Queries impossible per paradigm
    "impossible_queries": {
        "P1": {
            "Q14": "No JSONB metadata column",
            "Q15": "No JSONB metadata column",
            "Q16": "No JSONB tags column",
            "Q17": "No JSONB capabilities column",
        },
        "M1": {
            "Q19": "No JSONB for digital twin data",
        },
        "O2": {
            "Q20": "SPARQL lacks shortestPath algorithm",
            "Q21": "SPARQL lacks allShortestPaths algorithm",
        },
    },
}


@dataclass
class RowDiff:
    """Details of a row difference."""
    key: dict[str, Any]           # Key columns identifying the row
    column: str                   # Column with difference
    ref_value: Any                # Value in reference
    cmp_value: Any                # Value in compared paradigm
    diff_type: str                # "missing", "extra", "value_mismatch"


@dataclass
class ComparisonResult:
    """Result of comparing one query between two paradigms."""
    query_id: str
    reference_paradigm: str
    compared_paradigm: str
    status: ValidationStatus

    # Row counts
    row_count_ref: int = 0
    row_count_cmp: int = 0
    row_count_match: bool = False

    # Hash comparison (full result integrity)
    hash_ref: str | None = None
    hash_cmp: str | None = None
    hash_match: bool = False

    # Detailed differences (first 10 only)
    diffs: list[RowDiff] = field(default_factory=list)

    # Reason for DEGRADED/SKIP status
    reason: str | None = None

    def to_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "reference_paradigm": self.reference_paradigm,
            "compared_paradigm": self.compared_paradigm,
            "status": self.status.value,
            "row_count_ref": self.row_count_ref,
            "row_count_cmp": self.row_count_cmp,
            "row_count_match": self.row_count_match,
            "hash_match": self.hash_match,
            "diffs": [
                {
                    "key": d.key,
                    "column": d.column,
                    "ref_value": d.ref_value,
                    "cmp_value": d.cmp_value,
                    "diff_type": d.diff_type,
                }
                for d in self.diffs[:10]  # Limit to 10 diffs
            ],
            "reason": self.reason,
        }


@dataclass
class ValidationReport:
    """Complete validation report for a benchmark run."""
    validation_id: str
    benchmark_id: str
    reference_paradigm: str
    compared_paradigms: list[str]
    timestamp: datetime = field(default_factory=datetime.now)

    # Summary counts
    total_queries: int = 0
    equivalent_count: int = 0
    mismatch_count: int = 0
    degraded_count: int = 0
    skip_count: int = 0

    # Detailed results: query_id -> paradigm -> ComparisonResult
    comparisons: dict[str, dict[str, ComparisonResult]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "validation_id": self.validation_id,
            "benchmark_id": self.benchmark_id,
            "reference_paradigm": self.reference_paradigm,
            "compared_paradigms": self.compared_paradigms,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "total_queries": self.total_queries,
                "equivalent": self.equivalent_count,
                "mismatch": self.mismatch_count,
                "degraded": self.degraded_count,
                "skip": self.skip_count,
            },
            "queries": {
                qid: {
                    paradigm: cmp.to_dict()
                    for paradigm, cmp in paradigm_results.items()
                }
                for qid, paradigm_results in self.comparisons.items()
            },
        }

    def to_json(self, path: Path, indent: int = 2) -> None:
        """Export report to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=indent, default=str)


@dataclass
class PairComparison:
    """Summary of comparison between two paradigms."""
    paradigm_a: str
    paradigm_b: str
    equivalent: int = 0
    mismatch: int = 0
    degraded: int = 0
    skip: int = 0
    total: int = 0

    @property
    def equivalence_rate(self) -> float:
        """Percentage of equivalent queries (excluding skip)."""
        comparable = self.total - self.skip
        if comparable == 0:
            return 0.0
        return (self.equivalent / comparable) * 100

    def to_dict(self) -> dict:
        return {
            "paradigm_a": self.paradigm_a,
            "paradigm_b": self.paradigm_b,
            "equivalent": self.equivalent,
            "mismatch": self.mismatch,
            "degraded": self.degraded,
            "skip": self.skip,
            "total": self.total,
            "equivalence_rate": round(self.equivalence_rate, 1),
        }


@dataclass
class CrossValidationMatrix:
    """Complete cross-validation matrix for all paradigm pairs."""
    validation_id: str
    benchmark_id: str
    paradigms: list[str]
    timestamp: datetime = field(default_factory=datetime.now)

    # Matrix: paradigm_a -> paradigm_b -> PairComparison
    matrix: dict[str, dict[str, PairComparison]] = field(default_factory=dict)

    # Per-query details: query_id -> paradigm_a -> paradigm_b -> ComparisonResult
    query_details: dict[str, dict[str, dict[str, ComparisonResult]]] = field(default_factory=dict)

    def get_pair(self, a: str, b: str) -> PairComparison | None:
        """Get comparison for a specific pair."""
        return self.matrix.get(a, {}).get(b)

    def to_dict(self) -> dict:
        return {
            "validation_id": self.validation_id,
            "benchmark_id": self.benchmark_id,
            "paradigms": self.paradigms,
            "timestamp": self.timestamp.isoformat(),
            "matrix": {
                pa: {pb: cmp.to_dict() for pb, cmp in pb_map.items()}
                for pa, pb_map in self.matrix.items()
            },
            "query_details": {
                qid: {
                    pa: {pb: cmp.to_dict() for pb, cmp in pb_map.items()}
                    for pa, pb_map in pa_map.items()
                }
                for qid, pa_map in self.query_details.items()
            },
        }

    def to_json(self, path: Path, indent: int = 2) -> None:
        """Export matrix to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=indent, default=str)


class CrossParadigmValidator:
    """Validates query results across paradigms.

    Compares all paradigms against a reference (default: P1).
    Handles semantic equivalence with configurable tolerance.
    """

    def __init__(
        self,
        reference: str = "P1",
        float_tolerance: float = 0.01,
        rules: dict | None = None,
    ):
        self.reference = reference
        self.float_tolerance = float_tolerance
        self.rules = rules or EQUIVALENCE_RULES

    def validate_matrix(self, results: BenchmarkResults) -> CrossValidationMatrix:
        """Validate all paradigm pairs (cross-validation matrix).

        Compares every paradigm against every other paradigm.
        Useful for identifying which paradigms agree with each other.

        Args:
            results: Complete benchmark results

        Returns:
            CrossValidationMatrix with all pairwise comparisons
        """
        paradigms = list(results.results.keys())

        matrix = CrossValidationMatrix(
            validation_id=f"{results.benchmark_id}_cross_matrix",
            benchmark_id=results.benchmark_id,
            paradigms=paradigms,
        )

        # Get all query IDs
        query_ids = set()
        for paradigm in results.results.values():
            for level in paradigm.levels:
                if level.status == "success":
                    query_ids.update(level.queries.keys())
                    break

        # Compare each pair of paradigms
        for i, paradigm_a in enumerate(paradigms):
            matrix.matrix[paradigm_a] = {}
            for paradigm_b in paradigms[i + 1:]:  # Only upper triangle
                pair = PairComparison(
                    paradigm_a=paradigm_a,
                    paradigm_b=paradigm_b,
                    total=len(query_ids),
                )

                for query_id in sorted(query_ids):
                    # Get results for both paradigms
                    result_a = self._get_query_result(
                        results.results[paradigm_a], query_id
                    )
                    result_b = self._get_query_result(
                        results.results[paradigm_b], query_id
                    )

                    # Compare using paradigm_a as reference
                    old_ref = self.reference
                    self.reference = paradigm_a
                    comparison = self._compare_query(
                        query_id, result_a, result_b, paradigm_b
                    )
                    self.reference = old_ref

                    # Store in query_details
                    if query_id not in matrix.query_details:
                        matrix.query_details[query_id] = {}
                    if paradigm_a not in matrix.query_details[query_id]:
                        matrix.query_details[query_id][paradigm_a] = {}
                    matrix.query_details[query_id][paradigm_a][paradigm_b] = comparison

                    # Update pair counts
                    if comparison.status == ValidationStatus.EQUIVALENT:
                        pair.equivalent += 1
                    elif comparison.status == ValidationStatus.MISMATCH:
                        pair.mismatch += 1
                    elif comparison.status == ValidationStatus.DEGRADED:
                        pair.degraded += 1
                    elif comparison.status == ValidationStatus.SKIP:
                        pair.skip += 1

                matrix.matrix[paradigm_a][paradigm_b] = pair
                # Mirror for easy lookup
                if paradigm_b not in matrix.matrix:
                    matrix.matrix[paradigm_b] = {}
                matrix.matrix[paradigm_b][paradigm_a] = pair

        return matrix

    def validate(self, results: BenchmarkResults) -> ValidationReport:
        """Validate all paradigms in benchmark results.

        Args:
            results: Complete benchmark results

        Returns:
            ValidationReport with detailed comparison results
        """
        report = ValidationReport(
            validation_id=f"{results.benchmark_id}_validation",
            benchmark_id=results.benchmark_id,
            reference_paradigm=self.reference,
            compared_paradigms=[p for p in results.results.keys() if p != self.reference],
        )

        # Get reference results
        if self.reference not in results.results:
            raise ValueError(f"Reference paradigm {self.reference} not in results")

        ref_paradigm = results.results[self.reference]

        # Get all query IDs from first successful level
        query_ids = set()
        for paradigm in results.results.values():
            for level in paradigm.levels:
                if level.status == "success":
                    query_ids.update(level.queries.keys())
                    break

        report.total_queries = len(query_ids)

        # Compare each paradigm against reference
        for paradigm_name, paradigm_results in results.results.items():
            if paradigm_name == self.reference:
                continue

            for query_id in sorted(query_ids):
                # Get query results from first successful level
                ref_query = self._get_query_result(ref_paradigm, query_id)
                cmp_query = self._get_query_result(paradigm_results, query_id)

                # Compare
                comparison = self._compare_query(
                    query_id, ref_query, cmp_query, paradigm_name
                )

                # Store result
                if query_id not in report.comparisons:
                    report.comparisons[query_id] = {}
                report.comparisons[query_id][paradigm_name] = comparison

                # Update counts
                if comparison.status == ValidationStatus.EQUIVALENT:
                    report.equivalent_count += 1
                elif comparison.status == ValidationStatus.MISMATCH:
                    report.mismatch_count += 1
                elif comparison.status == ValidationStatus.DEGRADED:
                    report.degraded_count += 1
                elif comparison.status == ValidationStatus.SKIP:
                    report.skip_count += 1

        return report

    def _get_query_result(self, paradigm_results, query_id: str) -> QueryResult | None:
        """Get QueryResult from first successful level."""
        for level in paradigm_results.levels:
            if level.status == "success" and query_id in level.queries:
                return level.queries[query_id]
        return None

    def _compare_query(
        self,
        query_id: str,
        ref_result: QueryResult | None,
        cmp_result: QueryResult | None,
        cmp_paradigm: str,
    ) -> ComparisonResult:
        """Compare a single query between reference and compared paradigm."""
        comparison = ComparisonResult(
            query_id=query_id,
            reference_paradigm=self.reference,
            compared_paradigm=cmp_paradigm,
            status=ValidationStatus.NO_DATA,
        )

        # Check for IMPOSSIBLE queries
        impossible = self.rules.get("impossible_queries", {})
        if query_id in impossible.get(self.reference, {}):
            comparison.status = ValidationStatus.SKIP
            comparison.reason = f"IMPOSSIBLE for {self.reference}: {impossible[self.reference][query_id]}"
            return comparison

        if query_id in impossible.get(cmp_paradigm, {}):
            comparison.status = ValidationStatus.SKIP
            comparison.reason = f"IMPOSSIBLE for {cmp_paradigm}: {impossible[cmp_paradigm][query_id]}"
            return comparison

        # Check for missing results
        if ref_result is None and cmp_result is None:
            comparison.status = ValidationStatus.NO_DATA
            comparison.reason = "No results for either paradigm"
            return comparison

        if ref_result is None:
            comparison.status = ValidationStatus.SKIP
            comparison.reason = f"No results for reference {self.reference}"
            return comparison

        if cmp_result is None:
            comparison.status = ValidationStatus.SKIP
            comparison.reason = f"No results for {cmp_paradigm}"
            return comparison

        # Extract data
        comparison.row_count_ref = ref_result.row_count
        comparison.row_count_cmp = cmp_result.row_count
        comparison.row_count_match = (ref_result.row_count == cmp_result.row_count)
        comparison.hash_ref = ref_result.row_hash
        comparison.hash_cmp = cmp_result.row_hash
        comparison.hash_match = (ref_result.row_hash == cmp_result.row_hash)

        # Check for known DEGRADED status
        degraded = self.rules.get("degraded_queries", {})
        if query_id in degraded.get(cmp_paradigm, {}):
            comparison.status = ValidationStatus.DEGRADED
            comparison.reason = degraded[cmp_paradigm][query_id]
            return comparison

        # Quick check: if hashes match, results are identical
        if comparison.hash_match:
            comparison.status = ValidationStatus.EQUIVALENT
            return comparison

        # Detailed comparison of sample_rows
        if ref_result.sample_rows and cmp_result.sample_rows:
            diffs = self._compare_rows(
                ref_result.sample_rows,
                cmp_result.sample_rows,
                ref_result.column_names or [],
            )
            comparison.diffs = diffs

            if not diffs and comparison.row_count_match:
                comparison.status = ValidationStatus.EQUIVALENT
            elif not diffs:
                # Rows match but counts differ - could be sampling artifact
                comparison.status = ValidationStatus.EQUIVALENT
                comparison.reason = "Sample rows match, count differs (sampling artifact)"
            else:
                comparison.status = ValidationStatus.MISMATCH
                comparison.reason = f"{len(diffs)} row differences found"
        else:
            # No sample rows, fall back to row count
            if comparison.row_count_match:
                comparison.status = ValidationStatus.EQUIVALENT
                comparison.reason = "Row counts match (no sample rows for detailed comparison)"
            else:
                comparison.status = ValidationStatus.MISMATCH
                comparison.reason = f"Row count mismatch: {comparison.row_count_ref} vs {comparison.row_count_cmp}"

        return comparison

    def _compare_rows(
        self,
        ref_rows: list[dict],
        cmp_rows: list[dict],
        columns: list[str],
    ) -> list[RowDiff]:
        """Compare rows using key-based alignment."""
        diffs = []
        key_cols = self.rules.get("key_columns", [])
        ignore_cols = self.rules.get("ignore_columns", [])

        # Build index of reference rows by key
        ref_index = {}
        for row in ref_rows:
            key = self._extract_key(row, key_cols)
            if key:
                ref_index[key] = row

        # Build index of compared rows by key
        cmp_index = {}
        for row in cmp_rows:
            key = self._extract_key(row, key_cols)
            if key:
                cmp_index[key] = row

        # Find missing rows (in ref but not in cmp)
        for key, ref_row in ref_index.items():
            if key not in cmp_index:
                diffs.append(RowDiff(
                    key=dict(zip(key_cols, key)) if isinstance(key, tuple) else {"key": key},
                    column="*",
                    ref_value=ref_row,
                    cmp_value=None,
                    diff_type="missing",
                ))

        # Find extra rows (in cmp but not in ref)
        for key, cmp_row in cmp_index.items():
            if key not in ref_index:
                diffs.append(RowDiff(
                    key=dict(zip(key_cols, key)) if isinstance(key, tuple) else {"key": key},
                    column="*",
                    ref_value=None,
                    cmp_value=cmp_row,
                    diff_type="extra",
                ))

        # Compare matching rows
        for key in ref_index:
            if key in cmp_index:
                ref_row = ref_index[key]
                cmp_row = cmp_index[key]

                for col in ref_row.keys():
                    if col in ignore_cols:
                        continue

                    ref_val = ref_row.get(col)
                    cmp_val = cmp_row.get(col)

                    if not self._values_match(ref_val, cmp_val):
                        diffs.append(RowDiff(
                            key=dict(zip(key_cols, key)) if isinstance(key, tuple) else {"key": key},
                            column=col,
                            ref_value=ref_val,
                            cmp_value=cmp_val,
                            diff_type="value_mismatch",
                        ))

        return diffs

    def _extract_key(self, row: dict, key_cols: list[str]) -> tuple | str | None:
        """Extract key from row for alignment."""
        keys = []
        for col in key_cols:
            if col in row:
                val = row[col]
                # Convert unhashable types to string for use as dict key
                if isinstance(val, (dict, list)):
                    val = json.dumps(val, sort_keys=True, default=str)
                keys.append(val)

        if not keys:
            # Fallback: use first column as key
            if row:
                first_col = list(row.keys())[0]
                val = row[first_col]
                if isinstance(val, (dict, list)):
                    val = json.dumps(val, sort_keys=True, default=str)
                return val
            return None

        return tuple(keys) if len(keys) > 1 else keys[0]

    def _values_match(self, ref_val: Any, cmp_val: Any) -> bool:
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
                return abs(cmp_val) < self.float_tolerance
            rel_diff = abs(ref_val - cmp_val) / abs(ref_val)
            return rel_diff <= self.float_tolerance

        # String comparison (case-insensitive for some columns)
        if isinstance(ref_val, str) and isinstance(cmp_val, str):
            return ref_val == cmp_val

        # Default: exact match
        return ref_val == cmp_val


def validate_results(
    results_path: Path,
    reference: str = "P1",
    tolerance: float = 0.01,
) -> ValidationReport:
    """Convenience function to validate results from JSON file.

    Args:
        results_path: Path to results.json
        reference: Reference paradigm
        tolerance: Float comparison tolerance

    Returns:
        ValidationReport
    """
    results = BenchmarkResults.from_json(results_path)
    validator = CrossParadigmValidator(reference=reference, float_tolerance=tolerance)
    return validator.validate(results)
