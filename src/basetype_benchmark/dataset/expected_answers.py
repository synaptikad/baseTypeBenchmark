"""Expected Answer Generator for Benchmark Validation.

Computes ground truth answers for Q1-Q23 directly from the generated
dataset (nodes, edges, timeseries in memory).

This is called during dataset generation to produce expected_answers/
that can be used for validation against any paradigm's results.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Node, Edge, TimeseriesPoint


@dataclass
class ExpectedAnswer:
    """Expected answer for a query."""

    query_id: str
    parameters: dict[str, Any]
    answer_type: str  # set, value, aggregate, ordered_set, path, document
    semantic_content: Any
    row_count: int
    content_hash: str
    full_rows: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        content = self.semantic_content
        if isinstance(content, set):
            content = sorted(list(content), key=str)
        elif isinstance(content, frozenset):
            content = sorted(list(content), key=str)

        return {
            "query_id": self.query_id,
            "parameters": self.parameters,
            "answer_type": self.answer_type,
            "semantic_content": content,
            "row_count": self.row_count,
            "content_hash": self.content_hash,
            "full_rows": self.full_rows,
        }


def _compute_hash(content: Any) -> str:
    """Compute SHA256 hash of content."""
    if isinstance(content, set):
        serializable = sorted(list(content), key=str)
    elif isinstance(content, frozenset):
        serializable = sorted(list(content), key=str)
    elif isinstance(content, dict):
        serializable = {str(k): v for k, v in sorted(content.items())}
    else:
        serializable = content

    json_str = json.dumps(serializable, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


class ExpectedAnswerGenerator:
    """Generate expected answers from in-memory dataset."""

    def __init__(
        self,
        nodes: list["Node"],
        edges: list["Edge"],
        timeseries: list["TimeseriesPoint"],
    ):
        """Initialize with generated data.

        Args:
            nodes: List of Node objects
            edges: List of Edge objects
            timeseries: List of TimeseriesPoint objects
        """
        self.nodes = nodes
        self.edges = edges
        self.timeseries = timeseries

        # Build indexes for fast lookups
        self._build_indexes()

    def _build_indexes(self) -> None:
        """Build lookup indexes."""
        # Node by ID
        self.nodes_by_id: dict[str, "Node"] = {n.id: n for n in self.nodes}

        # Nodes by type
        self.nodes_by_type: dict[str, list["Node"]] = defaultdict(list)
        for n in self.nodes:
            self.nodes_by_type[n.type].append(n)

        # Edges by source
        self.edges_by_source: dict[str, list["Edge"]] = defaultdict(list)
        for e in self.edges:
            self.edges_by_source[e.source_id].append(e)

        # Edges by target
        self.edges_by_target: dict[str, list["Edge"]] = defaultdict(list)
        for e in self.edges:
            self.edges_by_target[e.target_id].append(e)

        # Edges by type
        self.edges_by_type: dict[str, list["Edge"]] = defaultdict(list)
        for e in self.edges:
            self.edges_by_type[e.rel_type].append(e)

        # Timeseries by point
        self.ts_by_point: dict[str, list["TimeseriesPoint"]] = defaultdict(list)
        for t in self.timeseries:
            self.ts_by_point[t.point_id].append(t)

    def generate_all(self, params: dict[str, Any]) -> dict[str, ExpectedAnswer]:
        """Generate expected answers for all read-only queries.

        Args:
            params: Query parameters from queries_params.yaml

        Returns:
            Dict mapping query_id to ExpectedAnswer
        """
        answers: dict[str, ExpectedAnswer] = {}

        # Generate each query that doesn't involve writes
        query_methods = [
            ("Q1", self._gen_q1),
            ("Q2", self._gen_q2),
            ("Q3", self._gen_q3),
            ("Q4", self._gen_q4),
            ("Q5", self._gen_q5),
            ("Q6", self._gen_q6),
            ("Q7", self._gen_q7),
            ("Q8", self._gen_q8),
            ("Q9", self._gen_q9),
            ("Q10", self._gen_q10),
            ("Q11", self._gen_q11),
            ("Q12", self._gen_q12),
            ("Q13", self._gen_q13),
            ("Q14", self._gen_q14),
            ("Q15", self._gen_q15),
            ("Q16", self._gen_q16),
            ("Q17", self._gen_q17),
            ("Q18", self._gen_q18),
            ("Q19", self._gen_q19),
            ("Q20", self._gen_q20),
            ("Q21", self._gen_q21),
            ("Q22", self._gen_q22),
            ("Q23", self._gen_q23),
            # Graph-native queries (Q27-Q30)
            ("Q27", self._gen_q27),
            ("Q28", self._gen_q28),
            ("Q29", self._gen_q29),
            ("Q30", self._gen_q30),
            # SQL-native queries (Q31-Q34)
            ("Q31", self._gen_q31),
            ("Q32", self._gen_q32),
            ("Q33", self._gen_q33),
            ("Q34", self._gen_q34),
            # JSONB validation queries (Q24-Q26) - validate QW writes
            ("Q24", self._gen_q24),
            ("Q25", self._gen_q25),
            ("Q26", self._gen_q26),
            # Write validation queries (Q35-Q38) - validate QW1, QW2, QW3, QW8
            ("Q35", self._gen_q35),
            ("Q36", self._gen_q36),
            ("Q37", self._gen_q37),
            ("Q38", self._gen_q38),
            # Tenant validation queries (Q39-Q41) - validate QW9-QW12
            ("Q39", self._gen_q39),
            ("Q40", self._gen_q40),
            ("Q41", self._gen_q41),
        ]

        for query_id, method in query_methods:
            try:
                answer = method(params)
                if answer:
                    answers[query_id] = answer
            except Exception as e:
                print(f"Warning: Failed to generate {query_id}: {e}")

        return answers

    def _traverse_downstream(
        self,
        start_id: str,
        rel_type: str,
        max_depth: int = 10,
    ) -> set[str]:
        """Traverse graph downstream from start node.

        Args:
            start_id: Starting node ID
            rel_type: Relationship type to follow
            max_depth: Maximum traversal depth

        Returns:
            Set of reachable node IDs (excluding start)
        """
        visited = set()
        current = {start_id}

        for _ in range(max_depth):
            next_level = set()
            for node_id in current:
                for edge in self.edges_by_source.get(node_id, []):
                    if edge.rel_type == rel_type and edge.target_id not in visited:
                        next_level.add(edge.target_id)

            if not next_level:
                break

            visited.update(next_level)
            current = next_level

        return visited

    def _traverse_upstream(
        self,
        start_id: str,
        rel_types: list[str] | None = None,
        max_depth: int = 10,
    ) -> set[str]:
        """Traverse graph upstream from start node.

        Args:
            start_id: Starting node ID
            rel_types: Relationship types to follow (None = all)
            max_depth: Maximum traversal depth

        Returns:
            Set of reachable node IDs (excluding start)
        """
        visited = set()
        current = {start_id}

        for _ in range(max_depth):
            next_level = set()
            for node_id in current:
                for edge in self.edges_by_target.get(node_id, []):
                    if rel_types is None or edge.rel_type in rel_types:
                        if edge.source_id not in visited:
                            next_level.add(edge.source_id)

            if not next_level:
                break

            visited.update(next_level)
            current = next_level

        return visited

    # =========================================================================
    # GRAPH-ONLY (Q1-Q5)
    # =========================================================================

    def _gen_q1(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q1: Energy chain - equipment downstream from meter."""
        meter_id = params.get("meter_id")
        if not meter_id:
            return None

        # Traverse FEEDS relationships
        downstream_ids = self._traverse_downstream(meter_id, "FEEDS")

        # Build full rows with details
        full_rows = []
        for node_id in downstream_ids:
            node = self.nodes_by_id.get(node_id)
            if node:
                full_rows.append({
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                })

        return ExpectedAnswer(
            query_id="Q1",
            parameters={"meter_id": meter_id},
            answer_type="set",
            semantic_content=downstream_ids,
            row_count=len(downstream_ids),
            content_hash=_compute_hash(downstream_ids),
            full_rows=full_rows,
        )

    def _gen_q2(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q2: Impact analysis - equipment upstream affected by failure."""
        equipment_id = params.get("equipment_id")
        if not equipment_id:
            return None

        # Traverse upstream (reverse of any relationship)
        upstream_ids = self._traverse_upstream(equipment_id)

        full_rows = []
        for node_id in upstream_ids:
            node = self.nodes_by_id.get(node_id)
            if node:
                full_rows.append({
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                })

        return ExpectedAnswer(
            query_id="Q2",
            parameters={"equipment_id": equipment_id},
            answer_type="set",
            semantic_content=upstream_ids,
            row_count=len(upstream_ids),
            content_hash=_compute_hash(upstream_ids),
            full_rows=full_rows,
        )

    def _gen_q3(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q3: Equipment serving a space."""
        space_id = params.get("space_id")
        if not space_id:
            return None

        # Find equipment with SERVES relationship to space
        equipment_ids = set()
        full_rows = []

        for edge in self.edges_by_target.get(space_id, []):
            if edge.rel_type == "SERVES":
                eq_id = edge.source_id
                equipment_ids.add(eq_id)
                node = self.nodes_by_id.get(eq_id)
                if node:
                    full_rows.append({
                        "equipment_id": eq_id,
                        "equipment_name": node.name,
                        "equipment_type": node.type,
                    })

        return ExpectedAnswer(
            query_id="Q3",
            parameters={"space_id": space_id},
            answer_type="set",
            semantic_content=equipment_ids,
            row_count=len(equipment_ids),
            content_hash=_compute_hash(equipment_ids),
            full_rows=full_rows,
        )

    def _gen_q4(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q4: Temperature sensors and equipment on floor."""
        floor_id = params.get("floor_id")
        if not floor_id:
            return None

        # Find points with "temp" in name that are on equipment located on this floor
        results = set()
        full_rows = []

        # Get spaces on floor
        spaces_on_floor = set()
        for edge in self.edges_by_source.get(floor_id, []):
            if edge.rel_type == "CONTAINS":
                spaces_on_floor.add(edge.target_id)

        # Get equipment in those spaces
        equipment_in_spaces = set()
        for space_id in spaces_on_floor:
            for edge in self.edges_by_target.get(space_id, []):
                if edge.rel_type == "LOCATED_IN":
                    equipment_in_spaces.add(edge.source_id)

        # Get temp points on that equipment
        for eq_id in equipment_in_spaces:
            for edge in self.edges_by_source.get(eq_id, []):
                if edge.rel_type == "HAS_POINT":
                    point_id = edge.target_id
                    point = self.nodes_by_id.get(point_id)
                    if point and point.properties.get("quantity") == "temperature":
                        results.add((point_id, eq_id))
                        eq = self.nodes_by_id.get(eq_id)
                        full_rows.append({
                            "point_id": point_id,
                            "point_name": point.name,
                            "equipment_id": eq_id,
                            "equipment_name": eq.name if eq else "",
                        })

        return ExpectedAnswer(
            query_id="Q4",
            parameters={"floor_id": floor_id},
            answer_type="set",
            semantic_content=results,
            row_count=len(results),
            content_hash=_compute_hash(results),
            full_rows=full_rows,
        )

    def _gen_q5(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q5: Orphan equipment (no relationships)."""
        # Find nodes with no edges (as source or target)
        nodes_with_edges = set()
        for e in self.edges:
            nodes_with_edges.add(e.source_id)
            nodes_with_edges.add(e.target_id)

        orphan_ids = set()
        full_rows = []

        for node in self.nodes:
            if node.type not in ("Building", "Floor", "Space", "Tenant", "Site"):
                if node.id not in nodes_with_edges:
                    orphan_ids.add(node.id)
                    full_rows.append({
                        "id": node.id,
                        "type": node.type,
                        "name": node.name,
                    })

        return ExpectedAnswer(
            query_id="Q5",
            parameters={},
            answer_type="set",
            semantic_content=orphan_ids,
            row_count=len(orphan_ids),
            content_hash=_compute_hash(orphan_ids),
            full_rows=full_rows,
        )

    # =========================================================================
    # TIMESERIES (Q6)
    # =========================================================================

    def _gen_q6(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q6: Hourly curve for sensor."""
        point_id = params.get("point_id")
        if not point_id:
            return None

        # Get timeseries for point
        ts_points = self.ts_by_point.get(point_id, [])
        if not ts_points:
            return ExpectedAnswer(
                query_id="Q6",
                parameters={"point_id": point_id},
                answer_type="aggregate",
                semantic_content={},
                row_count=0,
                content_hash=_compute_hash({}),
                full_rows=[],
            )

        # Aggregate by hour
        hourly_data: dict[str, list[float]] = defaultdict(list)
        for ts in ts_points:
            hour_key = ts.timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
            hourly_data[hour_key].append(ts.value)

        # Compute aggregates
        semantic = {}
        full_rows = []

        for hour_key, values in sorted(hourly_data.items()):
            avg_val = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)

            semantic[hour_key] = {
                "avg_value": round(avg_val, 4),
                "min_value": round(min_val, 4),
                "max_value": round(max_val, 4),
                "sample_count": len(values),
            }

            full_rows.append({
                "time_bucket": hour_key,
                "avg_value": round(avg_val, 4),
                "min_value": round(min_val, 4),
                "max_value": round(max_val, 4),
                "sample_count": len(values),
            })

        return ExpectedAnswer(
            query_id="Q6",
            parameters={"point_id": point_id},
            answer_type="aggregate",
            semantic_content=semantic,
            row_count=len(semantic),
            content_hash=_compute_hash(semantic),
            full_rows=full_rows,
        )

    # =========================================================================
    # HYBRID (Q7-Q13)
    # =========================================================================

    def _gen_q7(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q7: Top 20 sensors with highest variance in building."""
        building_id = params.get("building_id")
        if not building_id:
            return None

        # Get all points in building via hierarchy
        points_in_building = set()

        # Building -> Floors
        for e1 in self.edges_by_source.get(building_id, []):
            if e1.rel_type == "CONTAINS":
                floor_id = e1.target_id
                # Floor -> Spaces
                for e2 in self.edges_by_source.get(floor_id, []):
                    if e2.rel_type == "CONTAINS":
                        space_id = e2.target_id
                        # Space <- Equipment (LOCATED_IN)
                        for e3 in self.edges_by_target.get(space_id, []):
                            if e3.rel_type == "LOCATED_IN":
                                eq_id = e3.source_id
                                # Equipment -> Points
                                for e4 in self.edges_by_source.get(eq_id, []):
                                    if e4.rel_type == "HAS_POINT":
                                        points_in_building.add(e4.target_id)

        # Compute variance for each point
        variances = []
        for point_id in points_in_building:
            ts_points = self.ts_by_point.get(point_id, [])
            if len(ts_points) > 1:
                values = [t.value for t in ts_points]
                avg = sum(values) / len(values)
                variance = sum((v - avg) ** 2 for v in values) / len(values)
                variances.append((point_id, variance, avg, len(values)))

        # Sort by variance descending, take top 20
        variances.sort(key=lambda x: x[1], reverse=True)
        top_20 = variances[:20]

        semantic = [p[0] for p in top_20]
        full_rows = [
            {
                "point_id": p[0],
                "variance": round(p[1], 4),
                "avg_value": round(p[2], 4),
                "sample_count": p[3],
            }
            for p in top_20
        ]

        return ExpectedAnswer(
            query_id="Q7",
            parameters={"building_id": building_id},
            answer_type="ordered_set",
            semantic_content=semantic,
            row_count=len(semantic),
            content_hash=_compute_hash(semantic),
            full_rows=full_rows,
        )

    def _gen_q8(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q8: Total energy consumption for tenant."""
        tenant_id = params.get("tenant_id")
        if not tenant_id:
            return None

        # Get meters for tenant via METERS_TENANT
        # Note: METERS_TENANT goes SubMeter -> Tenant, so we look at edges_by_target
        total_energy = 0.0
        meter_count = 0
        point_count = 0

        for edge in self.edges_by_target.get(tenant_id, []):
            if edge.rel_type == "METERS_TENANT":
                meter_id = edge.source_id  # Meter is the source!
                meter_count += 1

                # Get points on meter
                for e2 in self.edges_by_source.get(meter_id, []):
                    if e2.rel_type == "HAS_POINT":
                        point_id = e2.target_id
                        point_count += 1

                        # Sum timeseries values (filter for energy points)
                        point = self.nodes_by_id.get(point_id)
                        if point and point.properties.get("quantity") == "energy":
                            for ts in self.ts_by_point.get(point_id, []):
                                total_energy += ts.value

        semantic = {
            "total_energy_kwh": round(total_energy, 2),
            "meter_count": meter_count,
            "point_count": point_count,
        }

        return ExpectedAnswer(
            query_id="Q8",
            parameters={"tenant_id": tenant_id},
            answer_type="value",
            semantic_content=semantic,
            row_count=1,
            content_hash=_compute_hash(semantic),
            full_rows=[semantic],
        )

    def _gen_q9(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q9: Carbon footprint for tenant."""
        tenant_id = params.get("tenant_id")
        carbon_factor = params.get("co2_factor", 0.0569)

        if not tenant_id:
            return None

        # Reuse Q8 for energy
        q8 = self._gen_q8(params)
        if not q8:
            return None

        total_energy = q8.semantic_content["total_energy_kwh"]
        carbon_kg = total_energy * carbon_factor

        semantic = {
            "carbon_kg_co2": round(carbon_kg, 2),
            "total_energy_kwh": round(total_energy, 2),
        }

        return ExpectedAnswer(
            query_id="Q9",
            parameters={"tenant_id": tenant_id, "carbon_factor": carbon_factor},
            answer_type="value",
            semantic_content=semantic,
            row_count=1,
            content_hash=_compute_hash(semantic),
            full_rows=[semantic],
        )

    def _gen_q10(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q10: Security equipment count per space in building."""
        building_id = params.get("building_id")
        if not building_id:
            return None

        # Equipment types that are security-related
        # Note: We check both node.type AND properties.equipment_type
        security_types = {"Camera", "AccessControl", "Alarm", "Sensor", "IPCamera", "BadgeReader"}
        security_equipment_types = {"IPCamera", "BadgeReader", "Camera", "AccessControl", "Alarm", "SecuritySensor"}

        # Get spaces in building
        space_equipment: dict[tuple, int] = defaultdict(int)
        full_rows = []

        for e1 in self.edges_by_source.get(building_id, []):
            if e1.rel_type == "CONTAINS":
                floor_id = e1.target_id
                for e2 in self.edges_by_source.get(floor_id, []):
                    if e2.rel_type == "CONTAINS":
                        space_id = e2.target_id
                        space = self.nodes_by_id.get(space_id)

                        for e3 in self.edges_by_target.get(space_id, []):
                            if e3.rel_type == "LOCATED_IN":
                                eq = self.nodes_by_id.get(e3.source_id)
                                if eq:
                                    # Check both node.type and properties.equipment_type
                                    eq_type = (eq.properties or {}).get("equipment_type", eq.type)
                                    if eq.type in security_types or eq_type in security_equipment_types:
                                        space_equipment[(space_id, eq_type)] += 1

        # Build results - convert tuple keys to string for JSON serialization
        semantic = {f"{space_id}:{eq_type}": count for (space_id, eq_type), count in space_equipment.items()}
        for (space_id, eq_type), count in space_equipment.items():
            space = self.nodes_by_id.get(space_id)
            full_rows.append({
                "space_id": space_id,
                "space_name": space.name if space else "",
                "equipment_type": eq_type,
                "equipment_count": count,
            })

        return ExpectedAnswer(
            query_id="Q10",
            parameters={"building_id": building_id},
            answer_type="aggregate",
            semantic_content=semantic,
            row_count=len(full_rows),
            content_hash=_compute_hash(semantic),
            full_rows=full_rows,
        )

    def _gen_q11(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q11: IT equipment downstream from UPS."""
        ups_id = params.get("ups_id")
        if not ups_id:
            return None

        # IT equipment types (check both node.type and properties.equipment_type)
        it_types = {"Server", "Switch", "Router", "Storage", "NetworkSwitch", "RackServer"}

        # Traverse downstream
        downstream = self._traverse_downstream(ups_id, "FEEDS")

        # Filter to IT equipment
        it_equipment = set()
        full_rows = []

        for node_id in downstream:
            node = self.nodes_by_id.get(node_id)
            if node:
                eq_type = (node.properties or {}).get("equipment_type", node.type)
                if node.type in it_types or eq_type in it_types:
                    it_equipment.add(node_id)
                    full_rows.append({
                        "equipment_id": node_id,
                        "equipment_type": eq_type,
                        "equipment_name": node.name,
                    })

        return ExpectedAnswer(
            query_id="Q11",
            parameters={"ups_id": ups_id},
            answer_type="set",
            semantic_content=it_equipment,
            row_count=len(it_equipment),
            content_hash=_compute_hash(it_equipment),
            full_rows=full_rows,
        )

    def _gen_q12(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q12: Building global metrics."""
        building_id = params.get("building_id")
        if not building_id:
            return None

        total_energy = 0.0
        temp_values = []
        occupancy_total = 0.0

        # Get all points in building via graph traversal:
        # Building -> Floor (CONTAINS) -> Space (CONTAINS) -> Equipment (LOCATED_IN or SERVES) -> Point (HAS_POINT)
        points_in_building = set()
        for e1 in self.edges_by_source.get(building_id, []):
            if e1.rel_type == "CONTAINS":
                floor_id = e1.target_id
                for e2 in self.edges_by_source.get(floor_id, []):
                    if e2.rel_type == "CONTAINS":
                        space_id = e2.target_id
                        for e3 in self.edges_by_target.get(space_id, []):
                            if e3.rel_type in ("LOCATED_IN", "SERVES"):
                                eq_id = e3.source_id
                                for e4 in self.edges_by_source.get(eq_id, []):
                                    if e4.rel_type == "HAS_POINT":
                                        points_in_building.add(e4.target_id)

        # Aggregate timeseries data for points in building
        for point_id in points_in_building:
            point = self.nodes_by_id.get(point_id)
            if not point:
                continue

            name_lower = point.name.lower()
            ts_values = [t.value for t in self.ts_by_point.get(point_id, [])]

            if not ts_values:
                continue

            if "energy" in name_lower or "power" in name_lower:
                total_energy += sum(ts_values)
            elif "temp" in name_lower:
                temp_values.extend(ts_values)
            elif "occupancy" in name_lower:
                occupancy_total += sum(ts_values)

        avg_temp = sum(temp_values) / len(temp_values) if temp_values else 0.0

        semantic = {
            "total_energy_kwh": round(total_energy, 2),
            "avg_temperature_c": round(avg_temp, 2),
            "total_occupancy": int(occupancy_total),
        }

        return ExpectedAnswer(
            query_id="Q12",
            parameters={"building_id": building_id},
            answer_type="value",
            semantic_content=semantic,
            row_count=1,
            content_hash=_compute_hash(semantic),
            full_rows=[semantic],
        )

    def _gen_q13(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q13: Air quality in offices during business hours."""
        building_id = params.get("building_id")
        if not building_id:
            return None

        # Get office spaces and their points
        space_data: dict[str, dict] = defaultdict(lambda: {"temp": [], "co2": []})

        for e1 in self.edges_by_source.get(building_id, []):
            if e1.rel_type == "CONTAINS":
                floor_id = e1.target_id
                for e2 in self.edges_by_source.get(floor_id, []):
                    if e2.rel_type == "CONTAINS":
                        space_id = e2.target_id
                        space = self.nodes_by_id.get(space_id)

                        if not space:
                            continue
                        space_type = (space.properties or {}).get("space_type", "")
                        if not space_type.startswith("office"):
                            continue

                        # Get equipment serving this space
                        for e3 in self.edges_by_target.get(space_id, []):
                            if e3.rel_type in ("SERVES", "LOCATED_IN"):
                                eq_id = e3.source_id
                                for e4 in self.edges_by_source.get(eq_id, []):
                                    if e4.rel_type == "HAS_POINT":
                                        point_id = e4.target_id
                                        point = self.nodes_by_id.get(point_id)
                                        if not point:
                                            continue

                                        # Filter business hours (8-18) and weekdays (Mon-Fri)
                                        quantity = (point.properties or {}).get("quantity", "")
                                        for ts in self.ts_by_point.get(point_id, []):
                                            # Business hours: 8-18, weekdays: 0=Mon to 4=Fri
                                            if 8 <= ts.timestamp.hour <= 18 and ts.timestamp.weekday() < 5:
                                                if quantity == "temperature":
                                                    space_data[space_id]["temp"].append(ts.value)
                                                elif quantity == "co2":
                                                    space_data[space_id]["co2"].append(ts.value)

        semantic = {}
        full_rows = []

        for space_id, data in space_data.items():
            space = self.nodes_by_id.get(space_id)
            avg_temp = sum(data["temp"]) / len(data["temp"]) if data["temp"] else None
            avg_co2 = sum(data["co2"]) / len(data["co2"]) if data["co2"] else None

            semantic[space_id] = {
                "avg_temp_c": round(avg_temp, 2) if avg_temp else None,
                "avg_co2_ppm": round(avg_co2, 2) if avg_co2 else None,
            }

            full_rows.append({
                "space_id": space_id,
                "space_name": space.name if space else "",
                "avg_temp_c": round(avg_temp, 2) if avg_temp else None,
                "avg_co2_ppm": round(avg_co2, 2) if avg_co2 else None,
            })

        return ExpectedAnswer(
            query_id="Q13",
            parameters={"building_id": building_id},
            answer_type="aggregate",
            semantic_content=semantic,
            row_count=len(semantic),
            content_hash=_compute_hash(semantic),
            full_rows=full_rows,
        )

    # =========================================================================
    # JSONB-SPECIFIC (Q14-Q19)
    # =========================================================================

    def _gen_q14(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q14: Points communicating with BACnet device."""
        device_id = params.get("device_id")
        if not device_id:
            return None

        # Find points with matching protocol.device_id
        matching_points = set()
        full_rows = []

        for node in self.nodes:
            if node.type == "Point":
                protocol = node.protocol or {}
                if protocol.get("device_id") == device_id:
                    matching_points.add(node.id)

                    # Find parent equipment
                    eq_id = None
                    for edge in self.edges_by_target.get(node.id, []):
                        if edge.rel_type == "HAS_POINT":
                            eq_id = edge.source_id
                            break

                    full_rows.append({
                        "point_id": node.id,
                        "point_name": node.name,
                        "equipment_id": eq_id,
                        "object_type": protocol.get("object_type"),
                        "object_instance": protocol.get("object_instance"),
                    })

        return ExpectedAnswer(
            query_id="Q14",
            parameters={"device_id": device_id},
            answer_type="set",
            semantic_content=matching_points,
            row_count=len(matching_points),
            content_hash=_compute_hash(matching_points),
            full_rows=full_rows,
        )

    def _gen_q15(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q15: Equipment with warranty expiring soon."""
        days_ahead = params.get("days_ahead", 90)
        reference_date = params.get("reference_date")

        if reference_date:
            if isinstance(reference_date, str):
                ref_date = datetime.fromisoformat(reference_date.replace("Z", "+00:00"))
            else:
                ref_date = reference_date
        else:
            ref_date = datetime.now()

        cutoff_date = ref_date + timedelta(days=days_ahead)

        expiring_equipment = set()
        full_rows = []

        for node in self.nodes:
            if node.type not in ("Building", "Floor", "Space", "Point", "Site"):
                metadata = node.metadata or {}
                warranty_end = metadata.get("warranty_end")

                if warranty_end:
                    if isinstance(warranty_end, str):
                        try:
                            warranty_date = datetime.fromisoformat(warranty_end.replace("Z", "+00:00"))
                        except:
                            continue
                    else:
                        warranty_date = warranty_end

                    if ref_date <= warranty_date <= cutoff_date:
                        days_remaining = (warranty_date - ref_date).days
                        expiring_equipment.add(node.id)
                        full_rows.append({
                            "equipment_id": node.id,
                            "name": node.name,
                            "equipment_type": node.type,
                            "warranty_end": str(warranty_date),
                            "days_remaining": days_remaining,
                        })

        return ExpectedAnswer(
            query_id="Q15",
            parameters={"days_ahead": days_ahead},
            answer_type="set",
            semantic_content=expiring_equipment,
            row_count=len(expiring_equipment),
            content_hash=_compute_hash(expiring_equipment),
            full_rows=full_rows,
        )

    def _gen_q16(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q16: Equipment with specific semantic tags."""
        tag_pattern = params.get("tag_pattern", "^brick:")

        import re
        pattern = re.compile(tag_pattern)

        matching_equipment = set()
        full_rows = []

        for node in self.nodes:
            if node.type not in ("Building", "Floor", "Space", "Point", "Site"):
                matching_tags = [t for t in (node.tags or []) if pattern.match(t)]
                if matching_tags:
                    matching_equipment.add(node.id)
                    full_rows.append({
                        "equipment_id": node.id,
                        "name": node.name,
                        "matching_tags": matching_tags,
                    })

        return ExpectedAnswer(
            query_id="Q16",
            parameters={"tag_pattern": tag_pattern},
            answer_type="set",
            semantic_content=matching_equipment,
            row_count=len(matching_equipment),
            content_hash=_compute_hash(matching_equipment),
            full_rows=full_rows,
        )

    def _gen_q17(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q17: HVAC equipment with specific capability."""
        capability = params.get("capability", "humidity_control")

        hvac_types = {"AHU", "VAV", "FCU", "Chiller", "Boiler", "HeatPump", "CoolingTower"}

        matching_equipment = set()
        full_rows = []

        for node in self.nodes:
            # Check properties.equipment_type since node.type is always "Equipment"
            eq_type = (node.properties or {}).get("equipment_type", "")
            if eq_type in hvac_types:
                if capability in (node.capabilities or []):
                    matching_equipment.add(node.id)
                    full_rows.append({
                        "equipment_id": node.id,
                        "name": node.name,
                        "equipment_type": eq_type,
                        "all_capabilities": node.capabilities,
                    })

        return ExpectedAnswer(
            query_id="Q17",
            parameters={"capability": capability},
            answer_type="set",
            semantic_content=matching_equipment,
            row_count=len(matching_equipment),
            content_hash=_compute_hash(matching_equipment),
            full_rows=full_rows,
        )

    def _gen_q18(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q18: Sensors with overdue calibration in energy chain."""
        meter_id = params.get("meter_id")
        reference_date = params.get("reference_date")

        if not meter_id:
            return None

        if reference_date:
            if isinstance(reference_date, str):
                ref_date = datetime.fromisoformat(reference_date.replace("Z", "+00:00"))
            else:
                ref_date = reference_date
        else:
            ref_date = datetime.now()

        # Get equipment in energy chain
        chain_equipment = self._traverse_downstream(meter_id, "FEEDS")
        chain_equipment.add(meter_id)

        # Find points with overdue calibration
        overdue_points = set()
        full_rows = []

        for eq_id in chain_equipment:
            for edge in self.edges_by_source.get(eq_id, []):
                if edge.rel_type == "HAS_POINT":
                    point_id = edge.target_id
                    point = self.nodes_by_id.get(point_id)

                    if point and point.calibration:
                        # Generator uses "next_date", not "next_calibration"
                        next_cal = point.calibration.get("next_date") or point.calibration.get("next_calibration")
                        if next_cal:
                            if isinstance(next_cal, str):
                                try:
                                    next_date = datetime.fromisoformat(next_cal.replace("Z", "+00:00"))
                                except:
                                    continue
                            else:
                                next_date = next_cal

                            if next_date < ref_date:
                                overdue_points.add(point_id)
                                full_rows.append({
                                    "point_id": point_id,
                                    "point_name": point.name,
                                    "equipment_id": eq_id,
                                    "last_calibration": point.calibration.get("last_date") or point.calibration.get("last_calibration"),
                                    "next_calibration": str(next_date),
                                })

        return ExpectedAnswer(
            query_id="Q18",
            parameters={"meter_id": meter_id},
            answer_type="set",
            semantic_content=overdue_points,
            row_count=len(overdue_points),
            content_hash=_compute_hash(overdue_points),
            full_rows=full_rows,
        )

    def _gen_q19(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q19: Digital twin document for equipment."""
        equipment_id = params.get("equipment_id")
        if not equipment_id:
            return None

        equipment = self.nodes_by_id.get(equipment_id)
        if not equipment:
            return None

        # Build document
        doc = {
            "id": equipment.id,
            "name": equipment.name,
            "type": equipment.type,
            "capabilities": equipment.capabilities,
            "tags": equipment.tags,
            "metadata": equipment.metadata,
            "protocol": equipment.protocol,
        }

        # Add points
        points = []
        for edge in self.edges_by_source.get(equipment_id, []):
            if edge.rel_type == "HAS_POINT":
                point = self.nodes_by_id.get(edge.target_id)
                if point:
                    points.append({
                        "id": point.id,
                        "name": point.name,
                        "quantity": point.properties.get("quantity"),
                        "unit": point.properties.get("unit"),
                    })

        doc["points"] = points

        return ExpectedAnswer(
            query_id="Q19",
            parameters={"equipment_id": equipment_id},
            answer_type="document",
            semantic_content=doc,
            row_count=1,
            content_hash=_compute_hash(doc),
            full_rows=[doc],
        )

    # =========================================================================
    # GRAPH-NATIVE (Q20-Q23)
    # =========================================================================

    def _gen_q20(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q20: Shortest path between equipment and space."""
        source_id = params.get("hvac_source_equipment_id") or params.get("equipment_id")
        target_id = params.get("hvac_target_space_id") or params.get("space_id")

        if not source_id or not target_id:
            return None

        # BFS to find shortest path
        from collections import deque

        visited = {source_id}
        queue = deque([(source_id, [source_id])])

        while queue:
            node_id, path = queue.popleft()

            if node_id == target_id:
                # Found path
                full_rows = []
                for i, nid in enumerate(path):
                    node = self.nodes_by_id.get(nid)
                    full_rows.append({
                        "path_index": 0,
                        "id": nid,
                        "node_type": node.type if node else "",
                        "node_name": node.name if node else "",
                    })

                return ExpectedAnswer(
                    query_id="Q20",
                    parameters={"source_id": source_id, "target_id": target_id},
                    answer_type="path",
                    semantic_content=[path],
                    row_count=len(path),
                    content_hash=_compute_hash([path]),
                    full_rows=full_rows,
                )

            # Explore neighbors (both directions)
            for edge in self.edges_by_source.get(node_id, []):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, path + [edge.target_id]))

            for edge in self.edges_by_target.get(node_id, []):
                if edge.source_id not in visited:
                    visited.add(edge.source_id)
                    queue.append((edge.source_id, path + [edge.source_id]))

        # No path found
        return ExpectedAnswer(
            query_id="Q20",
            parameters={"source_id": source_id, "target_id": target_id},
            answer_type="path",
            semantic_content=[],
            row_count=0,
            content_hash=_compute_hash([]),
            full_rows=[],
        )

    def _gen_q21(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q21: All electrical paths + single points of failure."""
        meter_id = params.get("meter_id")
        if not meter_id:
            return None

        # Find all paths through FEEDS
        # This is complex - simplified version
        all_paths = []
        spof_nodes = set()

        # DFS to find all paths
        def dfs(node_id: str, path: list[str], visited: set[str]):
            path = path + [node_id]

            # Get next nodes
            next_nodes = []
            for edge in self.edges_by_source.get(node_id, []):
                if edge.rel_type == "FEEDS" and edge.target_id not in visited:
                    next_nodes.append(edge.target_id)

            if not next_nodes:
                # End of path
                all_paths.append(path)
            else:
                for next_id in next_nodes:
                    dfs(next_id, path, visited | {next_id})

        dfs(meter_id, [], {meter_id})

        # Find SPOFs (nodes that appear in all paths)
        if all_paths:
            common_nodes = set(all_paths[0])
            for path in all_paths[1:]:
                common_nodes &= set(path)
            spof_nodes = common_nodes - {meter_id}  # Exclude source

        semantic = {
            "paths": all_paths,
            "spof_nodes": list(spof_nodes),
        }

        full_rows = []
        for i, path in enumerate(all_paths[:10]):  # Limit to 10 paths
            for node_id in path:
                node = self.nodes_by_id.get(node_id)
                full_rows.append({
                    "path_index": i,
                    "id": node_id,
                    "node_type": node.type if node else "",
                    "is_spof": node_id in spof_nodes,
                })

        return ExpectedAnswer(
            query_id="Q21",
            parameters={"meter_id": meter_id},
            answer_type="paths_with_spof",
            semantic_content=semantic,
            row_count=len(all_paths),
            content_hash=_compute_hash(semantic),
            full_rows=full_rows,
        )

    def _gen_q22(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q22: Equipment siblings (share same FEEDS parent).

        Per catalog: Find equipment fed by the same parent via FEEDS relationship.
        Pattern: (parent)-[:FEEDS]->(equipment) and (parent)-[:FEEDS]->(sibling)
        """
        equipment_id = params.get("equipment_id")
        if not equipment_id:
            return None

        # Find parent equipment that FEEDS this equipment
        # Only consider FEEDS relationship as per catalog intention
        parents = set()
        for edge in self.edges_by_target.get(equipment_id, []):
            if edge.rel_type == "FEEDS":
                parent_node = self.nodes_by_id.get(edge.source_id)
                # Only consider Equipment as parents (not spaces/buildings)
                if parent_node and parent_node.type == "Equipment":
                    parents.add(edge.source_id)

        # Find siblings (other equipment fed by same parent via FEEDS)
        siblings = set()
        full_rows = []

        for parent_id in parents:
            # Find all equipment fed by this parent
            for edge in self.edges_by_source.get(parent_id, []):
                if edge.rel_type == "FEEDS" and edge.target_id != equipment_id:
                    sibling_id = edge.target_id
                    sibling = self.nodes_by_id.get(sibling_id)
                    # Only include Equipment siblings
                    if sibling and sibling.type == "Equipment":
                        siblings.add(sibling_id)
                        parent = self.nodes_by_id.get(parent_id)
                        full_rows.append({
                            "sibling_id": sibling_id,
                            "sibling_name": sibling.name if sibling else "",
                            "sibling_type": sibling.properties.get("equipment_type", "Equipment") if sibling else "",
                            "parent_id": parent_id,
                            "parent_name": parent.name if parent else "",
                        })

        return ExpectedAnswer(
            query_id="Q22",
            parameters={"equipment_id": equipment_id},
            answer_type="set",
            semantic_content=siblings,
            row_count=len(siblings),
            content_hash=_compute_hash(siblings),
            full_rows=full_rows,
        )

    def _gen_q23(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q23: Failure Impact Analysis - nodes impacted within N hops via failure propagation.

        Semantic: If this equipment fails, which spaces/equipment are impacted within N hops?
        Uses meaningful relationship types for failure propagation:
        - FEEDS (power/fluid flow)
        - SERVES (service dependency)
        - POWERS (electrical dependency)
        """
        equipment_id = params.get("equipment_id")
        max_hops = params.get("max_hops", 3)

        if not equipment_id:
            return None

        # Relationship types for failure propagation
        failure_rel_types = {"FEEDS", "SERVES", "POWERS"}

        # BFS with hop tracking - only follow failure propagation relationships
        visited = {equipment_id: 0}
        current = {equipment_id}

        for hop in range(1, max_hops + 1):
            next_level = set()
            for node_id in current:
                # Outgoing edges (only failure propagation rel_types)
                for edge in self.edges_by_source.get(node_id, []):
                    if edge.rel_type in failure_rel_types and edge.target_id not in visited:
                        visited[edge.target_id] = hop
                        next_level.add(edge.target_id)

                # Incoming edges (only failure propagation rel_types)
                for edge in self.edges_by_target.get(node_id, []):
                    if edge.rel_type in failure_rel_types and edge.source_id not in visited:
                        visited[edge.source_id] = hop
                        next_level.add(edge.source_id)

            current = next_level

        # Exclude source
        del visited[equipment_id]

        reachable = set(visited.keys())
        full_rows = []

        for node_id, hop_distance in sorted(visited.items(), key=lambda x: (x[1], x[0])):
            node = self.nodes_by_id.get(node_id)
            full_rows.append({
                "node_id": node_id,
                "node_type": node.type if node else "",
                "node_name": node.name if node else "",
                "hop_distance": hop_distance,
            })

        return ExpectedAnswer(
            query_id="Q23",
            parameters={"equipment_id": equipment_id, "max_hops": max_hops},
            answer_type="set",
            semantic_content=reachable,
            row_count=len(reachable),
            content_hash=_compute_hash(reachable),
            full_rows=full_rows,
        )

    # =========================================================================
    # GRAPH-NATIVE (Q27-Q30) - Weighted paths, cycles, multi-hop traversals
    # =========================================================================

    def _gen_q27(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q27: Evacuation Path - Weighted shortest path to exit.

        Find shortest weighted path from a space to nearest exit space.
        Uses ADJACENT_TO and EMERGENCY_EXIT edges with distance property.
        """
        # Use evacuation_space_id (non-exit space on ground floor) if available
        space_id = params.get("evacuation_space_id") or params.get("space_id")
        if not space_id:
            return None

        # Check that source is not an exit
        source = self.nodes_by_id.get(space_id)
        if not source or source.properties.get("is_exit", False):
            return None

        # Find all exit spaces
        exit_spaces = set()
        for node in self.nodes:
            if node.type == "Space" and node.properties.get("is_exit", False):
                exit_spaces.add(node.id)

        if not exit_spaces:
            return ExpectedAnswer(
                query_id="Q27",
                parameters={"space_id": space_id},
                answer_type="path",
                semantic_content={"path": [], "total_distance": None},
                row_count=0,
                content_hash=_compute_hash([]),
                full_rows=[],
            )

        # Dijkstra's algorithm for weighted shortest path
        import heapq

        distances = {space_id: 0.0}
        predecessors = {space_id: None}
        pq = [(0.0, space_id)]
        visited = set()

        while pq:
            dist, node_id = heapq.heappop(pq)

            if node_id in visited:
                continue
            visited.add(node_id)

            # Check if we reached an exit
            if node_id in exit_spaces:
                # Reconstruct path
                path = []
                current = node_id
                while current is not None:
                    path.append(current)
                    current = predecessors[current]
                path.reverse()

                full_rows = []
                for i, nid in enumerate(path):
                    node = self.nodes_by_id.get(nid)
                    full_rows.append({
                        "step": i,
                        "space_id": nid,
                        "space_name": node.name if node else "",
                        "is_exit": node.properties.get("is_exit", False) if node else False,
                    })

                return ExpectedAnswer(
                    query_id="Q27",
                    parameters={"space_id": space_id},
                    answer_type="path",
                    semantic_content={"path": path, "total_distance": round(dist, 2)},
                    row_count=len(path),
                    content_hash=_compute_hash(path),
                    full_rows=full_rows,
                )

            # Explore neighbors via ADJACENT_TO and EMERGENCY_EXIT
            for edge in self.edges_by_source.get(node_id, []):
                if edge.rel_type in ("ADJACENT_TO", "EMERGENCY_EXIT"):
                    neighbor = edge.target_id
                    if neighbor not in visited:
                        edge_dist = edge.properties.get("distance", 10.0)
                        new_dist = dist + edge_dist
                        if neighbor not in distances or new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            predecessors[neighbor] = node_id
                            heapq.heappush(pq, (new_dist, neighbor))

        # No path found
        return ExpectedAnswer(
            query_id="Q27",
            parameters={"space_id": space_id},
            answer_type="path",
            semantic_content={"path": [], "total_distance": None},
            row_count=0,
            content_hash=_compute_hash([]),
            full_rows=[],
        )

    def _gen_q28(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q28: Tenant Impact Chain - Multi-hop traversal from SubMeter to Tenant.

        Find tenants impacted by a SubMeter via: SubMeter -[FEEDS]-> Equipment -[SERVES]-> Space <-[OCCUPIES]- Tenant
        """
        # Use submeter_id if available, fallback to meter_id
        meter_id = params.get("submeter_id") or params.get("meter_id")
        if not meter_id:
            return None

        # Get equipment fed by this meter (via FEEDS, up to 3 hops)
        fed_equipment = set()
        current = {meter_id}

        for _ in range(3):
            next_level = set()
            for node_id in current:
                for edge in self.edges_by_source.get(node_id, []):
                    if edge.rel_type == "FEEDS":
                        target = self.nodes_by_id.get(edge.target_id)
                        if target and target.type == "Equipment":
                            fed_equipment.add(edge.target_id)
                            next_level.add(edge.target_id)
            current = next_level

        # Get spaces served by this equipment
        served_spaces = set()
        for eq_id in fed_equipment:
            for edge in self.edges_by_source.get(eq_id, []):
                if edge.rel_type == "SERVES":
                    target = self.nodes_by_id.get(edge.target_id)
                    if target and target.type == "Space":
                        served_spaces.add(edge.target_id)

        # Get tenants occupying these spaces
        impacted_tenants = {}  # tenant_id -> count of affected equipment
        for space_id in served_spaces:
            for edge in self.edges_by_target.get(space_id, []):
                if edge.rel_type == "OCCUPIES":
                    tenant_id = edge.source_id
                    tenant = self.nodes_by_id.get(tenant_id)
                    if tenant and tenant.type == "Tenant":
                        if tenant_id not in impacted_tenants:
                            impacted_tenants[tenant_id] = 0
                        # Count equipment serving spaces this tenant occupies
                        for eq_id in fed_equipment:
                            for e in self.edges_by_source.get(eq_id, []):
                                if e.rel_type == "SERVES" and e.target_id == space_id:
                                    impacted_tenants[tenant_id] += 1
                                    break

        semantic = {tid: count for tid, count in impacted_tenants.items()}
        full_rows = []
        for tenant_id, eq_count in impacted_tenants.items():
            tenant = self.nodes_by_id.get(tenant_id)
            full_rows.append({
                "tenant_id": tenant_id,
                "tenant_name": tenant.name if tenant else "",
                "affected_equipment_count": eq_count,
            })

        return ExpectedAnswer(
            query_id="Q28",
            parameters={"meter_id": meter_id},
            answer_type="aggregate",
            semantic_content=semantic,
            row_count=len(impacted_tenants),
            content_hash=_compute_hash(semantic),
            full_rows=full_rows,
        )

    def _gen_q29(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q29: All Power Paths - Enumerate all paths from Transformer to critical equipment.

        Find all paths via FEEDS relationship to equipment with critical=true.
        """
        transformer_id = params.get("transformer_id")
        if not transformer_id:
            # Try to find a transformer
            for node in self.nodes:
                if node.type == "Equipment" and node.properties.get("equipment_type") == "Transformer_HT_BT":
                    transformer_id = node.id
                    break

        if not transformer_id:
            return None

        # Find all critical equipment
        critical_equipment = set()
        for node in self.nodes:
            if node.type == "Equipment" and node.properties.get("critical", False):
                critical_equipment.add(node.id)

        # DFS to find all paths to critical equipment
        all_paths = []

        def dfs(node_id: str, path: list[str], visited: set[str]):
            path = path + [node_id]

            if node_id in critical_equipment and node_id != transformer_id:
                all_paths.append(path)
                return  # Don't continue past critical equipment

            for edge in self.edges_by_source.get(node_id, []):
                if edge.rel_type == "FEEDS" and edge.target_id not in visited:
                    dfs(edge.target_id, path, visited | {edge.target_id})

        dfs(transformer_id, [], {transformer_id})

        # Limit paths for practical reasons
        limited_paths = all_paths[:100]

        full_rows = []
        for i, path in enumerate(limited_paths):
            node_ids = path
            full_rows.append({
                "path_index": i,
                "path_length": len(path),
                "path_nodes": node_ids,
                "target_id": path[-1] if path else None,
            })

        return ExpectedAnswer(
            query_id="Q29",
            parameters={"transformer_id": transformer_id},
            answer_type="paths",
            semantic_content={"paths": limited_paths, "total_count": len(all_paths)},
            row_count=len(all_paths),
            content_hash=_compute_hash(limited_paths),
            full_rows=full_rows,
        )

    def _gen_q30(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q30: Failure Impact Analysis - If equipment fails, what is impacted?

        Propagate via FEEDS to find all downstream equipment and spaces.
        """
        equipment_id = params.get("equipment_id") or params.get("meter_id")
        if not equipment_id:
            return None

        # BFS to find all impacted equipment via FEEDS
        impacted_equipment = []  # (id, name, type, hop_distance)
        impacted_spaces = []     # (space_id, space_name, equipment_id, equipment_name, hop_distance)
        visited = {equipment_id}
        queue = [(equipment_id, 0)]  # (node_id, distance)

        while queue:
            current_id, distance = queue.pop(0)
            current_node = self.nodes_by_id.get(current_id)

            # Record impacted equipment (except source at distance 0)
            if distance > 0 and current_node and current_node.type == "Equipment":
                impacted_equipment.append({
                    "impact_type": "equipment",
                    "impacted_id": current_id,
                    "impacted_name": current_node.name,
                    "impacted_subtype": current_node.properties.get("equipment_type", "Equipment"),
                    "hop_distance": distance,
                    "served_by_equipment": None,
                })

            # Find spaces served by this equipment
            for edge in self.edges_by_source.get(current_id, []):
                if edge.rel_type in ("SERVES", "MONITORS", "LOCATED_IN"):
                    space = self.nodes_by_id.get(edge.target_id)
                    if space and space.type == "Space":
                        eq_node = self.nodes_by_id.get(current_id)
                        impacted_spaces.append({
                            "impact_type": "space",
                            "impacted_id": edge.target_id,
                            "impacted_name": space.name,
                            "impacted_subtype": "Space",
                            "hop_distance": distance,
                            "served_by_equipment": eq_node.name if eq_node else None,
                        })

            # Propagate via FEEDS (only if distance < 10)
            if distance < 10:
                for edge in self.edges_by_source.get(current_id, []):
                    if edge.rel_type == "FEEDS" and edge.target_id not in visited:
                        visited.add(edge.target_id)
                        queue.append((edge.target_id, distance + 1))

        # Combine and sort results
        full_rows = impacted_equipment + impacted_spaces
        full_rows.sort(key=lambda x: (x["hop_distance"], x["impact_type"], x["impacted_id"]))

        # Semantic content: summary of impact
        semantic = {
            "source_equipment": equipment_id,
            "impacted_equipment_count": len(impacted_equipment),
            "impacted_spaces_count": len(impacted_spaces),
            "max_hop_distance": max((r["hop_distance"] for r in full_rows), default=0),
        }

        return ExpectedAnswer(
            query_id="Q30",
            parameters={"equipment_id": equipment_id},
            answer_type="impact_analysis",
            semantic_content=semantic,
            row_count=len(full_rows),
            content_hash=_compute_hash(semantic),
            full_rows=full_rows,
        )

    # =========================================================================
    # SQL-NATIVE (Q31-Q34) - Window functions, LATERAL, materialized views
    # =========================================================================

    def _gen_q31(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q31: Rolling Aggregation - Window functions on timeseries.

        Calculate rolling averages, percentiles, and stddev for points in a building.
        """
        building_id = params.get("building_id")
        if not building_id:
            return None

        # Get points in building
        points_in_building = set()
        for e1 in self.edges_by_source.get(building_id, []):
            if e1.rel_type == "CONTAINS":
                floor_id = e1.target_id
                for e2 in self.edges_by_source.get(floor_id, []):
                    if e2.rel_type == "CONTAINS":
                        space_id = e2.target_id
                        for e3 in self.edges_by_target.get(space_id, []):
                            if e3.rel_type in ("LOCATED_IN", "SERVES"):
                                eq_id = e3.source_id
                                for e4 in self.edges_by_source.get(eq_id, []):
                                    if e4.rel_type == "HAS_POINT":
                                        points_in_building.add(e4.target_id)

        # Calculate rolling stats per point (simplified - just compute basic stats)
        point_stats = {}
        for point_id in points_in_building:
            ts_data = self.ts_by_point.get(point_id, [])
            if len(ts_data) > 1:
                values = [t.value for t in ts_data]
                avg = sum(values) / len(values)
                variance = sum((v - avg) ** 2 for v in values) / len(values)
                stddev = variance ** 0.5
                sorted_vals = sorted(values)
                p95_idx = int(len(sorted_vals) * 0.95)
                p95 = sorted_vals[min(p95_idx, len(sorted_vals) - 1)]

                point_stats[point_id] = {
                    "avg": round(avg, 4),
                    "stddev": round(stddev, 4),
                    "p95": round(p95, 4),
                    "sample_count": len(values),
                }

        full_rows = []
        for point_id, stats in point_stats.items():
            full_rows.append({
                "point_id": point_id,
                "rolling_avg": stats["avg"],
                "stddev": stats["stddev"],
                "p95": stats["p95"],
            })

        return ExpectedAnswer(
            query_id="Q31",
            parameters={"building_id": building_id},
            answer_type="aggregate",
            semantic_content=point_stats,
            row_count=len(point_stats),
            content_hash=_compute_hash(point_stats),
            full_rows=full_rows,
        )

    def _gen_q32(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q32: JSON Schema Validation - Validate JSONB structure of equipment.

        Check that HVAC equipment has required protocol and metadata fields.
        """
        domain = params.get("domain", "HVAC")

        results = []
        for node in self.nodes:
            if node.type == "Equipment":
                eq_domain = node.properties.get("domain", "")
                if eq_domain == domain:
                    # Check schema requirements
                    has_protocol = bool(node.protocol)
                    has_metadata = bool(node.metadata)
                    protocol_is_object = isinstance(node.protocol, dict)
                    metadata_is_object = isinstance(node.metadata, dict)

                    is_valid = has_protocol and has_metadata and protocol_is_object and metadata_is_object
                    missing = []
                    if not has_protocol:
                        missing.append("protocol")
                    if not has_metadata:
                        missing.append("metadata")
                    if has_protocol and not protocol_is_object:
                        missing.append("protocol_type")
                    if has_metadata and not metadata_is_object:
                        missing.append("metadata_type")

                    results.append({
                        "equipment_id": node.id,
                        "name": node.name,
                        "schema_status": "valid" if is_valid else "invalid",
                        "missing_fields": missing,
                    })

        semantic = {r["equipment_id"]: r["schema_status"] for r in results}

        return ExpectedAnswer(
            query_id="Q32",
            parameters={"domain": domain},
            answer_type="aggregate",
            semantic_content=semantic,
            row_count=len(results),
            content_hash=_compute_hash(semantic),
            full_rows=results,
        )

    def _gen_q33(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q33: Latest Value per Space - LATERAL JOIN equivalent.

        Get latest timeseries value for each point serving each space in building.
        """
        building_id = params.get("building_id")
        if not building_id:
            return None

        results = []
        # Get spaces in building
        for e1 in self.edges_by_source.get(building_id, []):
            if e1.rel_type == "CONTAINS":
                floor_id = e1.target_id
                for e2 in self.edges_by_source.get(floor_id, []):
                    if e2.rel_type == "CONTAINS":
                        space_id = e2.target_id
                        space = self.nodes_by_id.get(space_id)

                        # Get equipment serving this space
                        for e3 in self.edges_by_target.get(space_id, []):
                            if e3.rel_type == "SERVES":
                                eq_id = e3.source_id
                                # Get points on equipment
                                for e4 in self.edges_by_source.get(eq_id, []):
                                    if e4.rel_type == "HAS_POINT":
                                        point_id = e4.target_id
                                        point = self.nodes_by_id.get(point_id)

                                        # Get latest timeseries value
                                        ts_data = self.ts_by_point.get(point_id, [])
                                        if ts_data:
                                            latest = max(ts_data, key=lambda t: t.timestamp)
                                            results.append({
                                                "space_id": space_id,
                                                "space_name": space.name if space else "",
                                                "point_id": point_id,
                                                "quantity": point.properties.get("quantity") if point else "",
                                                "last_value": latest.value,
                                                "last_time": latest.timestamp.isoformat(),
                                            })

        semantic = {f"{r['space_id']}:{r['point_id']}": r["last_value"] for r in results}

        return ExpectedAnswer(
            query_id="Q33",
            parameters={"building_id": building_id},
            answer_type="aggregate",
            semantic_content=semantic,
            row_count=len(results),
            content_hash=_compute_hash(semantic),
            full_rows=results,
        )

    def _gen_q34(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q34: Materialized Energy Summary - Pre-computed daily aggregates.

        Calculate daily energy consumption per building (simulates materialized view).
        """
        building_id = params.get("building_id")
        if not building_id:
            return None

        # Get energy points in building
        energy_points = set()
        for e1 in self.edges_by_source.get(building_id, []):
            if e1.rel_type == "CONTAINS":
                floor_id = e1.target_id
                for e2 in self.edges_by_source.get(floor_id, []):
                    if e2.rel_type == "CONTAINS":
                        space_id = e2.target_id
                        for e3 in self.edges_by_target.get(space_id, []):
                            if e3.rel_type in ("LOCATED_IN", "SERVES"):
                                eq_id = e3.source_id
                                for e4 in self.edges_by_source.get(eq_id, []):
                                    if e4.rel_type == "HAS_POINT":
                                        point_id = e4.target_id
                                        point = self.nodes_by_id.get(point_id)
                                        if point and point.properties.get("quantity") == "energy":
                                            energy_points.add(point_id)

        # Aggregate by day
        daily_data: dict[str, dict] = defaultdict(lambda: {"total": 0.0, "peak": 0.0, "meters": set()})

        for point_id in energy_points:
            for ts in self.ts_by_point.get(point_id, []):
                day = ts.timestamp.date().isoformat()
                daily_data[day]["total"] += ts.value
                daily_data[day]["peak"] = max(daily_data[day]["peak"], ts.value)
                daily_data[day]["meters"].add(point_id)

        results = []
        for day, data in sorted(daily_data.items()):
            results.append({
                "building_id": building_id,
                "day": day,
                "total_energy_kwh": round(data["total"], 2),
                "peak_power_kw": round(data["peak"], 2),
                "meter_count": len(data["meters"]),
            })

        semantic = {r["day"]: r["total_energy_kwh"] for r in results}

        return ExpectedAnswer(
            query_id="Q34",
            parameters={"building_id": building_id},
            answer_type="aggregate",
            semantic_content=semantic,
            row_count=len(results),
            content_hash=_compute_hash(semantic),
            full_rows=results,
        )

    # =========================================================================
    # JSONB VALIDATION QUERIES (Q24-Q26) - Expected results after QW writes
    # =========================================================================

    def _gen_q24(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q24: Maintenance History - validates QW4 write.

        Expected result after QW4 adds a maintenance event.
        Uses qw4_equipment_id and qw4_event from params.
        """
        equipment_id = params.get("qw4_equipment_id") or params.get("equipment_id")
        event = params.get("qw4_event")

        if not equipment_id:
            return None

        equipment = self.nodes_by_id.get(equipment_id)
        if not equipment:
            return None

        # Expected result: the event that QW4 will write
        expected_event = event or {
            "date": params.get("reference_date", "2024-06-01"),
            "type": "preventive",
            "technician": "Tech_Benchmark",
            "description": "Benchmark test maintenance event",
            "cost": 150.0,
            "parts_replaced": ["filter", "belt"],
        }

        result = {
            "equipment_id": equipment_id,
            "name": equipment.name,
            "event_count": 1,
            "last_event": expected_event,
            "last_event_date": expected_event.get("date"),
            "last_technician": expected_event.get("technician"),
            "total_maintenance_cost": expected_event.get("cost", 0),
            "all_parts_replaced": expected_event.get("parts_replaced", []),
        }

        return ExpectedAnswer(
            query_id="Q24",
            parameters={"equipment_id": equipment_id},
            answer_type="document",
            semantic_content=result,
            row_count=1,
            content_hash=_compute_hash(result),
            full_rows=[result],
        )

    def _gen_q25(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q25: Equipment Audit Trail - validates QW5 and QW6 writes.

        Expected result after QW5 updates calibration and QW6 merges firmware.
        """
        equipment_id = params.get("qw6_equipment_id") or params.get("equipment_id")
        point_id = params.get("qw5_point_id") or params.get("point_id")

        if not equipment_id:
            return None

        equipment = self.nodes_by_id.get(equipment_id)
        if not equipment:
            return None

        # Expected firmware from QW6
        firmware_version = "3.2.1"
        last_firmware_update = params.get("reference_date", "2024-06-01")

        # Expected calibration from QW5
        calibration_date = params.get("qw5_calibration_date", params.get("reference_date", "2024-06-01"))
        next_calibration = params.get("qw5_next_date", "2025-06-01")
        technician = params.get("qw5_technician", "Calibration_Corp")

        result = {
            "equipment_id": equipment_id,
            "name": equipment.name,
            "equipment_type": equipment.properties.get("equipment_type", "Equipment"),
            "current_firmware": firmware_version,
            "last_firmware_update": last_firmware_update,
            "maintenance_events": 0,  # No maintenance yet in Q25 scope
            "last_maintenance_date": None,
            "points_calibration_status": {
                "point_id": point_id,
                "calibration_date": calibration_date,
                "next_calibration": next_calibration,
                "technician": technician,
            } if point_id else None,
            "health_status": "good",
        }

        return ExpectedAnswer(
            query_id="Q25",
            parameters={"equipment_id": equipment_id},
            answer_type="document",
            semantic_content=result,
            row_count=1,
            content_hash=_compute_hash(result),
            full_rows=[result],
        )

    def _gen_q26(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q26: Capability Evolution - validates QW7 write.

        Expected result: distribution of capabilities including the one added by QW7.
        """
        domain = params.get("domain", "HVAC")
        new_capability = params.get("qw7_new_capability", "demand_control_ventilation")
        target_equipment_id = params.get("qw7_equipment_id")

        # Count equipment by type and capabilities
        type_stats: dict[str, dict] = defaultdict(lambda: {
            "count": 0,
            "capabilities": defaultdict(int),
        })

        hvac_types = {"AHU", "VAV", "FCU", "Chiller", "Boiler", "HeatPump", "CoolingTower", "RTU"}

        for node in self.nodes:
            if node.type == "Equipment":
                eq_type = node.properties.get("equipment_type", "Unknown")

                # Filter by domain (HVAC = hvac_types)
                if domain == "HVAC" and eq_type not in hvac_types:
                    continue

                type_stats[eq_type]["count"] += 1

                # Count capabilities
                capabilities = node.capabilities or []

                # If this is the target equipment for QW7, add the new capability
                if node.id == target_equipment_id and new_capability not in capabilities:
                    capabilities = capabilities + [new_capability]

                for cap in capabilities:
                    type_stats[eq_type]["capabilities"][cap] += 1

        results = []
        for eq_type, stats in sorted(type_stats.items(), key=lambda x: -x[1]["count"]):
            cap_dist = dict(stats["capabilities"])
            most_common = max(cap_dist, key=cap_dist.get) if cap_dist else None
            avg_caps = sum(cap_dist.values()) / stats["count"] if stats["count"] > 0 else 0

            results.append({
                "equipment_type": eq_type,
                "equipment_count": stats["count"],
                "capabilities_distribution": cap_dist,
                "most_common_capability": most_common,
                "avg_capabilities": round(avg_caps, 2),
            })

        semantic = {r["equipment_type"]: r["equipment_count"] for r in results}

        return ExpectedAnswer(
            query_id="Q26",
            parameters={"domain": domain},
            answer_type="aggregate",
            semantic_content=semantic,
            row_count=len(results),
            content_hash=_compute_hash(semantic),
            full_rows=results,
        )

    # =========================================================================
    # WRITE VALIDATION QUERIES (Q35-Q38) - Validate QW write operations
    # =========================================================================

    def _gen_q35(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q35: Validate Timeseries Append - validates QW1 write.

        Expected result after QW1 adds timeseries data.
        Uses qw1_* params from generator.
        """
        point_id = params.get("point_id")
        reference_date = params.get("reference_date")

        if not point_id:
            return None

        # Get QW1 parameters (what will be written)
        qw1_timestamps = params.get("qw1_timestamps", [])
        qw1_values = params.get("qw1_values", [])

        if not qw1_timestamps or not qw1_values:
            return None

        # Expected result: the data that QW1 will write
        result = {
            "point_id": point_id,
            "chunk_date": reference_date[:10] if isinstance(reference_date, str) else str(reference_date)[:10],
            "timestamp_count": len(qw1_timestamps),
            "value_count": len(qw1_values),
            "last_timestamps": qw1_timestamps[-3:] if len(qw1_timestamps) >= 3 else qw1_timestamps,
            "last_values": qw1_values[-3:] if len(qw1_values) >= 3 else qw1_values,
        }

        return ExpectedAnswer(
            query_id="Q35",
            parameters={"point_id": point_id, "reference_date": reference_date},
            answer_type="document",
            semantic_content=result,
            row_count=1,
            content_hash=_compute_hash(result),
            full_rows=[result],
        )

    def _gen_q36(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q36: Validate Metadata Tag Update - validates QW2 write.

        Expected result after QW2 updates the custom_tag property.
        Uses qw2_* params from generator.
        """
        node_id = params.get("qw2_node_id") or params.get("equipment_id")
        tag_value = params.get("qw2_tag_value", "verified_2024")

        if not node_id:
            return None

        node = self.nodes_by_id.get(node_id)
        if not node:
            return None

        # Expected result: the tag value that QW2 will set
        result = {
            "node_id": node_id,
            "node_name": node.name,
            "custom_tag": tag_value,
            "node_type": node.type,
        }

        return ExpectedAnswer(
            query_id="Q36",
            parameters={"node_id": node_id},
            answer_type="document",
            semantic_content=result,
            row_count=1,
            content_hash=_compute_hash(result),
            full_rows=[result],
        )

    def _gen_q37(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q37: Validate Relation Mutation - validates QW3 write.

        Expected result after QW3 creates a FEEDS relation.
        Uses qw3_* params from generator.
        """
        source_id = params.get("qw3_source_id") or params.get("meter_id")
        target_id = params.get("qw3_target_id") or params.get("equipment_id")

        if not source_id or not target_id:
            return None

        source_node = self.nodes_by_id.get(source_id)
        target_node = self.nodes_by_id.get(target_id)

        if not source_node or not target_node:
            return None

        # Expected result: the relation that QW3 will create
        result = {
            "source_id": source_id,
            "source_name": source_node.name,
            "rel_type": "FEEDS",
            "target_id": target_id,
            "target_name": target_node.name,
        }

        return ExpectedAnswer(
            query_id="Q37",
            parameters={"source_id": source_id, "target_id": target_id},
            answer_type="document",
            semantic_content=result,
            row_count=1,
            content_hash=_compute_hash(result),
            full_rows=[result],
        )

    def _gen_q38(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q38: Validate Property Removal - validates QW8 write.

        Expected result after QW8 removes the custom_tag property.
        Uses qw8_* params from generator.
        """
        node_id = params.get("qw8_node_id") or params.get("equipment_id")

        if not node_id:
            return None

        node = self.nodes_by_id.get(node_id)
        if not node:
            return None

        # Expected result: custom_tag should be removed (NULL)
        result = {
            "node_id": node_id,
            "node_name": node.name,
            "tag_removed": True,
            "remaining_keys": [],  # Will be filled by actual query
        }

        return ExpectedAnswer(
            query_id="Q38",
            parameters={"node_id": node_id},
            answer_type="document",
            semantic_content=result,
            row_count=1,
            content_hash=_compute_hash(result),
            full_rows=[result],
        )

    # =========================================================================
    # TENANT VALIDATION QUERIES (Q39-Q41) - Validate QW9-QW12 tenant operations
    # =========================================================================

    def _gen_q39(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q39: Verify Tenant Spaces - validates QW9/QW10/QW11 writes.

        Lists all spaces occupied by a tenant via OCCUPIES relationship.
        """
        tenant_id = params.get("tenant_id")
        if not tenant_id:
            return None

        # Find all spaces this tenant occupies
        occupied_spaces = set()
        full_rows = []

        for edge in self.edges_by_source.get(tenant_id, []):
            if edge.rel_type == "OCCUPIES":
                space_id = edge.target_id
                occupied_spaces.add(space_id)
                space = self.nodes_by_id.get(space_id)
                full_rows.append({
                    "space_id": space_id,
                    "space_name": space.name if space else "",
                    "space_type": space.type if space else "",
                })

        full_rows.sort(key=lambda x: x["space_id"])

        return ExpectedAnswer(
            query_id="Q39",
            parameters={"tenant_id": tenant_id},
            answer_type="set",
            semantic_content=occupied_spaces,
            row_count=len(occupied_spaces),
            content_hash=_compute_hash(occupied_spaces),
            full_rows=full_rows,
        )

    def _gen_q40(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q40: Verify Tenant Meters - validates QW9 meter association.

        Lists all meters associated with a tenant via METERS_TENANT relationship.
        Note: METERS_TENANT goes (meter)-[:METERS_TENANT]->(tenant)
        """
        tenant_id = params.get("tenant_id")
        if not tenant_id:
            return None

        # Find all meters pointing to this tenant
        associated_meters = set()
        full_rows = []

        for edge in self.edges_by_target.get(tenant_id, []):
            if edge.rel_type == "METERS_TENANT":
                meter_id = edge.source_id
                associated_meters.add(meter_id)
                meter = self.nodes_by_id.get(meter_id)
                full_rows.append({
                    "meter_id": meter_id,
                    "meter_name": meter.name if meter else "",
                    "meter_type": meter.type if meter else "",
                })

        full_rows.sort(key=lambda x: x["meter_id"])

        return ExpectedAnswer(
            query_id="Q40",
            parameters={"tenant_id": tenant_id},
            answer_type="set",
            semantic_content=associated_meters,
            row_count=len(associated_meters),
            content_hash=_compute_hash(associated_meters),
            full_rows=full_rows,
        )

    def _gen_q41(self, params: dict[str, Any]) -> ExpectedAnswer:
        """Q41: Verify Tenant Consolidation - validates QW12 merge.

        Returns counts of OCCUPIES and METERS_TENANT relations for a tenant.
        Used to verify that all relations were transferred during merge.
        """
        tenant_id = params.get("tenant_id")
        if not tenant_id:
            return None

        # Count OCCUPIES relations (tenant is source)
        occupied_count = 0
        for edge in self.edges_by_source.get(tenant_id, []):
            if edge.rel_type == "OCCUPIES":
                occupied_count += 1

        # Count METERS_TENANT relations (tenant is target)
        metered_count = 0
        for edge in self.edges_by_target.get(tenant_id, []):
            if edge.rel_type == "METERS_TENANT":
                metered_count += 1

        result = {
            "tenant_id": tenant_id,
            "occupied_spaces": occupied_count,
            "associated_meters": metered_count,
        }

        return ExpectedAnswer(
            query_id="Q41",
            parameters={"tenant_id": tenant_id},
            answer_type="aggregate",
            semantic_content=result,
            row_count=1,
            content_hash=_compute_hash(result),
            full_rows=[result],
        )


def write_expected_answers(
    answers: dict[str, ExpectedAnswer],
    output_dir: Path,
) -> None:
    """Write expected answers to JSON files.

    Args:
        answers: Dict mapping query_id to ExpectedAnswer
        output_dir: Directory to write to (creates expected_answers/ subdir)
    """
    answers_dir = Path(output_dir) / "expected_answers"
    answers_dir.mkdir(parents=True, exist_ok=True)

    # Write each answer
    for query_id, answer in answers.items():
        answer_file = answers_dir / f"{query_id}.json"
        with open(answer_file, "w", encoding="utf-8") as f:
            json.dump(answer.to_dict(), f, indent=2, default=str)

    # Write metadata
    metadata = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "query_count": len(answers),
        "queries": sorted(answers.keys()),
    }

    metadata_file = answers_dir / "metadata.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Generated {len(answers)} expected answers in {answers_dir}")
