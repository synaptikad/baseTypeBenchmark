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

    def as_sparql(self) -> str:
        """Convert to SPARQL literal."""
        if self.value is None:
            return "UNDEF"
        if self.param_type == "timestamp":
            ts = self._parse_timestamp()
            if ts:
                return f'"{ts.isoformat()}"^^xsd:dateTime'
        if self.param_type == "integer":
            return f'"{self.value}"^^xsd:integer'
        if self.param_type == "float":
            return f'"{self.value}"^^xsd:decimal'
        if self.param_type == "boolean":
            return "true" if self.value else "false"
        # Default: string literal
        escaped = str(self.value).replace('"', '\\"')
        return f'"{escaped}"'

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

    def to_sparql_bindings(self) -> dict[str, str]:
        """Convert to SPARQL BIND values."""
        return {name: p.as_sparql() for name, p in self.parameters.items()}

    def to_dialect(self, dialect: QueryDialect) -> dict[str, Any]:
        """Convert to dialect-specific parameters."""
        if dialect == QueryDialect.SQL:
            return self.to_sql_params()
        elif dialect == QueryDialect.CYPHER:
            return self.to_cypher_params()
        elif dialect == QueryDialect.SPARQL:
            return self.to_sparql_bindings()
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


class SPARQLParameterBinder(ParameterBinder):
    """Parameter binder for SPARQL.

    Uses ?name variables with BIND or VALUES clauses.
    """

    def __init__(self, use_values: bool = False):
        """Initialize SPARQL binder.

        Args:
            use_values: If True, use VALUES clause. Otherwise, use BIND.
        """
        self.use_values = use_values

    def bind(self, query: str, params: ParameterSet) -> tuple[str, dict[str, str]]:
        """Bind parameters to SPARQL query.

        For SPARQL, we inject BIND statements or VALUES clause.
        """
        sparql_bindings = params.to_sparql_bindings()

        if not sparql_bindings:
            return query, {}

        if self.use_values:
            # VALUES (?var1 ?var2) { (val1 val2) }
            vars_str = " ".join(f"?{name}" for name in sparql_bindings)
            vals_str = " ".join(sparql_bindings.values())
            values_clause = f"VALUES ({vars_str}) {{ ({vals_str}) }}"

            # Insert after WHERE {
            bound_query = re.sub(
                r"(WHERE\s*\{)",
                rf"\1\n  {values_clause}",
                query,
                flags=re.IGNORECASE
            )
        else:
            # BIND statements
            bind_statements = "\n  ".join(
                f"BIND({value} AS ?{name})"
                for name, value in sparql_bindings.items()
            )
            bound_query = re.sub(
                r"(WHERE\s*\{)",
                rf"\1\n  {bind_statements}",
                query,
                flags=re.IGNORECASE
            )

        return bound_query, sparql_bindings

    def get_placeholder(self, name: str, index: int) -> str:
        """Get SPARQL variable."""
        return f"?{name}"


def get_binder(dialect: QueryDialect) -> ParameterBinder:
    """Get the appropriate parameter binder for a dialect."""
    if dialect == QueryDialect.SQL:
        return SQLParameterBinder(style="named")
    elif dialect == QueryDialect.CYPHER:
        return CypherParameterBinder()
    elif dialect == QueryDialect.SPARQL:
        return SPARQLParameterBinder(use_values=False)
    raise ValueError(f"Unknown dialect: {dialect}")


class GoldenAnswersLoader:
    """Loads parameter values from golden_answers.yaml."""

    def __init__(self, golden_path: Optional[Path] = None):
        """Initialize loader.

        Args:
            golden_path: Path to golden_answers.yaml
        """
        if golden_path is None:
            golden_path = Path(__file__).parents[4] / "queries" / "golden_answers.yaml"
        self.golden_path = golden_path
        self._data: Optional[dict] = None

    def load(self) -> None:
        """Load golden answers file."""
        if self._data is not None:
            return

        with open(self.golden_path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

    def get_parameters(self, query_id: str) -> ParameterSet:
        """Get parameters for a query from golden answers."""
        self.load()

        param_set = ParameterSet(query_id=query_id)

        if self._data is None:
            return param_set

        queries = self._data.get("queries", {})
        query_data = queries.get(query_id, {})
        params_data = query_data.get("parameters", {})

        for name, value in params_data.items():
            # Infer type from value
            param_type = self._infer_type(value)
            param_set.add(name, value, param_type)

        return param_set

    def get_expected_results(self, query_id: str) -> Optional[list[dict]]:
        """Get expected results for validation."""
        self.load()

        if self._data is None:
            return None

        queries = self._data.get("queries", {})
        query_data = queries.get(query_id, {})
        return query_data.get("expected_results")

    def get_expected_count(self, query_id: str) -> Optional[int]:
        """Get expected row count."""
        self.load()

        if self._data is None:
            return None

        queries = self._data.get("queries", {})
        query_data = queries.get(query_id, {})
        return query_data.get("expected_count")

    def _infer_type(self, value: Any) -> str:
        """Infer parameter type from value."""
        if value is None:
            return "string"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "float"
        if isinstance(value, (list, tuple)):
            return "array"
        if isinstance(value, str):
            # Check if it looks like a timestamp
            if re.match(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", value):
                return "timestamp"
            if re.match(r"\d{4}-\d{2}-\d{2}$", value):
                return "date"
        return "string"

    def get_all_query_ids(self) -> list[str]:
        """Get all query IDs in golden answers."""
        self.load()

        if self._data is None:
            return []

        return list(self._data.get("queries", {}).keys())


# Singleton instance
_golden_loader: Optional[GoldenAnswersLoader] = None


def get_golden_loader() -> GoldenAnswersLoader:
    """Get global golden answers loader."""
    global _golden_loader
    if _golden_loader is None:
        _golden_loader = GoldenAnswersLoader()
    return _golden_loader


def get_query_parameters(query_id: str) -> ParameterSet:
    """Convenience function to get parameters for a query."""
    return get_golden_loader().get_parameters(query_id)
