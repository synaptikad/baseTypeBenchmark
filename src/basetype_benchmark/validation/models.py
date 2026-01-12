"""Data models for validation engine.

Provides dataclasses for:
- ExpectedAnswer: Expected answer (ground truth) for a query
- NormalizedResult: Normalized paradigm result
- ValidationResult: Result of comparing against expected answer
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SemanticType(str, Enum):
    """Types of query results for semantic validation."""

    SET = "set"                    # Unordered set of IDs
    VALUE = "value"                # Single scalar or tuple
    AGGREGATE = "aggregate"        # Time-bucketed or grouped aggregates
    ORDERED_SET = "ordered_set"    # Ordered results (Top-N)
    PATH = "path"                  # Graph path
    DOCUMENT = "document"          # Nested JSON document


class ValidationStatus(str, Enum):
    """Validation outcome status."""

    MATCH = "MATCH"               # Identical to expected answer
    DEGRADED = "DEGRADED"         # Expected difference (tolerance)
    IMPOSSIBLE = "IMPOSSIBLE"     # Query not supported by paradigm
    MISMATCH = "MISMATCH"         # Bug detected!


@dataclass
class ExpectedAnswer:
    """Expected answer (ground truth) for a query.

    Computed during dataset generation from in-memory nodes/edges/timeseries.
    """

    query_id: str
    parameters: dict[str, Any]
    semantic_type: SemanticType
    semantic_content: Any          # set, dict, list depending on type
    row_count: int
    content_hash: str              # SHA256 of normalized content
    full_rows: list[dict] = field(default_factory=list)  # All rows for debugging

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        content = self.semantic_content
        if isinstance(content, set):
            content = sorted(list(content), key=str)
        elif isinstance(content, frozenset):
            content = sorted(list(content), key=str)

        return {
            "query_id": self.query_id,
            "parameters": self.parameters,
            "semantic_type": self.semantic_type.value if isinstance(self.semantic_type, SemanticType) else self.semantic_type,
            "semantic_content": content,
            "row_count": self.row_count,
            "content_hash": self.content_hash,
            "full_rows": self.full_rows,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExpectedAnswer":
        """Create from dictionary."""
        # Handle both "semantic_type" and "answer_type" keys for compatibility
        semantic_type_str = data.get("semantic_type") or data.get("answer_type", "set")
        try:
            semantic_type = SemanticType(semantic_type_str)
        except ValueError:
            semantic_type = SemanticType.SET

        content = data["semantic_content"]

        # Restore set types
        if semantic_type == SemanticType.SET:
            if isinstance(content, list):
                # Check if items are tuples (composite keys)
                if content and isinstance(content[0], list):
                    content = {tuple(item) for item in content}
                else:
                    content = set(content)

        return cls(
            query_id=data["query_id"],
            parameters=data["parameters"],
            semantic_type=semantic_type,
            semantic_content=content,
            row_count=data["row_count"],
            content_hash=data["content_hash"],
            full_rows=data.get("full_rows", []),
        )


@dataclass
class NormalizedResult:
    """Normalized paradigm result for validation."""

    semantic_type: str
    semantic_content: Any
    row_count: int
    content_hash: str
    canonical_rows: list[dict]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        content = self.semantic_content
        if isinstance(content, set):
            content = sorted(list(content), key=str)
        elif isinstance(content, frozenset):
            content = sorted(list(content), key=str)

        return {
            "semantic_type": self.semantic_type,
            "semantic_content": content,
            "row_count": self.row_count,
            "content_hash": self.content_hash,
            "canonical_rows": self.canonical_rows,
        }


@dataclass
class ValidationResult:
    """Result of validating a paradigm result against expected answer."""

    query_id: str
    paradigm: str
    status: ValidationStatus
    reason: str

    expected_row_count: int = 0
    paradigm_row_count: int = 0
    hash_match: bool = False
    semantic_match: bool = False

    # Differences (if MISMATCH)
    missing_items: list = field(default_factory=list)
    extra_items: list = field(default_factory=list)
    value_differences: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "query_id": self.query_id,
            "paradigm": self.paradigm,
            "status": self.status.value,
            "reason": self.reason,
            "expected_row_count": self.expected_row_count,
            "paradigm_row_count": self.paradigm_row_count,
            "hash_match": self.hash_match,
            "semantic_match": self.semantic_match,
        }

        if self.missing_items:
            result["missing_items"] = self.missing_items[:10]
        if self.extra_items:
            result["extra_items"] = self.extra_items[:10]
        if self.value_differences:
            result["value_differences"] = self.value_differences

        return result


def compute_content_hash(content: Any) -> str:
    """Compute SHA256 hash of semantic content."""
    if isinstance(content, set):
        serializable = sorted(list(content), key=str)
    elif isinstance(content, frozenset):
        serializable = sorted(list(content), key=str)
    elif isinstance(content, dict):
        serializable = {str(k): v for k, v in sorted(content.items())}
    else:
        serializable = content

    json_str = json.dumps(serializable, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]
