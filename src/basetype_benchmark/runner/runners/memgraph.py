"""Memgraph query runner using neo4j driver (Bolt protocol).

Sprint 3 - Benchmark BaseType V3

Supports M1 (standalone) and M2 (hybrid with TimescaleDB) paradigms with:
- Cypher query execution
- Query profiling (PROFILE)
- Timeout handling
"""
from __future__ import annotations

import time
from typing import Any

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import (
    ServiceUnavailable,
    SessionExpired,
    TransientError,
    ClientError,
)

from ..config import MemgraphConfig
from .base import BaseRunner, RunResult, RunStatus, register_runner


class MemgraphRunner(BaseRunner):
    """Query runner for Memgraph (M1, M2 paradigms).

    Uses the neo4j Python driver (Bolt protocol) for Cypher execution.
    Memgraph is Bolt-compatible so the neo4j driver works.

    Example:
        ```python
        config = MemgraphConfig(uri="bolt://localhost:7687")
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
        self._driver: Driver | None = None

    def _get_driver(self) -> Driver:
        """Get or create database driver."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.config.uri,
                auth=self.config.auth,
            )
            self._connected = True
        return self._driver

    def _get_session(self) -> Session:
        """Get a new session."""
        driver = self._get_driver()
        return driver.session()

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
            with self._get_session() as session:
                # neo4j driver handles timeout via connection config
                # For per-query timeout, we rely on the database's query timeout
                result = session.run(query, params)

                # Collect all records
                rows = []
                for record in result:
                    # Convert neo4j Record to dict
                    row = dict(record)
                    # Convert Node/Relationship objects to dicts
                    row = self._convert_neo4j_types(row)
                    rows.append(row)

                duration_ms = (time.perf_counter() - start) * 1000

                return RunResult(
                    rows=rows,
                    duration_ms=duration_ms,
                    status=RunStatus.SUCCESS,
                    row_count=len(rows),
                )

        except (ServiceUnavailable, SessionExpired) as e:
            duration_ms = (time.perf_counter() - start) * 1000
            self._connected = False
            return self._make_error_result(e, duration_ms)

        except TransientError as e:
            duration_ms = (time.perf_counter() - start) * 1000
            error_msg = str(e).lower()

            if "timeout" in error_msg:
                return RunResult(
                    rows=[],
                    duration_ms=duration_ms,
                    status=RunStatus.TIMEOUT,
                    error_message=str(e),
                )
            return self._make_error_result(e, duration_ms)

        except ClientError as e:
            duration_ms = (time.perf_counter() - start) * 1000
            error_msg = str(e).lower()

            # Memgraph OOM detection
            if "memory" in error_msg or "allocation" in error_msg:
                return RunResult(
                    rows=[],
                    duration_ms=duration_ms,
                    status=RunStatus.OOM,
                    error_message=str(e),
                )
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
            with self._get_session() as session:
                result = session.run("RETURN 1 AS test")
                result.single()
            return True
        except Exception:
            self._connected = False
            return False

    def close(self) -> None:
        """Close database driver."""
        if self._driver is not None:
            self._driver.close()
        self._driver = None
        self._connected = False

    def get_query_plan(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> dict | None:
        """Get PROFILE output for a query.

        Note: In Memgraph, PROFILE actually executes the query.
        Use EXPLAIN for plan without execution.

        Args:
            query: Cypher query to analyze
            params: Query parameters

        Returns:
            Query profile as dict
        """
        try:
            with self._get_session() as session:
                # EXPLAIN doesn't execute, PROFILE does
                explain_query = f"EXPLAIN {query}"
                result = session.run(explain_query, params or {})

                plan_rows = []
                for record in result:
                    plan_rows.append(dict(record))

                if plan_rows:
                    return {"plan": plan_rows}
                return None

        except Exception:
            return None

    def _convert_neo4j_types(self, obj: Any) -> Any:
        """Convert neo4j types to Python native types.

        Args:
            obj: Object to convert

        Returns:
            Converted object
        """
        if hasattr(obj, "__iter__") and not isinstance(obj, (str, dict)):
            if isinstance(obj, dict):
                return {k: self._convert_neo4j_types(v) for k, v in obj.items()}
            return [self._convert_neo4j_types(item) for item in obj]

        # Convert Node to dict
        if hasattr(obj, "labels") and hasattr(obj, "items"):
            return {
                "_labels": list(obj.labels),
                **dict(obj.items()),
            }

        # Convert Relationship to dict
        if hasattr(obj, "type") and hasattr(obj, "items") and hasattr(obj, "start_node"):
            return {
                "_type": obj.type,
                **dict(obj.items()),
            }

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
