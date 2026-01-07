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

            # Substitute parameters into query
            sparql = self._substitute_params(query, params or {})

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

    def _substitute_params(self, query: str, params: dict[str, Any]) -> str:
        """Substitute parameters into SPARQL query.

        SPARQL doesn't have standard parameterized queries, so we do
        string substitution. Uses $param_name or ?param_name syntax.

        Args:
            query: SPARQL query with placeholders
            params: Parameters to substitute

        Returns:
            Query with substituted values
        """
        result = query

        for key, value in params.items():
            # Format value based on type
            if isinstance(value, str):
                # Escape and quote string
                escaped = value.replace("\\", "\\\\").replace('"', '\\"')
                formatted = f'"{escaped}"'
            elif isinstance(value, bool):
                formatted = "true" if value else "false"
            elif isinstance(value, (int, float)):
                formatted = str(value)
            elif isinstance(value, list):
                # For lists, create a VALUES block substitution
                # This is a special case - caller should handle
                formatted = str(value)
            else:
                formatted = f'"{value}"'

            # Replace $key and ?key placeholders
            result = result.replace(f"${key}", formatted)
            result = result.replace(f"?{key}", formatted)

        return result

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
