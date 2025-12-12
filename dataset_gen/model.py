"""Définition du modèle conceptuel pour le dataset synthétique."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


class NodeType(str, Enum):
    SITE = "Site"
    BUILDING = "Building"
    FLOOR = "Floor"
    SPACE = "Space"
    EQUIPMENT = "Equipment"
    POINT = "Point"
    METER = "Meter"
    TENANT = "Tenant"


class RelationType(str, Enum):
    CONTAINS = "CONTAINS"
    LOCATED_IN = "LOCATED_IN"
    HAS_PART = "HAS_PART"
    HAS_POINT = "HAS_POINT"
    MEASURES = "MEASURES"
    CONTROLS = "CONTROLS"
    FEEDS = "FEEDS"
    SERVES = "SERVES"
    OCCUPIES = "OCCUPIES"


POINT_QUANTITIES = [
    "temperature",
    "co2",
    "power",
    "flow",
    "status",
    "command",
]


@dataclass
class Node:
    id: str
    type: NodeType
    name: str


@dataclass
class Edge:
    src: str
    dst: str
    rel: RelationType


@dataclass
class MeasuresEdge:
    src: str
    quantity: str


def relation_targets() -> Dict[RelationType, List[Tuple[NodeType, NodeType]]]:
    """Couples source/destination autorisés pour les relations orientées."""

    return {
        RelationType.CONTAINS: [
            (NodeType.SITE, NodeType.BUILDING),
            (NodeType.BUILDING, NodeType.FLOOR),
            (NodeType.FLOOR, NodeType.SPACE),
        ],
        RelationType.LOCATED_IN: [(NodeType.EQUIPMENT, NodeType.SPACE)],
        RelationType.HAS_PART: [(NodeType.EQUIPMENT, NodeType.EQUIPMENT)],
        RelationType.HAS_POINT: [(NodeType.EQUIPMENT, NodeType.POINT)],
        RelationType.CONTROLS: [(NodeType.POINT, NodeType.EQUIPMENT)],
        RelationType.FEEDS: [
            (NodeType.METER, NodeType.EQUIPMENT),
            (NodeType.METER, NodeType.METER),
        ],
        RelationType.SERVES: [(NodeType.EQUIPMENT, NodeType.SPACE)],
        RelationType.OCCUPIES: [(NodeType.TENANT, NodeType.SPACE)],
    }
