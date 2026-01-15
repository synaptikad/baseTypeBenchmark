"""Parameter binding for different query dialects.

Handles conversion of parameter values to database-specific formats.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Optional, Sequence

import yaml
from pydantic import BaseModel, Field

from .query import QueryDialect


class ParameterValue(BaseModel):
    """A parameter value with type information."""
    name: str
    value: Any
    param_type: str = "string"

    def as_string(self) -> str:
        """Convert to string representation."""
        if self.value is None:
            return "NULL"
        return str(self.value)

    def as_sql(self) -> Any:
        """Convert to SQL-compatible value."""
        if self.param_type == "timestamp":
            return self._parse_timestamp()
        if self.param_type == "date":
            return self._parse_date()
        if self.param_type == "integer":
            return int(self.value) if self.value is not None else None
        if self.param_type == "float":
            return float(self.value) if self.value is not None else None
        if self.param_type == "boolean":
            return bool(self.value) if self.value is not None else None
        if self.param_type == "array":
            return list(self.value) if self.value is not None else []
        return self.value

    def as_cypher(self) -> Any:
        """Convert to Cypher-compatible value."""
        # Cypher handles most types natively
        if self.param_type == "timestamp":
            # Cypher datetime format
            ts = self._parse_timestamp()
            if ts:
                return ts.isoformat()
        return self.as_sql()

    def _parse_timestamp(self) -> Optional[datetime]:
        """Parse timestamp from various formats."""
        if self.value is None:
            return None
        if isinstance(self.value, datetime):
            return self.value
        if isinstance(self.value, str):
            # Try ISO format
            try:
                return datetime.fromisoformat(self.value.replace('Z', '+00:00'))
            except ValueError:
                pass
            # Try common formats
            for fmt in [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
            ]:
                try:
                    return datetime.strptime(self.value, fmt)
                except ValueError:
                    continue
        return None

    def _parse_date(self) -> Optional[date]:
        """Parse date from various formats."""
        if self.value is None:
            return None
        if isinstance(self.value, date):
            return self.value
        if isinstance(self.value, datetime):
            return self.value.date()
        if isinstance(self.value, str):
            try:
                return datetime.strptime(self.value, "%Y-%m-%d").date()
            except ValueError:
                pass
        return None


class ParameterSet(BaseModel):
    """Set of parameters for a query execution."""
    query_id: str
    parameters: dict[str, ParameterValue] = Field(default_factory=dict)

    def add(self, name: str, value: Any, param_type: str = "string") -> None:
        """Add a parameter."""
        self.parameters[name] = ParameterValue(
            name=name,
            value=value,
            param_type=param_type
        )

    def get(self, name: str) -> Optional[ParameterValue]:
        """Get a parameter by name."""
        return self.parameters.get(name)

    def to_sql_params(self) -> dict[str, Any]:
        """Convert to SQL parameter dict."""
        return {name: p.as_sql() for name, p in self.parameters.items()}

    def to_cypher_params(self) -> dict[str, Any]:
        """Convert to Cypher parameter dict."""
        return {name: p.as_cypher() for name, p in self.parameters.items()}

    def to_dialect(self, dialect: QueryDialect) -> dict[str, Any]:
        """Convert to dialect-specific parameters."""
        if dialect == QueryDialect.SQL:
            return self.to_sql_params()
        elif dialect == QueryDialect.CYPHER:
            return self.to_cypher_params()
        return self.to_sql_params()


class ParameterBinder(ABC):
    """Abstract base for dialect-specific parameter binding."""

    @abstractmethod
    def bind(self, query: str, params: ParameterSet) -> tuple[str, Sequence[Any]]:
        """Bind parameters to query.

        Returns:
            Tuple of (query with placeholders, ordered parameter values)
        """
        ...

    @abstractmethod
    def get_placeholder(self, name: str, index: int) -> str:
        """Get placeholder for a parameter."""
        ...


class SQLParameterBinder(ParameterBinder):
    """Parameter binder for SQL (PostgreSQL style).

    Supports both named (:name) and positional ($1) placeholders.
    """

    def __init__(self, style: str = "named"):
        """Initialize with placeholder style.

        Args:
            style: "named" for :name, "positional" for $1, $2, etc.
        """
        self.style = style

    def bind(self, query: str, params: ParameterSet) -> tuple[str, Sequence[Any]]:
        """Bind parameters to SQL query."""
        sql_params = params.to_sql_params()

        if self.style == "positional":
            # Convert :name to $1, $2, etc.
            bound_query = query
            ordered_values = []
            for i, (name, value) in enumerate(sql_params.items(), 1):
                pattern = rf":{name}\b"
                if re.search(pattern, bound_query):
                    bound_query = re.sub(pattern, f"${i}", bound_query)
                    ordered_values.append(value)
            return bound_query, ordered_values
        else:
            # Named style - return dict
            return query, sql_params  # type: ignore

    def get_placeholder(self, name: str, index: int) -> str:
        """Get SQL placeholder."""
        if self.style == "positional":
            return f"${index}"
        return f":{name}"


class CypherParameterBinder(ParameterBinder):
    """Parameter binder for Cypher (Memgraph/Neo4j style).

    Uses $name placeholders.
    """

    def bind(self, query: str, params: ParameterSet) -> tuple[str, dict[str, Any]]:
        """Bind parameters to Cypher query."""
        cypher_params = params.to_cypher_params()
        # Cypher uses $name - convert :name if present
        bound_query = query
        for name in cypher_params:
            bound_query = re.sub(rf":{name}\b", f"${name}", bound_query)
        return bound_query, cypher_params

    def get_placeholder(self, name: str, index: int) -> str:
        """Get Cypher placeholder."""
        return f"${name}"


def get_binder(dialect: QueryDialect) -> ParameterBinder:
    """Get the appropriate parameter binder for a dialect."""
    if dialect == QueryDialect.SQL:
        return SQLParameterBinder(style="named")
    elif dialect == QueryDialect.CYPHER:
        return CypherParameterBinder()
    raise ValueError(f"Unknown dialect: {dialect}")
