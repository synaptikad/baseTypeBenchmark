"""Oxigraph query runner using SPARQL HTTP endpoint.

Sprint 3 - Benchmark BaseType V3

Supports O2 (hybrid with TimescaleDB) paradigm with:
- SPARQL query execution via HTTP
- JSON result parsing
- Timeout handling
"""
from __future__ import annotations

import time
from typing import Any

import httpx

from ..config import OxigraphConfig
from .base import BaseRunner, RunResult, RunStatus, register_runner


class OxigraphRunner(BaseRunner):
    """Query runner for Oxigraph (O2 paradigm).

    Uses SPARQL HTTP endpoint for query execution. Oxigraph exposes
    a standard SPARQL 1.1 endpoint.

    Example:
        ```python
        config = OxigraphConfig(
            query_endpoint="http://localhost:7878/query",
        )
        runner = OxigraphRunner(config)

        if runner.check_connection():
            result = runner.execute('''
                SELECT ?s ?p ?o
                WHERE { ?s ?p ?o }
                LIMIT 10
            ''')
            print(f"Got {result.row_count} rows")

        runner.close()
        ```
    """

    def __init__(self, config: OxigraphConfig, paradigm: str = "O2"):
        """Initialize Oxigraph runner.

        Args:
            config: Oxigraph connection configuration
            paradigm: Usually O2
        """
        super().__init__(paradigm)
        self.config = config
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                timeout=httpx.Timeout(self.config.timeout_seconds),
            )
            self._connected = True
        return self._client

    def execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
    ) -> RunResult:
        """Execute a SPARQL query.

        Args:
            query: SPARQL query string
            params: Query parameters (will be substituted into query)
            timeout_seconds: Maximum execution time

        Returns:
            RunResult with rows, timing, and status
        """
        start = time.perf_counter()

        try:
            client = self._get_client()

            # Inject VALUES clause for parameter binding
            sparql = self._inject_values_clause(query, params or {})

            # Execute query
            response = client.post(
                self.config.query_endpoint,
                data={"query": sparql},
                headers={
                    "Accept": "application/sparql-results+json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=timeout_seconds,
            )

            duration_ms = (time.perf_counter() - start) * 1000

            # Check response status
            if response.status_code != 200:
                error_msg = response.text[:500]
                if "timeout" in error_msg.lower():
                    return RunResult(
                        rows=[],
                        duration_ms=duration_ms,
                        status=RunStatus.TIMEOUT,
                        error_message=error_msg,
                    )
                return RunResult(
                    rows=[],
                    duration_ms=duration_ms,
                    status=RunStatus.ERROR,
                    error_message=f"HTTP {response.status_code}: {error_msg}",
                )

            # Parse JSON results
            rows = self._parse_sparql_json(response.json())

            return RunResult(
                rows=rows,
                duration_ms=duration_ms,
                status=RunStatus.SUCCESS,
                row_count=len(rows),
            )

        except httpx.TimeoutException as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return RunResult(
                rows=[],
                duration_ms=duration_ms,
                status=RunStatus.TIMEOUT,
                error_message=str(e),
            )

        except httpx.ConnectError as e:
            duration_ms = (time.perf_counter() - start) * 1000
            self._connected = False
            return self._make_error_result(e, duration_ms)

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return self._make_error_result(e, duration_ms)

    def check_connection(self) -> bool:
        """Check if Oxigraph endpoint is reachable.

        Returns:
            True if connected and responsive
        """
        try:
            client = self._get_client()

            # Simple ASK query to test connection
            response = client.post(
                self.config.query_endpoint,
                data={"query": "ASK { ?s ?p ?o }"},
                headers={
                    "Accept": "application/sparql-results+json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=10.0,
            )
            return response.status_code == 200
        except Exception:
            self._connected = False
            return False

    def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            self._client.close()
        self._client = None
        self._connected = False

    def get_query_plan(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> dict | None:
        """Get query execution plan.

        Note: Oxigraph doesn't expose EXPLAIN functionality via HTTP.

        Args:
            query: SPARQL query to analyze
            params: Query parameters

        Returns:
            None (not supported)
        """
        return None

    def _format_sparql_value(self, value: Any, param_type: str | None = None) -> str:
        """Format Python value as SPARQL literal.

        Args:
            value: Python value to format
            param_type: Optional type hint ("string", "integer", "timestamp", etc.)

        Returns:
            SPARQL-formatted literal
        """
        import re
        from datetime import datetime, date

        if value is None:
            return "UNDEF"

        # Date-only string (YYYY-MM-DD format) → xsd:date
        if isinstance(value, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            return f'"{value}"^^xsd:date'

        # Timestamp: "2024-06-01T00:00:00"^^xsd:dateTime
        if param_type == "timestamp" or (param_type is None and isinstance(value, datetime)):
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return f'"{dt.isoformat()}"^^xsd:dateTime'
                except ValueError:
                    pass
            elif isinstance(value, datetime):
                return f'"{value.isoformat()}"^^xsd:dateTime'

        # Date: "2024-06-01"^^xsd:date
        if param_type == "date" or (param_type is None and isinstance(value, date)):
            if isinstance(value, str):
                return f'"{value}"^^xsd:date'
            elif isinstance(value, date):
                return f'"{value.isoformat()}"^^xsd:date'

        # Integer: 123 (no quotes)
        if param_type == "integer" or (param_type is None and isinstance(value, int) and not isinstance(value, bool)):
            return str(value)

        # Float: 3.14 (no quotes)
        if param_type == "float" or (param_type is None and isinstance(value, float)):
            return str(value)

        # Boolean: true/false
        if param_type == "boolean" or isinstance(value, bool):
            return "true" if value else "false"

        # Default: string literal with escaping
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    def _inject_values_clause(
        self,
        query: str,
        params: dict[str, Any],
    ) -> str:
        """Inject VALUES clause for parameter binding in SPARQL.

        Uses VALUES (?var1 ?var2) { (val1 val2) } pattern injected after WHERE {
        to bind parameters without corrupting SPARQL variables.

        Args:
            query: SPARQL query text
            params: Parameters dict (keys normalized to camelCase for SPARQL)

        Returns:
            Query with VALUES clause injected

        Raises:
            ValueError: If WHERE clause missing or duplicate VALUES detected
        """
        if not params:
            return query

        import re

        # Step 1: Check for existing VALUES clauses that conflict
        for key in params.keys():
            if re.search(rf"VALUES\s+\?{key}\s*\{{", query, re.IGNORECASE):
                raise ValueError(
                    f"Query already contains VALUES clause for ?{key}. "
                    f"Remove hardcoded VALUES to use dynamic parameter binding."
                )

        # Step 2: Format values (assume simple types, no catalog lookup for now)
        # Keys are already normalized to camelCase by gradient.py
        formatted_values = {}
        for var_name, value in params.items():
            # Infer type from value (catalog lookup can be added later)
            formatted_values[var_name] = self._format_sparql_value(value, param_type=None)

        # Step 3: Build VALUES clause
        if len(formatted_values) == 1:
            # Single parameter: VALUES ?var { value }
            var_name = list(formatted_values.keys())[0]
            var_value = list(formatted_values.values())[0]
            values_clause = f"VALUES ?{var_name} {{ {var_value} }}"
        else:
            # Multiple parameters: VALUES (?var1 ?var2) { (val1 val2) }
            vars_str = " ".join(f"?{v}" for v in formatted_values.keys())
            vals_str = " ".join(formatted_values.values())
            values_clause = f"VALUES ({vars_str}) {{ ({vals_str}) }}"

        # Step 4: Inject after WHERE {
        pattern = r"(WHERE\s*\{)"

        if not re.search(pattern, query, re.IGNORECASE):
            raise ValueError(
                f"Cannot inject VALUES: query must contain WHERE {{ clause"
            )

        # Insert VALUES clause after WHERE { (only first occurrence)
        injected_query = re.sub(
            pattern,
            rf"\1\n    {values_clause}",
            query,
            count=1,
            flags=re.IGNORECASE
        )

        return injected_query

    def _parse_sparql_json(self, json_result: dict) -> list[dict[str, Any]]:
        """Parse SPARQL JSON results format to list of dicts.

        SPARQL JSON format:
        {
            "head": {"vars": ["s", "p", "o"]},
            "results": {
                "bindings": [
                    {"s": {"type": "uri", "value": "..."}, ...}
                ]
            }
        }

        Args:
            json_result: Parsed JSON response

        Returns:
            List of dictionaries with extracted values
        """
        rows = []

        # Handle ASK queries
        if "boolean" in json_result:
            return [{"result": json_result["boolean"]}]

        # Handle SELECT queries
        bindings = json_result.get("results", {}).get("bindings", [])

        for binding in bindings:
            row = {}
            for var, val_info in binding.items():
                row[var] = self._extract_sparql_value(val_info)
            rows.append(row)

        return rows

    def _extract_sparql_value(self, val_info: dict) -> Any:
        """Extract Python value from SPARQL binding.

        Args:
            val_info: SPARQL value info dict

        Returns:
            Extracted Python value
        """
        val_type = val_info.get("type", "literal")
        value = val_info.get("value", "")

        if val_type == "uri":
            # Return URI as string
            return value
        elif val_type == "bnode":
            # Blank node
            return f"_:{value}"
        elif val_type == "literal":
            # Check for datatype
            datatype = val_info.get("datatype", "")

            if "integer" in datatype:
                return int(value)
            elif "decimal" in datatype or "double" in datatype or "float" in datatype:
                return float(value)
            elif "boolean" in datatype:
                return value.lower() == "true"
            elif "dateTime" in datatype:
                # Return as string for now
                return value
            else:
                return value
        else:
            return value

    def __enter__(self) -> "OxigraphRunner":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - close connection."""
        self.close()


# Register for O2 paradigm
@register_runner("O2")
class OxigraphRunnerO2(OxigraphRunner):
    """Oxigraph runner for O2 (hybrid) paradigm.

    Note: O2 hybrid execution is handled by HybridRunner,
    this class is for direct SPARQL queries only.
    """

    def __init__(self, config: OxigraphConfig):
        super().__init__(config, paradigm="O2")
