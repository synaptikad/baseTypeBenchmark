"""SPARQL parameter generator for Oxigraph paradigms (O1, O2).

This module implements parameter generation for SPARQL-based scenarios:
- O1: Pure RDF with embedded timeseries (reification or named graphs)
- O2: Hybrid RDF + TimescaleDB for timeseries

SPARQL-specific conventions:
- Pattern matching: STRSTARTS(?var, "prefix") or REGEX(?var, "^prefix")
- Date format: xsd:date (YYYY-MM-DD) or xsd:dateTime for semantic queries
- URI construction: <http://basetype.benchmark/entity_id>
"""

from datetime import datetime, timezone

from .base import ParamGenerator


class SPARQLParamGenerator(ParamGenerator):
    """Parameter generator for SPARQL paradigm (Oxigraph O1/O2).

    SPARQL uses STRSTARTS for prefix matching (most efficient) or REGEX
    for complex patterns. Dates follow XSD datatypes for semantic precision.

    Example query patterns:
        O1/O2: FILTER(STRSTARTS(?spaceType, "office_"))
        Alternative: FILTER(REGEX(?spaceType, "^office_"))

    STRSTARTS is preferred over REGEX for simple prefix matching as it's
    more efficient and explicitly communicates intent.
    """

    paradigm = "sparql"
    scenarios = ["O1", "O2"]

    def transform_space_type(self, prefix: str, is_exact: bool = False) -> str:
        """Transform space type for SPARQL STRSTARTS.

        SPARQL's STRSTARTS function checks if a string starts with a prefix.
        No wildcards are needed - the function handles prefix matching natively.

        Args:
            prefix: Base prefix (e.g., "office_")
            is_exact: If True, return as-is for exact equality matching

        Returns:
            Prefix string (no transformation needed for STRSTARTS)

        Examples:
            transform_space_type("office_") -> "office_"
            transform_space_type("conference", is_exact=True) -> "conference"

        Query usage:
            FILTER(STRSTARTS(?spaceType, "office_"))  # Prefix match
            FILTER(?spaceType = "conference")          # Exact match
        """
        # SPARQL STRSTARTS doesn't need wildcards
        return prefix

    def format_date(self, timestamp: int) -> str:
        """Format timestamp as xsd:date for SPARQL.

        SPARQL semantic queries typically use xsd:date or xsd:dateTime.
        For benchmark consistency and simpler queries, we use xsd:date format.

        For O1 (embedded timeseries), dates filter RDF statements.
        For O2 (hybrid), dates are passed to TimescaleDB queries as ISO strings.

        Args:
            timestamp: Unix timestamp (seconds since epoch)

        Returns:
            XSD date string (YYYY-MM-DD format)

        Note:
            We use date-only format for cleaner SPARQL queries. If time
            precision is needed, queries should use xsd:dateTime with
            format_datetime() method.
        """
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")

    def format_datetime(self, timestamp: int) -> str:
        """Format timestamp as xsd:dateTime for SPARQL (with time component).

        Use this when queries need sub-day precision.

        Args:
            timestamp: Unix timestamp (seconds since epoch)

        Returns:
            XSD dateTime string (ISO 8601 with timezone)
        """
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
