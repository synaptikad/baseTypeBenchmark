"""PostgreSQL query runner using psycopg3.

Sprint 3 - Benchmark BaseType V3

Supports P1 (relational) and P2 (JSONB) paradigms with:
- Parameterized queries
- Query timeout handling
- EXPLAIN support for query plans
- Connection pooling (optional)
"""
from __future__ import annotations

import json
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

        # Schema isolation for Option A (addendum.md section 1)
        # Set search_path so queries automatically resolve to correct schema
        paradigm_lower = paradigm.lower()
        self.search_path = f"{paradigm_lower}, ts, public"

    def _get_connection(self) -> psycopg.Connection:
        """Get or create database connection with schema-specific search_path."""
        need_new_connection = self._conn is None or self._conn.closed

        # Also check if connection is actually usable (handles container restarts)
        if not need_new_connection and self._conn is not None:
            try:
                # Quick ping to verify connection is alive
                self._conn.execute("SELECT 1")
            except Exception:
                # Connection lost (e.g., container restarted)
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None
                need_new_connection = True

        if need_new_connection:
            self._conn = psycopg.connect(
                self.config.dsn,
                row_factory=dict_row,
                autocommit=True,
            )

            # Set search_path for schema isolation (Option A)
            # This makes queries like "SELECT * FROM edges" resolve to:
            # - p1.edges for P1 paradigm
            # - p2.edges for P2 paradigm
            # - ts.timeseries for both (shared)
            with self._conn.cursor() as cur:
                cur.execute(f"SET search_path TO {self.search_path};")

            self._connected = True
        return self._conn

    def execute(
        self,
        query: str,
        params: dict[str, Any] | tuple | None = None,
        timeout_seconds: float = 300.0,
        query_id: str | None = None,
    ) -> RunResult:
        """Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters (optional)
            timeout_seconds: Maximum execution time
            query_id: Optional query ID for catalog lookup (for parameter ordering)

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
                # Convert dict params and query to psycopg format
                converted_query, converted_params = self._convert_params(params, query, query_id)
                cursor = conn.execute(converted_query, converted_params)
            else:
                cursor = conn.execute(query)

            # Fetch results (handle write queries that don't return rows)
            try:
                rows = cursor.fetchall()
                row_count = len(rows)
            except psycopg.ProgrammingError:
                # INSERT/UPDATE/DELETE don't return rows - use rowcount
                rows = []
                row_count = cursor.rowcount if cursor.rowcount >= 0 else 0

            duration_ms = (time.perf_counter() - start) * 1000

            return RunResult(
                rows=rows,
                duration_ms=duration_ms,
                status=RunStatus.SUCCESS,
                row_count=row_count,
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

            if params:
                converted_query, converted_params = self._convert_params(params, query)
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {converted_query}"
                cursor = conn.execute(explain_query, converted_params)
            else:
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
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

    def _convert_params(
        self,
        params: dict[str, Any] | tuple,
        query: str,
        query_id: str | None = None,
    ) -> tuple[str, tuple | dict]:
        """Convert parameter dict/tuple and query to format suitable for psycopg.

        psycopg3 supports positional (%s) and named (%(name)s) params.
        PostgreSQL native $1, $2 style must be converted to %s.

        Args:
            params: Parameter dictionary or tuple (if already ordered)
            query: Query string (to detect param style)
            query_id: Optional query ID for catalog lookup (parameter ordering)

        Returns:
            Tuple of (converted_query, converted_params)
        """
        import re

        def strip_sql_comments(sql: str) -> str:
            """Remove SQL comments (-- style) before placeholder conversion."""
            lines = []
            for line in sql.split('\n'):
                # Remove -- comments (keep everything before --)
                if '--' in line:
                    line = line.split('--')[0]
                lines.append(line)
            return '\n'.join(lines)

        def convert_positional_to_psycopg(sql: str, param_values: list) -> tuple[str, tuple]:
            """Convert PostgreSQL $N placeholders to psycopg %s format.

            Handles cases where the same placeholder ($1) is used multiple times
            by building a param list that repeats values as needed.

            Args:
                sql: Query with $N style placeholders (comments already stripped)
                param_values: List of values in order [value_for_$1, value_for_$2, ...]

            Returns:
                Tuple of (converted_query, param_tuple)
            """
            # Find all $N occurrences in order of appearance
            placeholders_in_order = re.findall(r'\$(\d+)', sql)

            # Build param list matching each %s placeholder
            expanded_params = []
            for placeholder_num in placeholders_in_order:
                idx = int(placeholder_num) - 1  # $1 -> index 0
                if idx < len(param_values):
                    expanded_params.append(param_values[idx])

            # Replace all $N with %s
            converted = re.sub(r'\$(\d+)', '%s', sql)
            return converted, tuple(expanded_params)

        # If params is already a tuple, use it directly for positional binding
        if isinstance(params, tuple):
            if "$1" in query:
                # Strip comments to avoid converting placeholders in comments
                clean_query = strip_sql_comments(query)
                converted_query, expanded_params = convert_positional_to_psycopg(
                    clean_query, list(params)
                )
                return converted_query, expanded_params
            return query, params

        # If query uses %(name)s style, serialize dict values to JSON for JSONB params
        if "%(" in query:
            serialized_params = {}
            for key, value in params.items():
                if isinstance(value, dict):
                    # psycopg3 cannot adapt dict directly - serialize to JSON string
                    serialized_params[key] = json.dumps(value)
                else:
                    serialized_params[key] = value
            return query, serialized_params

        # If query uses $1, $2 style (PostgreSQL native), convert to psycopg format
        if "$1" in query:
            # Strip comments to avoid converting placeholders in comments
            clean_query = strip_sql_comments(query)

            # Get parameter order from catalog if available
            param_values = []
            if query_id:
                try:
                    from ..core.catalog import get_catalog
                    catalog = get_catalog()
                    query_def = catalog.get_query(query_id)
                    if query_def and query_def.parameter_order:
                        # Use catalog-defined parameter order
                        param_order = query_def.parameter_order
                        param_values = [params.get(p) for p in param_order if p in params]
                except Exception:
                    pass  # Fall through to fallback

            # Fallback if no catalog lookup or no params found
            if not param_values:
                keys = list(params.keys())
                for i in range(1, 100):  # Reasonable upper limit
                    placeholder = f"${i}"
                    if placeholder not in query:
                        break
                    # Use dict key order (may not be correct!)
                    if i - 1 < len(keys):
                        param_values.append(params[keys[i - 1]])

            # Convert with proper handling of repeated placeholders
            converted_query, expanded_params = convert_positional_to_psycopg(
                clean_query, param_values
            )
            return converted_query, expanded_params

        # Default: return query and params as-is (no params or unknown style)
        return query, params

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
