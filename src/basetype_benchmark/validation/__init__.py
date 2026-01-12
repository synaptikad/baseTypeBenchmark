"""Validation engine for cross-paradigm query correctness.

This module provides full-results validation to ensure that for the SAME dataset
and SAME question, all paradigms return the SAME information.

Approach:
- Read-only queries (Q1-Q23): Expected Answers computed during dataset generation
- Write queries (QW*): Comparative validation between paradigms
- Workloads: Comparative validation (same sequence → same result)

Key components:
- ExpectedAnswerStore: Loads Expected Answers from dataset's expected_answers/
- FullResultNormalizer: Normalizes paradigm-specific results to canonical form
- AnswerValidator: Validates paradigm results against Expected Answers
- ComparativeValidator: Validates write queries by comparing between paradigms
"""

from .models import (
    ExpectedAnswer,
    NormalizedResult,
    SemanticType,
    ValidationResult,
    ValidationStatus,
)
from .normalizer import FullResultNormalizer
from .expected_store import ExpectedAnswerStore
from .validator import AnswerValidator, ComparativeValidator

__all__ = [
    # Models
    "ExpectedAnswer",
    "NormalizedResult",
    "SemanticType",
    "ValidationResult",
    "ValidationStatus",
    # Core
    "FullResultNormalizer",
    "ExpectedAnswerStore",
    "AnswerValidator",
    "ComparativeValidator",
]
