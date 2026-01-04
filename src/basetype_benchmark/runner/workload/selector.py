"""Query selectors for workload execution."""

import random
from abc import ABC, abstractmethod
from typing import List, Optional

from .config import QuerySpec, SelectionStrategy


class QuerySelector(ABC):
    """Abstract base for query selection."""

    def __init__(self, queries: List[QuerySpec], seed: Optional[int] = None):
        self.queries = queries
        self.seed = seed
        self._index = 0

    @abstractmethod
    def next(self) -> QuerySpec:
        """Get next query to execute."""
        pass

    def reset(self) -> None:
        """Reset selector state."""
        self._index = 0


class SequentialSelector(QuerySelector):
    """Select queries in order: Q1, Q2, ..., Q13, Q1, ..."""

    def next(self) -> QuerySpec:
        query = self.queries[self._index % len(self.queries)]
        self._index += 1
        return query


class WeightedRandomSelector(QuerySelector):
    """Select queries randomly based on weights."""

    def __init__(self, queries: List[QuerySpec], seed: Optional[int] = None):
        super().__init__(queries, seed)
        self._rng = random.Random(seed)
        self._weights = [q.weight for q in queries]

    def next(self) -> QuerySpec:
        return self._rng.choices(self.queries, weights=self._weights, k=1)[0]

    def reset(self) -> None:
        super().reset()
        self._rng = random.Random(self.seed)


class RoundRobinSelector(QuerySelector):
    """Select queries proportionally to weights in round-robin fashion.

    Example: Q1(weight=2), Q2(weight=1) -> Q1, Q1, Q2, Q1, Q1, Q2, ...
    """

    def __init__(self, queries: List[QuerySpec], seed: Optional[int] = None):
        super().__init__(queries, seed)
        # Build expanded list based on weights
        self._expanded: List[QuerySpec] = []
        for q in queries:
            self._expanded.extend([q] * q.weight)

    def next(self) -> QuerySpec:
        query = self._expanded[self._index % len(self._expanded)]
        self._index += 1
        return query


def create_selector(
    strategy: SelectionStrategy,
    queries: List[QuerySpec],
    seed: Optional[int] = None
) -> QuerySelector:
    """Factory to create appropriate selector.

    Args:
        strategy: Selection strategy
        queries: List of query specs
        seed: Random seed for reproducibility

    Returns:
        QuerySelector instance
    """
    if strategy == SelectionStrategy.WEIGHTED_RANDOM:
        return WeightedRandomSelector(queries, seed)
    elif strategy == SelectionStrategy.ROUND_ROBIN:
        return RoundRobinSelector(queries, seed)
    return SequentialSelector(queries, seed)
