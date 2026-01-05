"""SQL parameter generator for PostgreSQL paradigms (P1, P2).

This module implements parameter generation for SQL-based scenarios:
- P1: Normalized relational schema (direct column access)
- P2: JSONB flexible schema (properties->>'field' access)

Both P1 and P2 use identical parameter values since they share the same
SQL LIKE syntax for pattern matching. The schema difference (normalized vs JSONB)
affects query syntax, not parameter values.

SQL-specific conventions:
- Pattern matching: LIKE 'prefix%' (% = wildcard for zero or more characters)
- Date format: ISO 8601 (2024-01-01T00:00:00+00:00)
- String quoting: handled by query, params are raw values
"""

from datetime import datetime, timezone

from .base import ParamGenerator


class SQLParamGenerator(ParamGenerator):
    """Parameter generator for SQL paradigm (PostgreSQL P1/P2).

    SQL uses LIKE for pattern matching with % as wildcard.
    Dates are formatted as ISO 8601 strings for PostgreSQL timestamp parsing.

    Example query patterns:
        P1: WHERE space_type LIKE 'office_%'
        P2: WHERE properties->>'space_type' LIKE 'office_%'

    Both use the same parameter value: 'office_%'
    """

    paradigm = "sql"
    scenarios = ["P1", "P2"]

    def transform_space_type(self, prefix: str, is_exact: bool = False) -> str:
        """Transform space type for SQL LIKE pattern.

        Args:
            prefix: Base prefix (e.g., "office_")
            is_exact: If True, match exactly without wildcard

        Returns:
            SQL LIKE pattern with % wildcard if not exact

        Examples:
            transform_space_type("office_") -> "office_%"
            transform_space_type("conference", is_exact=True) -> "conference"
        """
        if is_exact:
            return prefix
        return f"{prefix}%"

    def format_date(self, timestamp: int) -> str:
        """Format timestamp as ISO 8601 for PostgreSQL.

        PostgreSQL accepts ISO 8601 format for timestamp/timestamptz columns.
        The ::timestamptz cast in queries handles timezone conversion.

        Args:
            timestamp: Unix timestamp (seconds since epoch)

        Returns:
            ISO 8601 formatted string (e.g., "2024-01-01T00:00:00+00:00")
        """
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
