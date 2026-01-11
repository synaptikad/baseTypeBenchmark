"""
Data Models for Dataset Generation - Benchmark BaseType V3

Dataclasses partagées entre les différents modules de génération de données.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List


@dataclass
class Node:
    """Nœud du graphe"""
    id: str
    type: str  # Site, Building, Floor, Space, Equipment, Point, Tenant, Contract, Ticket, Zone
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    # Propriétés JSONB (P2 uniquement)
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    protocol: Dict[str, Any] = field(default_factory=dict)
    calibration: Dict[str, Any] = field(default_factory=dict)
    range_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """Relation entre nœuds"""
    source_id: str
    target_id: str
    rel_type: str  # FEEDS, SERVES, CONTAINS, HAS_POINT, etc.
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimeseriesPoint:
    """Point de mesure timeseries"""
    point_id: str
    timestamp: datetime
    value: float
