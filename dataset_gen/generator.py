"""Génération déterministe d'un dataset bâtimentaire synthétique."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from random import Random
from typing import Dict, Iterable, List, Tuple

from .config import ScaleProfile
from .model import Edge, MeasuresEdge, Node, NodeType, RelationType


@dataclass
class Dataset:
    nodes: List[Node]
    edges: List[Edge]
    measures: List[MeasuresEdge]


@dataclass
class Summary:
    node_count: int
    relation_counts: Dict[RelationType, int]
    max_depth: int
    max_feeds_depth: int
    max_functional_depth: int


class IdFactory:
    def __init__(self) -> None:
        self.counters: Dict[str, int] = defaultdict(int)

    def new(self, prefix: str) -> str:
        self.counters[prefix] += 1
        return f"{prefix}-{self.counters[prefix]}"


def _allocate_per_bucket(total: int, buckets: int, rng: Random) -> List[int]:
    raw_weights = [max(0.2, rng.gauss(1.0, 0.2)) for _ in range(buckets)]
    s = sum(raw_weights)
    scaled = [w / s * total for w in raw_weights]
    counts = [max(0, int(round(v))) for v in scaled]
    diff = total - sum(counts)
    while diff != 0:
        for i in range(buckets):
            if diff == 0:
                break
            counts[i] += 1 if diff > 0 else -1 if counts[i] > 0 else 0
            diff = total - sum(counts)
    return counts


def generate_dataset(profile: ScaleProfile, seed: int) -> Tuple[Dataset, Summary]:
    rng = Random(seed)
    factory = IdFactory()

    nodes: List[Node] = []
    edges: List[Edge] = []
    measures: List[MeasuresEdge] = []

    site = Node(id=factory.new("site"), type=NodeType.SITE, name="Site principal")
    nodes.append(site)

    building = Node(id=factory.new("building"), type=NodeType.BUILDING, name="Immeuble A")
    nodes.append(building)
    edges.append(Edge(src=site.id, dst=building.id, rel=RelationType.CONTAINS))

    floors: List[Node] = []
    for i in range(profile.floors):
        floor = Node(
            id=factory.new("floor"),
            type=NodeType.FLOOR,
            name=f"Étage {i}",
        )
        floors.append(floor)
        nodes.append(floor)
        edges.append(Edge(src=building.id, dst=floor.id, rel=RelationType.CONTAINS))

    spaces: List[Node] = []
    spaces_per_floor = _allocate_per_bucket(profile.spaces, len(floors), rng)
    for floor, count in zip(floors, spaces_per_floor):
        for _ in range(count):
            space = Node(
                id=factory.new("space"),
                type=NodeType.SPACE,
                name=f"Espace {floor.name}-{factory.counters['space']}",
            )
            spaces.append(space)
            nodes.append(space)
            edges.append(Edge(src=floor.id, dst=space.id, rel=RelationType.CONTAINS))

    equipments: List[Node] = []
    equipment_per_space = _allocate_per_bucket(profile.equipments, len(spaces), rng)
    for space, count in zip(spaces, equipment_per_space):
        assigned = max(1, count)
        for _ in range(assigned):
            equip = Node(
                id=factory.new("equip"),
                type=NodeType.EQUIPMENT,
                name=f"Equipement {factory.counters['equip']}",
            )
            equipments.append(equip)
            nodes.append(equip)
            edges.append(Edge(src=equip.id, dst=space.id, rel=RelationType.LOCATED_IN))
            edges.append(Edge(src=equip.id, dst=space.id, rel=RelationType.SERVES))

    rng.shuffle(equipments)
    functional_layers: List[List[Node]] = []
    remaining = list(equipments)
    depth = 0
    while remaining and depth < 6:
        layer_size = max(1, len(remaining) // 4)
        layer = remaining[:layer_size]
        functional_layers.append(layer)
        remaining = remaining[layer_size:]
        if depth > 0:
            for child in layer:
                parent = rng.choice(functional_layers[depth - 1])
                edges.append(Edge(src=parent.id, dst=child.id, rel=RelationType.HAS_PART))
        depth += 1

    points: List[Node] = []
    base_points = 3
    remaining_points = profile.points - base_points * len(equipments)
    extras = [0 for _ in equipments]
    if remaining_points > 0:
        raw_allocation = _allocate_per_bucket(remaining_points, len(equipments), rng)
        extras = [min(7, value) for value in raw_allocation]
        diff = remaining_points - sum(extras)
        capacities = [7 - value for value in extras]
        while diff > 0 and any(c > 0 for c in capacities):
            for idx in rng.sample(range(len(equipments)), len(equipments)):
                if capacities[idx] <= 0:
                    continue
                extras[idx] += 1
                capacities[idx] -= 1
                diff -= 1
                if diff <= 0:
                    break

    for equip, extra in zip(equipments, extras):
        point_count = min(10, base_points + extra)
        for i in range(point_count):
            point = Node(
                id=factory.new("point"),
                type=NodeType.POINT,
                name=f"Point {equip.id}-{i}",
            )
            points.append(point)
            nodes.append(point)
            edges.append(Edge(src=equip.id, dst=point.id, rel=RelationType.HAS_POINT))
            quantity = _sample_quantity(rng)
            measures.append(MeasuresEdge(src=point.id, quantity=quantity))
            if quantity in {"command", "status"} and rng.random() < 0.7:
                edges.append(Edge(src=point.id, dst=equip.id, rel=RelationType.CONTROLS))

    meters: List[Node] = []
    root_meter = Node(id=factory.new("meter"), type=NodeType.METER, name="Point de livraison")
    meters.append(root_meter)
    nodes.append(root_meter)
    meter_tree: List[List[Node]] = [[root_meter]]
    remaining_meters = profile.meters - 1
    depth = 0
    while remaining_meters > 0 and depth < 7:
        parents = meter_tree[depth]
        level: List[Node] = []
        for parent in parents:
            if remaining_meters <= 0:
                break
            children = rng.randint(1, 3)
            for _ in range(children):
                if remaining_meters <= 0:
                    break
                child = Node(
                    id=factory.new("meter"),
                    type=NodeType.METER,
                    name=f"Sous-compteur {factory.counters['meter']}",
                )
                nodes.append(child)
                meters.append(child)
                level.append(child)
                edges.append(Edge(src=parent.id, dst=child.id, rel=RelationType.FEEDS))
                remaining_meters -= 1
        if level:
            meter_tree.append(level)
            depth += 1
        else:
            break

    leaf_meters = meter_tree[-1]
    for equip in equipments:
        meter = rng.choice(leaf_meters)
        edges.append(Edge(src=meter.id, dst=equip.id, rel=RelationType.FEEDS))

    tenants: List[Node] = []
    tenant_count = max(1, len(spaces) // 40)
    selected_spaces = rng.sample(spaces, min(tenant_count * 3, len(spaces)))
    for idx in range(tenant_count):
        tenant = Node(id=factory.new("tenant"), type=NodeType.TENANT, name=f"Locataire {idx+1}")
        tenants.append(tenant)
        nodes.append(tenant)
        occupied = selected_spaces[idx : idx + 3]
        for space in occupied:
            edges.append(Edge(src=tenant.id, dst=space.id, rel=RelationType.OCCUPIES))

    relation_counts = _count_relations(edges, measures)
    max_depth = _compute_global_depth(nodes, edges)
    max_feeds_depth = _compute_depth_by_type(edges, RelationType.FEEDS)
    max_functional_depth = _compute_depth_by_type(edges, RelationType.HAS_PART)

    return Dataset(nodes=nodes, edges=edges, measures=measures), Summary(
        node_count=len(nodes),
        relation_counts=relation_counts,
        max_depth=max_depth,
        max_feeds_depth=max_feeds_depth,
        max_functional_depth=max_functional_depth,
    )


def _sample_quantity(rng: Random) -> str:
    weights = {
        "temperature": 0.25,
        "co2": 0.1,
        "power": 0.25,
        "flow": 0.15,
        "status": 0.15,
        "command": 0.1,
    }
    choices = list(weights.items())
    total = sum(w for _, w in choices)
    pick = rng.random() * total
    cumulative = 0.0
    for quantity, weight in choices:
        cumulative += weight
        if pick <= cumulative:
            return quantity
    return "command"


def _count_relations(edges: Iterable[Edge], measures: Iterable[MeasuresEdge]) -> Dict[RelationType, int]:
    counts: Dict[RelationType, int] = defaultdict(int)
    for edge in edges:
        counts[edge.rel] += 1
    counts[RelationType.MEASURES] = len(list(measures))
    return counts


def _compute_global_depth(nodes: Iterable[Node], edges: Iterable[Edge]) -> int:
    adjacency: Dict[str, List[str]] = defaultdict(list)
    for edge in edges:
        adjacency[edge.src].append(edge.dst)

    max_depth = 0
    for node in nodes:
        max_depth = max(max_depth, _depth_from(node.id, adjacency, limit=10))
    return max_depth


def _depth_from(start: str, adjacency: Dict[str, List[str]], limit: int) -> int:
    max_depth = 0
    stack: List[Tuple[str, int]] = [(start, 0)]
    visited_edges = set()
    while stack:
        node, depth = stack.pop()
        max_depth = max(max_depth, depth)
        if depth >= limit:
            continue
        for neighbor in adjacency.get(node, []):
            edge_id = (node, neighbor)
            if edge_id in visited_edges:
                continue
            visited_edges.add(edge_id)
            stack.append((neighbor, depth + 1))
    return max_depth


def _compute_depth_by_type(edges: Iterable[Edge], rel: RelationType) -> int:
    adjacency: Dict[str, List[str]] = defaultdict(list)
    for edge in edges:
        if edge.rel == rel:
            adjacency[edge.src].append(edge.dst)

    max_depth = 0
    for src in adjacency:
        max_depth = max(max_depth, _depth_from(src, adjacency, limit=10))
    return max_depth
