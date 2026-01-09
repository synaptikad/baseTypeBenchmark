"""Memgraph query runner using pymgclient (native C driver).

Sprint 3 - Benchmark BaseType V3

Supports M1 (standalone) and M2 (hybrid with TimescaleDB) paradigms with:
- Cypher query execution via native driver
- Query profiling (EXPLAIN)
- Timeout handling

Uses pymgclient (official Memgraph driver) for optimal performance.
"""
from __future__ import annotations

import time
from typing import Any

import mgclient

from ..config import MemgraphConfig
from .base import BaseRunner, RunResult, RunStatus, register_runner


class MemgraphRunner(BaseRunner):
    """Query runner for Memgraph (M1, M2 paradigms).

    Uses pymgclient (official Memgraph C driver) for Cypher execution.
    This is the recommended driver for production Memgraph usage.

    Example:
        ```python
        config = MemgraphConfig(host="localhost", port=7687)
        runner = MemgraphRunner(config, paradigm="M1")

        if runner.check_connection():
            result = runner.execute(
                "MATCH (n:Node {id: $id}) RETURN n",
                {"id": "node_123"},
            )
            print(f"Got {result.row_count} rows")

        runner.close()
        ```
    """

    def __init__(self, config: MemgraphConfig, paradigm: str = "M1"):
        """Initialize Memgraph runner.

        Args:
            config: Memgraph connection configuration
            paradigm: M1 or M2
        """
        super().__init__(paradigm)
        self.config = config
        self._conn: mgclient.Connection | None = None

    def _get_connection(self) -> mgclient.Connection:
        """Get or create database connection."""
        if self._conn is None or not self._is_connection_alive():
            # Parse host/port from URI (bolt://host:port)
            host = "localhost"
            port = 7687

            uri = self.config.uri
            if uri.startswith("bolt://"):
                uri = uri[7:]
            if ":" in uri:
                parts = uri.split(":", 1)
                host = parts[0]
                port = int(parts[1])
            else:
                host = uri

            # Extract auth if present
            username = ""
            password = ""
            if self.config.auth:
                username, password = self.config.auth

            self._conn = mgclient.connect(
                host=host,
                port=port,
                username=username,
                password=password,
                lazy=False,  # Eager connection
            )
            self._connected = True
        return self._conn

    def _is_connection_alive(self) -> bool:
        """Check if the connection is still valid."""
        if self._conn is None:
            return False
        try:
            cursor = self._conn.cursor()
            cursor.execute("RETURN 1")
            cursor.fetchall()
            return True
        except Exception:
            return False

    def execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
    ) -> RunResult:
        """Execute a Cypher query.

        Args:
            query: Cypher query string
            params: Query parameters (optional)
            timeout_seconds: Maximum execution time

        Returns:
            RunResult with rows, timing, and status
        """
        start = time.perf_counter()
        params = params or {}

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Execute query with parameters
            cursor.execute(query, params)

            # Fetch all results
            # mgclient.Column has .name attribute, not index [0]
            columns = [col.name for col in cursor.description] if cursor.description else []
            raw_rows = cursor.fetchall()

            # Convert to list of dicts
            rows = []
            for raw_row in raw_rows:
                row = {}
                for i, col in enumerate(columns):
                    row[col] = self._convert_mgclient_types(raw_row[i])
                rows.append(row)

            duration_ms = (time.perf_counter() - start) * 1000

            return RunResult(
                rows=rows,
                duration_ms=duration_ms,
                status=RunStatus.SUCCESS,
                row_count=len(rows),
            )

        except mgclient.DatabaseError as e:
            duration_ms = (time.perf_counter() - start) * 1000
            error_msg = str(e).lower()

            # OOM detection
            if "memory" in error_msg or "allocation" in error_msg:
                return RunResult(
                    rows=[],
                    duration_ms=duration_ms,
                    status=RunStatus.OOM,
                    error_message=str(e),
                )

            # Timeout detection
            if "timeout" in error_msg:
                return RunResult(
                    rows=[],
                    duration_ms=duration_ms,
                    status=RunStatus.TIMEOUT,
                    error_message=str(e),
                )

            return self._make_error_result(e, duration_ms)

        except mgclient.InterfaceError as e:
            duration_ms = (time.perf_counter() - start) * 1000
            self._connected = False
            self._conn = None
            return self._make_error_result(e, duration_ms)

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return self._make_error_result(e, duration_ms)

    def execute_with_profile(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> tuple[RunResult, dict | None]:
        """Execute query and return results with PROFILE.

        Args:
            query: Cypher query string
            params: Query parameters

        Returns:
            Tuple of (RunResult, profile_info)
        """
        # First get the profile
        profile = self.get_query_plan(query, params)

        # Then execute normally
        result = self.execute(query, params)

        return result, profile

    def check_connection(self) -> bool:
        """Check if Memgraph connection is alive.

        Returns:
            True if connected and responsive
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("RETURN 1 AS test")
            cursor.fetchall()
            return True
        except Exception:
            self._connected = False
            self._conn = None
            return False

    def close(self) -> None:
        """Close database connection."""
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
        self._conn = None
        self._connected = False

    def get_query_plan(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> dict | None:
        """Get EXPLAIN output for a query.

        Note: In Memgraph, EXPLAIN shows the plan without execution.
        PROFILE executes and shows actual metrics.

        Args:
            query: Cypher query to analyze
            params: Query parameters

        Returns:
            Query plan as dict
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            explain_query = f"EXPLAIN {query}"
            cursor.execute(explain_query, params or {})

            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            raw_rows = cursor.fetchall()

            plan_rows = []
            for raw_row in raw_rows:
                row = {}
                for i, col in enumerate(columns):
                    row[col] = raw_row[i]
                plan_rows.append(row)

            if plan_rows:
                return {"plan": plan_rows}
            return None

        except Exception:
            return None

    def _convert_mgclient_types(self, obj: Any) -> Any:
        """Convert mgclient types to Python native types.

        Args:
            obj: Object to convert

        Returns:
            Converted object
        """
        # Handle Node
        if isinstance(obj, mgclient.Node):
            return {
                "_id": obj.id,
                "_labels": list(obj.labels),
                **obj.properties,
            }

        # Handle Relationship
        if isinstance(obj, mgclient.Relationship):
            return {
                "_id": obj.id,
                "_type": obj.type,
                "_start": obj.start_id,
                "_end": obj.end_id,
                **obj.properties,
            }

        # Handle Path
        if isinstance(obj, mgclient.Path):
            return {
                "nodes": [self._convert_mgclient_types(n) for n in obj.nodes],
                "relationships": [self._convert_mgclient_types(r) for r in obj.relationships],
            }

        # Handle lists
        if isinstance(obj, (list, tuple)):
            return [self._convert_mgclient_types(item) for item in obj]

        # Handle dicts
        if isinstance(obj, dict):
            return {k: self._convert_mgclient_types(v) for k, v in obj.items()}

        # Return as-is for primitive types
        return obj

    def __enter__(self) -> "MemgraphRunner":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - close connection."""
        self.close()


# Register for M1 and M2 paradigms
@register_runner("M1")
class MemgraphRunnerM1(MemgraphRunner):
    """Memgraph runner for M1 (standalone) paradigm."""

    def __init__(self, config: MemgraphConfig):
        super().__init__(config, paradigm="M1")


@register_runner("M2")
class MemgraphRunnerM2(MemgraphRunner):
    """Memgraph runner for M2 (hybrid) paradigm.

    Note: M2 hybrid execution is handled by HybridRunner,
    this class is for direct Memgraph queries only.
    """

    def __init__(self, config: MemgraphConfig):
        super().__init__(config, paradigm="M2")
