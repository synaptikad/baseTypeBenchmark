"""Cypher parameter generator for Memgraph paradigms (M1, M2).

This module implements parameter generation for Cypher-based scenarios:
- M1: Pure graph with embedded timeseries (ArchiveDay nodes)
- M2: Hybrid graph + TimescaleDB for timeseries

Cypher-specific conventions:
- Pattern matching: STARTS WITH 'prefix' (no wildcard character needed)
- Date format: Unix timestamp as integer (Cypher handles epoch natively)
- Timeseries: M1 embeds in chunks, M2 delegates to TimescaleDB
"""

from .base import ParamGenerator


class CypherParamGenerator(ParamGenerator):
    """Parameter generator for Cypher paradigm (Memgraph M1/M2).

    Cypher uses STARTS WITH for prefix matching without wildcards.
    Dates are passed as Unix timestamps (integers) which Cypher handles natively.

    Example query patterns:
        M1: WHERE node.space_type STARTS WITH 'office_'
        M2: WHERE node.space_type STARTS WITH 'office_'

    Cypher also supports regex via =~ but STARTS WITH is more efficient
    for prefix matching and represents idiomatic Cypher usage.
    """

    paradigm = "cypher"
    scenarios = ["M1", "M2"]

    def transform_space_type(self, prefix: str, is_exact: bool = False) -> str:
        """Transform space type for Cypher STARTS WITH.

        Cypher's STARTS WITH operator doesn't use wildcards - it simply
        checks if a string starts with the given prefix. For exact matches,
        the query uses = instead of STARTS WITH.

        Args:
            prefix: Base prefix (e.g., "office_")
            is_exact: If True, return as-is for exact equality matching

        Returns:
            Prefix string (no transformation needed for Cypher)

        Examples:
            transform_space_type("office_") -> "office_"
            transform_space_type("conference", is_exact=True) -> "conference"

        Note:
            The query decides whether to use STARTS WITH or = based on
            whether the value contains wildcards. Since we don't add
            wildcards, queries should use STARTS WITH for prefixes
            and = for exact matches.
        """
        # Cypher STARTS WITH doesn't need wildcards
        return prefix

    def format_date(self, timestamp: int) -> str:
        """Format timestamp as Unix epoch for Cypher.

        Memgraph/Neo4j handle Unix timestamps natively. Passing integers
        avoids string parsing overhead and timezone ambiguity.

        For M1 (embedded timeseries), timestamps index into ArchiveDay chunks.
        For M2 (hybrid), timestamps are passed to TimescaleDB queries.

        Args:
            timestamp: Unix timestamp (seconds since epoch)

        Returns:
            Unix timestamp as string (for query substitution)

        Note:
            Returns string representation since substitute_params() converts
            all values to strings. The query can cast if needed.
        """
        return str(int(timestamp))
