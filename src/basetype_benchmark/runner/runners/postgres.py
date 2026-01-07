"""PostgreSQL query runner using psycopg3.

Sprint 3 - Benchmark BaseType V3

Supports P1 (relational) and P2 (JSONB) paradigms with:
- Parameterized queries
- Query timeout handling
- EXPLAIN support for query plans
- Connection pooling (optional)
"""
from __future__ import annotations

import time
from typing import Any

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from ..config import PostgresConfig
from .base import BaseRunner, RunResult, RunStatus, register_runner


class PostgresRunner(BaseRunner):
    """Query runner for PostgreSQL (P1, P2 paradigms).

    Uses psycopg3 (async-capable, modern PostgreSQL driver) for execution.

    Example:
        ```python
        config = PostgresConfig(dsn="postgresql://...")
        runner = PostgresRunner(config, paradigm="P1")

        if runner.check_connection():
            result = runner.execute(
                "SELECT * FROM nodes WHERE id = %s",
                {"id": "node_123"},
            )
            print(f"Got {result.row_count} rows")

        runner.close()
        ```
    """

    def __init__(self, config: PostgresConfig, paradigm: str = "P1"):
        """Initialize PostgreSQL runner.

        Args:
            config: PostgreSQL connection configuration
            paradigm: P1 or P2
        """
        super().__init__(paradigm)
        self.config = config
        self._conn: psycopg.Connection | None = None

    def _get_connection(self) -> psycopg.Connection:
        """Get or create database connection."""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg.connect(
                self.config.dsn,
                row_factory=dict_row,
                autocommit=True,
            )
            self._connected = True
        return self._conn

    def execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
    ) -> RunResult:
        """Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters (optional)
            timeout_seconds: Maximum execution time

        Returns:
            RunResult with rows, timing, and status
        """
        start = time.perf_counter()

        try:
            conn = self._get_connection()

            # Set statement timeout
            timeout_ms = int(timeout_seconds * 1000)
            conn.execute(f"SET statement_timeout = {timeout_ms}")

            # Execute query
            if params:
                # Convert dict params to positional for psycopg
                cursor = conn.execute(query, self._convert_params(params, query))
            else:
                cursor = conn.execute(query)

            # Fetch results
            rows = cursor.fetchall()
            duration_ms = (time.perf_counter() - start) * 1000

            return RunResult(
                rows=rows,
                duration_ms=duration_ms,
                status=RunStatus.SUCCESS,
                row_count=len(rows),
            )

        except psycopg.OperationalError as e:
            duration_ms = (time.perf_counter() - start) * 1000
            error_msg = str(e).lower()

            if "timeout" in error_msg or "cancel" in error_msg:
                return RunResult(
                    rows=[],
                    duration_ms=duration_ms,
                    status=RunStatus.TIMEOUT,
                    error_message=str(e),
                )
            return self._make_error_result(e, duration_ms)

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return self._make_error_result(e, duration_ms)

    def execute_with_explain(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> tuple[RunResult, dict | None]:
        """Execute query and return results with EXPLAIN ANALYZE.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Tuple of (RunResult, explain_plan)
        """
        # First get the plan
        plan = self.get_query_plan(query, params)

        # Then execute
        result = self.execute(query, params)

        return result, plan

    def check_connection(self) -> bool:
        """Check if PostgreSQL connection is alive.

        Returns:
            True if connected and responsive
        """
        try:
            conn = self._get_connection()
            conn.execute("SELECT 1")
            return True
        except Exception:
            self._connected = False
            return False

    def close(self) -> None:
        """Close database connection."""
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
        self._conn = None
        self._connected = False

    def get_query_plan(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> dict | None:
        """Get EXPLAIN ANALYZE output for a query.

        Args:
            query: SQL query to analyze
            params: Query parameters

        Returns:
            Query plan as dict with timing info
        """
        try:
            conn = self._get_connection()

            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

            if params:
                cursor = conn.execute(explain_query, self._convert_params(params, query))
            else:
                cursor = conn.execute(explain_query)

            result = cursor.fetchone()
            if result:
                # Result is a dict with QUERY PLAN key containing list
                plan_data = result.get("QUERY PLAN", result)
                if isinstance(plan_data, list) and len(plan_data) > 0:
                    return plan_data[0]
                return plan_data
            return None

        except Exception:
            return None

    def _convert_params(self, params: dict[str, Any], query: str) -> tuple | dict:
        """Convert parameter dict to format suitable for psycopg.

        psycopg3 supports both positional (%s, $1) and named (%(name)s) params.
        This method converts our dict to the appropriate format.

        Args:
            params: Parameter dictionary
            query: Query string (to detect param style)

        Returns:
            Parameters in format suitable for psycopg
        """
        # If query uses %(name)s style, return dict as-is
        if "%(" in query:
            return params

        # If query uses $1, $2 style (PostgreSQL native), convert to tuple
        if "$1" in query:
            # Extract positional params
            result = []
            for i in range(1, 100):  # Reasonable upper limit
                placeholder = f"${i}"
                if placeholder not in query:
                    break
                # Find param by name (assuming keys like "1", "2" or param names)
                param_key = str(i)
                if param_key in params:
                    result.append(params[param_key])
                else:
                    # Try to find by order in dict
                    keys = list(params.keys())
                    if i - 1 < len(keys):
                        result.append(params[keys[i - 1]])
            return tuple(result)

        # Default: return dict for named params
        return params

    def __enter__(self) -> "PostgresRunner":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - close connection."""
        self.close()


# Register for P1 and P2 paradigms
@register_runner("P1")
class PostgresRunnerP1(PostgresRunner):
    """PostgreSQL runner for P1 (relational) paradigm."""

    def __init__(self, config: PostgresConfig):
        super().__init__(config, paradigm="P1")


@register_runner("P2")
class PostgresRunnerP2(PostgresRunner):
    """PostgreSQL runner for P2 (JSONB) paradigm."""

    def __init__(self, config: PostgresConfig):
        super().__init__(config, paradigm="P2")
