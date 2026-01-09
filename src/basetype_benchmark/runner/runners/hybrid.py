"""Hybrid query runner for two-phase execution (M2, O2).

Sprint 3 - Benchmark BaseType V3

Orchestrates hybrid queries that require:
1. Graph phase: Execute Cypher/SPARQL to get point_ids
2. Timeseries phase: Execute SQL with collected point_ids

This is the core of the federated architecture described in papier.md
Section 3.6 "Architecture hybride federee".
"""
from __future__ import annotations

import time
from typing import Any, Union

from ..config import PostgresConfig, MemgraphConfig, OxigraphConfig
from .base import (
    BaseRunner,
    RunResult,
    RunStatus,
    HybridRunResult,
    HybridQueryRunner,
)
from .postgres import PostgresRunner
from .memgraph import MemgraphRunner
from .oxigraph import OxigraphRunner


class HybridRunner:
    """Two-phase query runner for hybrid paradigms (M2, O2).

    Implements the federated execution pattern:
    1. Execute graph query (Cypher or SPARQL) to identify point_ids
    2. Inject point_ids into timeseries query (SQL)
    3. Execute timeseries query and return combined results

    This approach:
    - Reflects real-world microservices architectures
    - Allows measuring the true cost of federation
    - Is academically rigorous (transparent overhead)

    Example:
        ```python
        # M2: Memgraph + TimescaleDB
        runner = HybridRunner(
            graph_runner=MemgraphRunner(memgraph_config),
            ts_runner=PostgresRunner(postgres_config),
            paradigm="M2",
        )

        result = runner.execute_hybrid(
            graph_query="MATCH (p:Point)-[:HAS_POINT]-(e:Equipment) RETURN p.id",
            ts_query="SELECT * FROM timeseries WHERE point_id = ANY($point_ids)",
            params={"equipment_id": "eq_123"},
        )
        print(f"Total: {result.total_ms}ms (graph: {result.graph_ms}ms, ts: {result.ts_ms}ms)")
        ```
    """

    # Column names that indicate point IDs in graph results
    POINT_ID_COLUMNS = ["point_id", "id", "pointId", "point"]

    def __init__(
        self,
        graph_runner: Union[MemgraphRunner, OxigraphRunner],
        ts_runner: PostgresRunner,
        paradigm: str = "M2",
    ):
        """Initialize hybrid runner.

        Args:
            graph_runner: Runner for graph queries (Memgraph or Oxigraph)
            ts_runner: Runner for timeseries queries (PostgreSQL/TimescaleDB)
            paradigm: M2 or O2
        """
        self.graph = graph_runner
        self.ts = ts_runner
        self.paradigm = paradigm

    def execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
    ) -> RunResult:
        """Execute a query - auto-detects query type and routes appropriately.

        This method is required for compatibility with the benchmark framework.
        It automatically detects whether the query is:
        - Graph-only (Cypher/SPARQL) → routes to graph runner
        - Timeseries-only (SQL) → routes to timeseries runner
        - Hybrid queries are not supported via this method; use execute_hybrid()

        Args:
            query: Query string (Cypher, SPARQL, or SQL)
            params: Query parameters
            timeout_seconds: Timeout

        Returns:
            RunResult from appropriate runner
        """
        # Simple detection based on query content
        query_lower = query.lower().strip()

        # Detect Cypher (M2)
        if any(keyword in query_lower[:100] for keyword in ['match ', 'create ', 'merge ', 'return ']):
            return self.graph.execute(query, params, timeout_seconds)

        # Detect SPARQL (O2)
        if any(keyword in query_lower[:100] for keyword in ['select ', 'construct ', 'describe ', 'ask ', 'prefix ']):
            # Check if it's SPARQL or SQL
            if 'where' in query_lower and '{' in query:
                # SPARQL has WHERE { ... } patterns
                return self.graph.execute(query, params, timeout_seconds)

        # Default: SQL query → timeseries
        return self.ts.execute(query, params, timeout_seconds)

    def execute_hybrid(
        self,
        graph_query: str,
        ts_query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
        point_id_column: str | None = None,
    ) -> HybridRunResult:
        """Execute a hybrid query in two phases.

        Phase 1 (Graph):
            Execute graph_query with params
            Extract point_ids from results

        Phase 2 (Timeseries):
            Inject point_ids into ts_query
            Execute and return results

        Args:
            graph_query: Cypher or SPARQL query
            ts_query: SQL query with $point_ids or %(point_ids)s placeholder
            params: Shared parameters for both queries
            timeout_seconds: Total timeout for both phases
            point_id_column: Column name for point IDs (auto-detected if None)

        Returns:
            HybridRunResult with timing breakdown
        """
        params = params or {}
        total_start = time.perf_counter()

        # Phase 1: Graph query
        graph_result = self._execute_graph_phase(
            graph_query,
            params,
            timeout_seconds,
        )

        if graph_result.status != RunStatus.SUCCESS:
            total_ms = (time.perf_counter() - total_start) * 1000
            return HybridRunResult(
                rows=[],
                total_ms=total_ms,
                graph_ms=graph_result.duration_ms,
                ts_ms=0.0,
                status=graph_result.status,
                error_message=graph_result.error_message,
            )

        # Extract point_ids from graph results
        point_ids = self._extract_point_ids(graph_result.rows, point_id_column)

        if not point_ids:
            # No points found - return empty result
            total_ms = (time.perf_counter() - total_start) * 1000
            return HybridRunResult(
                rows=[],
                total_ms=total_ms,
                graph_ms=graph_result.duration_ms,
                ts_ms=0.0,
                status=RunStatus.SUCCESS,
                point_ids=[],
            )

        # Calculate remaining timeout
        elapsed = time.perf_counter() - total_start
        remaining_timeout = max(1.0, timeout_seconds - elapsed)

        # Phase 2: Timeseries query
        ts_result = self._execute_ts_phase(
            ts_query,
            params,
            point_ids,
            remaining_timeout,
        )

        total_ms = (time.perf_counter() - total_start) * 1000

        return HybridRunResult(
            rows=ts_result.rows,
            total_ms=total_ms,
            graph_ms=graph_result.duration_ms,
            ts_ms=ts_result.duration_ms,
            status=ts_result.status,
            error_message=ts_result.error_message,
            row_count=ts_result.row_count,
            point_ids=point_ids,
        )

    def execute_graph_only(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
    ) -> RunResult:
        """Execute a graph-only query (no timeseries phase).

        Useful for pure graph traversals (Q1-Q5).

        Args:
            query: Cypher or SPARQL query
            params: Query parameters
            timeout_seconds: Timeout

        Returns:
            RunResult from graph execution
        """
        return self.graph.execute(query, params, timeout_seconds)

    def execute_ts_only(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 300.0,
    ) -> RunResult:
        """Execute a timeseries-only query (no graph phase).

        Useful for pure time-series queries (Q6).

        Args:
            query: SQL query
            params: Query parameters
            timeout_seconds: Timeout

        Returns:
            RunResult from timeseries execution
        """
        return self.ts.execute(query, params, timeout_seconds)

    def _execute_graph_phase(
        self,
        query: str,
        params: dict[str, Any],
        timeout_seconds: float,
    ) -> RunResult:
        """Execute graph phase.

        Args:
            query: Graph query (Cypher or SPARQL)
            params: Query parameters
            timeout_seconds: Timeout

        Returns:
            RunResult from graph query
        """
        return self.graph.execute(query, params, timeout_seconds)

    def _execute_ts_phase(
        self,
        query: str,
        params: dict[str, Any],
        point_ids: list[str] | dict[str, list[str]],
        timeout_seconds: float,
    ) -> RunResult:
        """Execute timeseries phase with injected point_ids.

        Args:
            query: SQL query with %(name)s placeholders
            params: Original parameters (DATE_START, DATE_END, CO2_FACTOR, etc.)
            point_ids: Either a single list of IDs or a dict mapping quantity to IDs
                       (e.g., {"energy": [...], "temperature": [...], "occupancy": [...]})
            timeout_seconds: Timeout

        Returns:
            RunResult from timeseries query
        """
        from ..core.query_utils import normalize_param_keys

        # Build params dict for named placeholders %(name)s
        # SQL uses lowercase_snake param names, so normalize keys
        ts_params = normalize_param_keys(params, target_case="lower")

        # Handle different point_ids formats
        if isinstance(point_ids, dict):
            # Q12: multiple point_id lists by quantity
            # Map quantity names to SQL param names
            quantity_to_param = {
                "energy": "energy_point_ids",
                "temperature": "temp_point_ids",
                "occupancy": "occ_point_ids",
                "co2": "co2_point_ids",
            }
            # Initialize all possible point_id lists to empty arrays
            # (in case some quantities don't exist in the dataset)
            for param_name in quantity_to_param.values():
                ts_params[param_name] = []
            # Then populate with actual values
            for quantity, ids in point_ids.items():
                param_name = quantity_to_param.get(quantity, f"{quantity}_point_ids")
                ts_params[param_name] = ids
        else:
            # Q7, Q8, Q9: single point_ids list
            ts_params["point_ids"] = point_ids

        return self.ts.execute(query, ts_params, timeout_seconds)

    def _extract_point_ids(
        self,
        rows: list[dict[str, Any]],
        column: str | None = None,
    ) -> list[str] | dict[str, list[str]]:
        """Extract point IDs from graph query results.

        Handles different result formats:
        - Q7: Single row with point_ids list -> returns list[str]
        - Q12: Multiple rows with (quantity, point_ids) -> returns dict[str, list[str]]
        - Q13: Multiple rows with points list of {point_id, quantity} -> returns dict[str, list[str]]

        Args:
            rows: Query result rows
            column: Specific column name (auto-detect if None)

        Returns:
            List of point ID strings, or dict mapping quantity to point ID lists
        """
        if not rows:
            return []

        sample_row = rows[0]

        # Case 1: Q12 format - rows with (quantity, point_ids)
        if "quantity" in sample_row and "point_ids" in sample_row:
            result = {}
            for row in rows:
                quantity = row.get("quantity")
                ids = row.get("point_ids", [])
                if quantity and ids:
                    # Handle both list and single value
                    if isinstance(ids, list):
                        result[quantity] = [str(id) for id in ids]
                    else:
                        result[quantity] = [str(ids)]
            return result if result else []

        # Case 2: Q13 format - rows with points list of {point_id, quantity}
        if "points" in sample_row:
            result = {}
            for row in rows:
                points = row.get("points", [])
                for point in points:
                    if isinstance(point, dict):
                        pid = point.get("point_id")
                        qty = point.get("quantity")
                        if pid and qty:
                            if qty not in result:
                                result[qty] = []
                            result[qty].append(str(pid))
            return result if result else []

        # Case 3: Q7/Q8/Q9 format - single row with point_ids as list
        if "point_ids" in sample_row:
            ids = sample_row.get("point_ids", [])
            if isinstance(ids, list):
                return [str(id) for id in ids]
            return [str(ids)] if ids else []

        # Fallback: auto-detect column
        if column is None:
            for col in self.POINT_ID_COLUMNS:
                if col in sample_row:
                    column = col
                    break
            if column is None:
                column = list(sample_row.keys())[0]

        # Extract IDs from column
        point_ids = []
        for row in rows:
            value = row.get(column)
            if value is not None:
                if isinstance(value, list):
                    point_ids.extend(str(v) for v in value)
                else:
                    point_ids.append(str(value))

        # Deduplicate while preserving order
        seen = set()
        unique_ids = []
        for pid in point_ids:
            if pid not in seen:
                seen.add(pid)
                unique_ids.append(pid)

        return unique_ids

    def check_connection(self) -> bool:
        """Check both graph and timeseries connections.

        Returns:
            True if both are connected
        """
        return self.graph.check_connection() and self.ts.check_connection()

    def close(self) -> None:
        """Close both connections."""
        self.graph.close()
        self.ts.close()

    def get_query_plan(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> dict | None:
        """Get query plan - routes to appropriate runner.

        Args:
            query: Query string
            params: Query parameters

        Returns:
            Query plan if supported, None otherwise
        """
        # Detect query type using same logic as execute()
        query_lower = query.lower().strip()

        # Cypher query
        if any(keyword in query_lower[:100] for keyword in ['match ', 'create ', 'merge ', 'return ']):
            return self.graph.get_query_plan(query, params)

        # SPARQL query
        if any(keyword in query_lower[:100] for keyword in ['select ', 'construct ', 'describe ', 'ask ', 'prefix ']):
            if 'where' in query_lower and '{' in query:
                return self.graph.get_query_plan(query, params)

        # SQL query
        return self.ts.get_query_plan(query, params)

    def __enter__(self) -> "HybridRunner":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


class M2HybridRunner(HybridRunner):
    """Hybrid runner for M2 (Memgraph + TimescaleDB)."""

    def __init__(
        self,
        memgraph_config: MemgraphConfig,
        postgres_config: PostgresConfig,
    ):
        """Initialize M2 hybrid runner.

        Args:
            memgraph_config: Memgraph connection config
            postgres_config: TimescaleDB connection config
        """
        super().__init__(
            graph_runner=MemgraphRunner(memgraph_config, paradigm="M2"),
            ts_runner=PostgresRunner(postgres_config, paradigm="M2"),
            paradigm="M2",
        )


class O2HybridRunner(HybridRunner):
    """Hybrid runner for O2 (Oxigraph + TimescaleDB)."""

    def __init__(
        self,
        oxigraph_config: OxigraphConfig,
        postgres_config: PostgresConfig,
    ):
        """Initialize O2 hybrid runner.

        Args:
            oxigraph_config: Oxigraph connection config
            postgres_config: TimescaleDB connection config
        """
        super().__init__(
            graph_runner=OxigraphRunner(oxigraph_config, paradigm="O2"),
            ts_runner=PostgresRunner(postgres_config, paradigm="O2"),
            paradigm="O2",
        )
