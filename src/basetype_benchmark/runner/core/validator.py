"""Golden dataset validation module.

Compares actual query results against expected values from golden_answers.yaml.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .params import GoldenAnswersLoader


@dataclass
class ValidationResult:
    """Result of validating query results against golden answers."""

    passed: bool
    query_id: str
    expected_count: Optional[int] = None
    actual_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        msg = f"[{status}] {self.query_id}: {self.actual_count} rows"
        if self.expected_count is not None:
            msg += f" (expected {self.expected_count})"
        if self.errors:
            msg += f" - Errors: {', '.join(self.errors)}"
        if self.warnings:
            msg += f" - Warnings: {', '.join(self.warnings)}"
        return msg


class GoldenValidator:
    """Validates query results against golden_answers.yaml expectations.

    Supports:
    - Row count validation (exact match)
    - Column presence validation
    - Value comparison with tolerance for floats
    """

    def __init__(self, tolerance: float = 0.01):
        """Initialize validator.

        Args:
            tolerance: Relative tolerance for float comparisons (default 1%)
        """
        self.tolerance = tolerance
        self.loader = GoldenAnswersLoader()

    def validate(
        self,
        query_id: str,
        actual_results: list[dict[str, Any]],
        skip_value_check: bool = False,
    ) -> ValidationResult:
        """Validate query results against golden answers.

        Args:
            query_id: Query identifier (Q1, Q2, ..., QW1, etc.)
            actual_results: List of result dictionaries from query execution
            skip_value_check: If True, only validate row count

        Returns:
            ValidationResult with pass/fail status and any errors/warnings
        """
        result = ValidationResult(
            passed=True,
            query_id=query_id,
            actual_count=len(actual_results),
        )

        # Get expected values
        expected_count = self.loader.get_expected_count(query_id)
        expected_rows = self.loader.get_expected_results(query_id)

        result.expected_count = expected_count

        # Validate row count
        if expected_count is not None:
            if len(actual_results) != expected_count:
                result.passed = False
                result.errors.append(
                    f"Row count mismatch: got {len(actual_results)}, expected {expected_count}"
                )

        # Skip further validation if requested or no expected rows defined
        if skip_value_check or expected_rows is None:
            return result

        # Validate columns and values
        if expected_rows and actual_results:
            col_errors = self._validate_columns(actual_results, expected_rows)
            result.errors.extend(col_errors)
            if col_errors:
                result.passed = False

            # Validate values (sample comparison)
            value_errors = self._validate_values(actual_results, expected_rows)
            result.errors.extend(value_errors)
            if value_errors:
                result.passed = False

        return result

    def validate_row_count_only(
        self, query_id: str, actual_count: int
    ) -> ValidationResult:
        """Validate only the row count.

        Args:
            query_id: Query identifier
            actual_count: Number of rows returned

        Returns:
            ValidationResult with pass/fail status
        """
        result = ValidationResult(
            passed=True,
            query_id=query_id,
            actual_count=actual_count,
        )

        expected_count = self.loader.get_expected_count(query_id)
        result.expected_count = expected_count

        if expected_count is not None and actual_count != expected_count:
            result.passed = False
            result.errors.append(
                f"Row count mismatch: got {actual_count}, expected {expected_count}"
            )

        return result

    def _validate_columns(
        self, actual: list[dict], expected: list[dict]
    ) -> list[str]:
        """Check that actual results have expected columns."""
        errors = []

        if not expected or not actual:
            return errors

        expected_cols = set(expected[0].keys())
        actual_cols = set(actual[0].keys())

        # Check for missing columns
        missing = expected_cols - actual_cols
        if missing:
            errors.append(f"Missing columns: {sorted(missing)}")

        return errors

    def _validate_values(
        self, actual: list[dict], expected: list[dict]
    ) -> list[str]:
        """Compare actual values against expected (sample comparison).

        Only compares the first N rows where N = min(len(expected), len(actual)).
        Uses fuzzy matching for floats.
        """
        errors = []

        # Find matching rows by primary key or index
        for i, expected_row in enumerate(expected):
            if i >= len(actual):
                break

            # Try to match by 'id' or other key columns
            actual_row = self._find_matching_row(actual, expected_row)
            if actual_row is None:
                # Fallback to index-based comparison
                if i < len(actual):
                    actual_row = actual[i]
                else:
                    continue

            # Compare values
            for key, expected_val in expected_row.items():
                if key not in actual_row:
                    continue

                actual_val = actual_row[key]
                if not self._values_match(actual_val, expected_val):
                    errors.append(
                        f"Value mismatch at row {i}, column '{key}': "
                        f"got {actual_val!r}, expected {expected_val!r}"
                    )

        return errors

    def _find_matching_row(
        self, actual: list[dict], expected_row: dict
    ) -> Optional[dict]:
        """Find an actual row that matches the expected row by key columns."""
        # Common key columns to match on
        key_cols = ['id', 'point_id', 'equipment_id', 'space_id', 'tenant_id']

        for key_col in key_cols:
            if key_col in expected_row:
                expected_key = expected_row[key_col]
                for actual_row in actual:
                    if actual_row.get(key_col) == expected_key:
                        return actual_row

        return None

    def _values_match(self, actual: Any, expected: Any) -> bool:
        """Compare two values with tolerance for floats."""
        if actual is None and expected is None:
            return True

        if actual is None or expected is None:
            return False

        # Float comparison with tolerance
        if isinstance(expected, float) or isinstance(actual, float):
            try:
                actual_f = float(actual)
                expected_f = float(expected)
                if expected_f == 0:
                    return abs(actual_f) < self.tolerance
                return abs(actual_f - expected_f) / abs(expected_f) <= self.tolerance
            except (ValueError, TypeError):
                return False

        # Integer comparison
        if isinstance(expected, int) and isinstance(actual, (int, float)):
            return int(actual) == expected

        # String comparison (case-sensitive)
        if isinstance(expected, str):
            return str(actual) == expected

        # List comparison
        if isinstance(expected, list):
            if not isinstance(actual, list):
                return False
            return set(actual) == set(expected)

        # Direct comparison
        return actual == expected


# Singleton instance
_validator: Optional[GoldenValidator] = None


def get_golden_validator(tolerance: float = 0.01) -> GoldenValidator:
    """Get or create global golden validator instance."""
    global _validator
    if _validator is None:
        _validator = GoldenValidator(tolerance=tolerance)
    return _validator
