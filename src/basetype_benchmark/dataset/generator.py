"""Génération déterministe d'un dataset bâtimentaire synthétique.

Ce générateur produit un dataset couvrant TOUS les domaines d'un smart building/campus:
- Spatial: Site → Building(s) → Floor → Space → Zone
- Équipements: Systems, Equipment, Sensors, Actuators, Controllers
- Énergie: Meters (arbre de distribution), EnergyZones
- IT/Datacenter: Datacenter → Rack → Server/NetworkDevice/Storage
- Audiovisuel: AVSystem → Display/Projector/Speaker/ConferenceUnit
- Parking: ParkingZone → ParkingLevel → ParkingSpot, ChargingStation, Vehicle
- Sécurité: SecurityZone → AccessPoint/Camera/Alarm/IntrusionDetector
- Organisation: Organization → Department → Team → Person
- Contractuel: Contract, Provider, Lease, WorkOrder

Architecture multi-bâtiments pour extraction dynamique:
- Le dataset complet (large-1y) contient N bâtiments
- Chaque entité porte un building_id hérité
- L'extraction par scale filtre simplement par building_id:
  - small  = building 1
  - medium = buildings 1-5
  - large  = tous les buildings
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import Random
from typing import Any, Dict, List, Optional, Tuple
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from basetype_benchmark.dataset.config import ScaleProfile, TIMESERIES_RATIO
from basetype_benchmark.dataset.model import (
    Edge, MeasuresEdge, Node, NodeType, RelationType, TimeseriesChunk,
    TIMESERIES_QUANTITIES, POINT_QUANTITIES
)


# =============================================================================
# Configuration multi-bâtiments
# =============================================================================

# Mapping scale -> building_ids pour l'extraction
SCALE_BUILDINGS = {
    "small": [1],                    # Building 1 seulement
    "medium": [1, 2, 3, 4, 5],       # Buildings 1-5
    "large": None,                   # Tous (pas de filtre)
}

# Nombre de bâtiments pour le profil large
NUM_BUILDINGS_LARGE = 10

# Répartition des ressources par bâtiment (pondération)
# Building 1 (small) = 20%, Buildings 2-5 (medium) = 40%, Buildings 6-10 = 40%
BUILDING_WEIGHTS = {
    1: 0.20,   # small tier
    2: 0.10, 3: 0.10, 4: 0.10, 5: 0.10,  # medium tier (10% chacun)
    6: 0.08, 7: 0.08, 8: 0.08, 9: 0.08, 10: 0.08,  # large tier (8% chacun)
}


# =============================================================================
# Dataclasses pour le dataset
# =============================================================================

@dataclass
class Dataset:
    """Dataset complet généré."""
    nodes: List[Node]
    edges: List[Edge]
    measures: List[MeasuresEdge]
    timeseries: List[TimeseriesChunk]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le dataset en dictionnaires pour export."""
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "measures": [{"src": m.src, "quantity": m.quantity} for m in self.measures],
        }


@dataclass
class Summary:
    """Résumé statistique du dataset."""
    node_count: int
    edge_count: int
    node_types: Dict[str, int]
    relation_counts: Dict[str, int]
    max_depth: int
    timeseries_points: int
    timeseries_samples: int
    buildings_count: int = 1
    building_stats: Dict[int, Dict[str, int]] = field(default_factory=dict)


# =============================================================================
# Factory pour les identifiants
# =============================================================================

class IdFactory:
    """Génère des identifiants uniques par type."""

    def __init__(self) -> None:
        self.counters: Dict[str, int] = defaultdict(int)

    def new(self, prefix: str) -> str:
        self.counters[prefix] += 1
        return f"{prefix}-{self.counters[prefix]}"

    def count(self, prefix: str) -> int:
        return self.counters.get(prefix, 0)


# =============================================================================
# Contexte de génération (pour propager building_id)
# =============================================================================

@dataclass
class BuildingContext:
    """Contexte pour la génération d'un bâtiment."""
    building_id: int
    building_node: Node
    floors: List[Node] = field(default_factory=list)
    spaces: List[Node] = field(default_factory=list)
    zones: List[Node] = field(default_factory=list)
    equipments: List[Node] = field(default_factory=list)
    systems: List[Node] = field(default_factory=list)
    meters: List[Node] = field(default_factory=list)
    points: List[Node] = field(default_factory=list)


# =============================================================================
# Utilitaires
# =============================================================================

def _allocate_per_bucket(total: int, buckets: int, rng: Random) -> List[int]:
    """Distribue un total sur N buckets avec variation gaussienne."""
    if buckets == 0:
        return []
    raw_weights = [max(0.2, rng.gauss(1.0, 0.2)) for _ in range(buckets)]
    s = sum(raw_weights)
    scaled = [w / s * total for w in raw_weights]
    counts = [max(0, int(round(v))) for v in scaled]
    diff = total - sum(counts)
    while diff != 0:
        for i in range(buckets):
            if diff == 0:
                break
            if diff > 0:
                counts[i] += 1
            elif counts[i] > 0:
                counts[i] -= 1
            diff = total - sum(counts)
    return counts


def _allocate_by_weights(total: int, weights: Dict[int, float]) -> Dict[int, int]:
    """Distribue un total selon des poids par clé."""
    total_weight = sum(weights.values())
    result = {}
    remaining = total
    for key, weight in weights.items():
        count = int(round(total * weight / total_weight))
        result[key] = min(count, remaining)
        remaining -= result[key]
    # Distribuer le reste
    if remaining > 0:
        for key in weights:
            if remaining <= 0:
                break
            result[key] += 1
            remaining -= 1
    return result


def _sample_from_weights(weights: Dict[str, float], rng: Random) -> str:
    """Échantillonne une clé selon des poids."""
    choices = list(weights.items())
    total = sum(w for _, w in choices)
    pick = rng.random() * total
    cumulative = 0.0
    for key, weight in choices:
        cumulative += weight
        if pick <= cumulative:
            return key
    return choices[-1][0]


def _create_node(
    factory: IdFactory,
    prefix: str,
    node_type: NodeType,
    name: str,
    properties: Dict[str, Any],
    building_id: int,
) -> Node:
    """Crée un nœud avec building_id dans les properties."""
    props = dict(properties)
    props["building_id"] = building_id
    return Node(
        id=factory.new(prefix),
        type=node_type,
        name=name,
        properties=props,
    )


# =============================================================================
# Générateur principal (multi-bâtiments)
# =============================================================================

def generate_dataset(profile: ScaleProfile, seed: int) -> Tuple[Dataset, Summary]:
    """Génère un dataset complet selon le profil spécifié.

    Le dataset contient plusieurs bâtiments pour permettre l'extraction
    dynamique par scale (small/medium/large).

    Args:
        profile: Profil de volumétrie (small, medium, large)
        seed: Graine pour reproductibilité

    Returns:
        Tuple (Dataset, Summary)
    """
    rng = Random(seed)
    factory = IdFactory()

    nodes: List[Node] = []
    edges: List[Edge] = []
    measures: List[MeasuresEdge] = []
    building_contexts: List[BuildingContext] = []

    # Déterminer le nombre de bâtiments
    num_buildings = _get_num_buildings(profile)

    # Calculer la répartition des ressources par bâtiment
    building_weights = {i: BUILDING_WEIGHTS.get(i, 0.05) for i in range(1, num_buildings + 1)}

    floors_per_building = _allocate_by_weights(profile.floors, building_weights)
    spaces_per_building = _allocate_by_weights(profile.spaces, building_weights)
    equips_per_building = _allocate_by_weights(profile.equipments, building_weights)
    points_per_building = _allocate_by_weights(profile.points, building_weights)
    meters_per_building = _allocate_by_weights(profile.meters, building_weights)

    # =========================================================================
    # SITE (racine unique pour tout le campus)
    # =========================================================================

    site = Node(
        id=factory.new("site"),
        type=NodeType.SITE,
        name="Campus Principal",
        properties={"area_hectares": rng.randint(5, 50), "country": "FR", "building_id": 0}
    )
    nodes.append(site)

    # =========================================================================
    # GÉNÉRATION PAR BÂTIMENT
    # =========================================================================

    building_names = [
        "Bâtiment Principal", "Tour Nord", "Aile Est", "Pavillon Sud", "Annexe Ouest",
        "Centre Technique", "Bâtiment R&D", "Administration", "Services", "Logistique"
    ]

    for bld_idx in range(1, num_buildings + 1):
        ctx = _generate_building(
            factory=factory,
            rng=rng,
            site=site,
            building_id=bld_idx,
            building_name=building_names[bld_idx - 1] if bld_idx <= len(building_names) else f"Bâtiment {bld_idx}",
            num_floors=floors_per_building.get(bld_idx, 5),
            num_spaces=spaces_per_building.get(bld_idx, 50),
            num_equipments=equips_per_building.get(bld_idx, 100),
            num_points=points_per_building.get(bld_idx, 500),
            num_meters=meters_per_building.get(bld_idx, 20),
            nodes=nodes,
            edges=edges,
            measures=measures,
        )
        building_contexts.append(ctx)

    # =========================================================================
    # DOMAINES TRANSVERSAUX (partagés entre bâtiments)
    # =========================================================================

    all_spaces = [s for ctx in building_contexts for s in ctx.spaces]
    all_equipments = [e for ctx in building_contexts for e in ctx.equipments]
    all_points = [p for ctx in building_contexts for p in ctx.points]

    # IT/Datacenter (généralement centralisé)
    if profile.it_devices > 0:
        _generate_it_domain(
            factory, rng, building_contexts[0], profile.it_devices,
            nodes, edges, measures, all_points
        )

    # Parking (associé au site)
    if profile.parking_spots > 0:
        _generate_parking_domain(
            factory, rng, site, profile.parking_spots,
            nodes, edges, measures, all_points
        )

    # Sécurité (zones cross-buildings)
    if profile.security_devices > 0:
        _generate_security_domain(
            factory, rng, all_spaces, profile.security_devices,
            nodes, edges, measures, all_points
        )

    # Organisation
    if profile.persons > 0:
        _generate_organization_domain(
            factory, rng, all_spaces, profile.persons,
            nodes, edges
        )

    # Tenants et Contracts
    _generate_tenant_domain(factory, rng, all_spaces, nodes, edges)

    if profile.contracts > 0:
        _generate_contract_domain(
            factory, rng, all_equipments, profile.contracts,
            nodes, edges
        )

    # =========================================================================
    # GÉNÉRATION DES TIMESERIES
    # =========================================================================

    ts_points = [p for p in all_points if p.properties.get("quantity") in TIMESERIES_QUANTITIES]
    max_ts_points = int(len(all_points) * TIMESERIES_RATIO)
    if len(ts_points) > max_ts_points:
        ts_points = rng.sample(ts_points, max_ts_points)

    timeseries = _generate_timeseries(ts_points, measures, profile, rng)

    # =========================================================================
    # SUMMARY
    # =========================================================================

    node_types = defaultdict(int)
    for node in nodes:
        node_types[node.type.value] += 1

    relation_counts = defaultdict(int)
    for edge in edges:
        relation_counts[edge.rel.value] += 1

    max_depth = _compute_max_depth(nodes, edges)

    # Stats par bâtiment
    building_stats = {}
    for ctx in building_contexts:
        building_stats[ctx.building_id] = {
            "floors": len(ctx.floors),
            "spaces": len(ctx.spaces),
            "equipments": len(ctx.equipments),
            "points": len(ctx.points),
            "meters": len(ctx.meters),
        }

    summary = Summary(
        node_count=len(nodes),
        edge_count=len(edges),
        node_types=dict(node_types),
        relation_counts=dict(relation_counts),
        max_depth=max_depth,
        timeseries_points=len(ts_points),
        timeseries_samples=sum(len(ts.values) for ts in timeseries),
        buildings_count=num_buildings,
        building_stats=building_stats,
    )

    return Dataset(nodes=nodes, edges=edges, measures=measures, timeseries=timeseries), summary


def _get_num_buildings(profile: ScaleProfile) -> int:
    """Détermine le nombre de bâtiments selon le profil."""
    # Basé sur le nombre de points comme indicateur de taille
    if profile.points <= 60000:
        return 1  # small
    elif profile.points <= 150000:
        return 5  # medium
    else:
        return NUM_BUILDINGS_LARGE  # large


# =============================================================================
# Génération d'un bâtiment complet
# =============================================================================

def _generate_building(
    factory: IdFactory,
    rng: Random,
    site: Node,
    building_id: int,
    building_name: str,
    num_floors: int,
    num_spaces: int,
    num_equipments: int,
    num_points: int,
    num_meters: int,
    nodes: List[Node],
    edges: List[Edge],
    measures: List[MeasuresEdge],
) -> BuildingContext:
    """Génère un bâtiment complet avec tous ses domaines."""

    # Building
    building = _create_node(
        factory, "building", NodeType.BUILDING, building_name,
        {
            "total_area_sqm": rng.randint(5000, 50000),
            "construction_year": rng.randint(1990, 2023),
            "floors_count": num_floors,
            "certification": rng.choice(["HQE", "BREEAM", "LEED", "None"]),
        },
        building_id
    )
    nodes.append(building)
    edges.append(Edge(src=site.id, dst=building.id, rel=RelationType.CONTAINS))

    ctx = BuildingContext(building_id=building_id, building_node=building)

    # Floors
    for i in range(num_floors):
        floor = _create_node(
            factory, "floor", NodeType.FLOOR, f"Étage {i} - {building_name}",
            {"level": i, "area_sqm": rng.randint(500, 2000)},
            building_id
        )
        ctx.floors.append(floor)
        nodes.append(floor)
        edges.append(Edge(src=building.id, dst=floor.id, rel=RelationType.CONTAINS))

    # Adjacences entre étages
    for i in range(len(ctx.floors) - 1):
        edges.append(Edge(src=ctx.floors[i].id, dst=ctx.floors[i + 1].id, rel=RelationType.ADJACENT_TO))

    # Spaces
    space_types = ["office", "meeting_room", "corridor", "restroom", "storage", "technical", "lobby"]
    spaces_per_floor = _allocate_per_bucket(num_spaces, len(ctx.floors), rng)

    for floor, count in zip(ctx.floors, spaces_per_floor):
        floor_spaces = []
        for j in range(max(1, count)):
            space_type = rng.choice(space_types)
            space = _create_node(
                factory, "space", NodeType.SPACE,
                f"{space_type.title()} {floor.properties['level']}-{j + 1}",
                {
                    "usage": space_type,
                    "area_sqm": rng.randint(10, 200),
                    "capacity": rng.randint(1, 50) if space_type in ["office", "meeting_room"] else 0,
                },
                building_id
            )
            ctx.spaces.append(space)
            floor_spaces.append(space)
            nodes.append(space)
            edges.append(Edge(src=floor.id, dst=space.id, rel=RelationType.CONTAINS))

        # Adjacences entre espaces du même étage
        if len(floor_spaces) > 1:
            for _ in range(min(5, len(floor_spaces) // 2)):
                s1, s2 = rng.sample(floor_spaces, 2)
                edges.append(Edge(src=s1.id, dst=s2.id, rel=RelationType.ADJACENT_TO))

    # Zones
    zone_types = ["comfort_zone", "security_zone", "energy_zone", "open_space"]
    num_zones = max(1, len(ctx.spaces) // 10)
    for i in range(num_zones):
        zone = _create_node(
            factory, "zone", NodeType.ZONE,
            f"Zone {rng.choice(zone_types)} {building_id}-{i + 1}",
            {"zone_type": rng.choice(zone_types)},
            building_id
        )
        ctx.zones.append(zone)
        nodes.append(zone)
        zone_spaces = rng.sample(ctx.spaces, min(10, len(ctx.spaces)))
        for space in zone_spaces:
            edges.append(Edge(src=space.id, dst=zone.id, rel=RelationType.CONTAINS))

    # Systems
    system_types = ["HVAC", "Electrical", "Plumbing", "Fire_Safety", "Lighting", "BMS"]
    for sys_type in system_types:
        system = _create_node(
            factory, "system", NodeType.SYSTEM, f"Système {sys_type} - {building_name}",
            {"system_type": sys_type, "critical": sys_type in ["Fire_Safety", "Electrical"]},
            building_id
        )
        ctx.systems.append(system)
        nodes.append(system)
        edges.append(Edge(src=building.id, dst=system.id, rel=RelationType.HAS_SYSTEM))

    # Equipments
    equipment_types = ["AHU", "VAV", "Chiller", "Boiler", "Pump", "Fan", "Valve", "Damper", "Panel", "UPS"]
    manufacturers = ["Schneider Electric", "Siemens", "Honeywell", "Johnson Controls", "ABB", "Daikin", "Carrier"]

    equip_per_space = _allocate_per_bucket(num_equipments, len(ctx.spaces), rng)
    for space, count in zip(ctx.spaces, equip_per_space):
        for _ in range(max(1, count)):
            equip_type = rng.choice(equipment_types)
            equip = _create_node(
                factory, "equip", NodeType.EQUIPMENT,
                f"{equip_type}-{factory.count('equip')}",
                {
                    "equipment_type": equip_type,
                    "manufacturer": rng.choice(manufacturers),
                    "model": f"Model-{rng.randint(100, 999)}",
                    "installation_date": f"20{rng.randint(15, 23)}-{rng.randint(1, 12):02d}-01",
                    "nominal_power_kw": round(rng.uniform(0.5, 50), 1),
                    "efficiency": round(rng.uniform(0.7, 0.98), 2),
                },
                building_id
            )
            ctx.equipments.append(equip)
            nodes.append(equip)
            edges.append(Edge(src=equip.id, dst=space.id, rel=RelationType.LOCATED_IN))
            edges.append(Edge(src=equip.id, dst=space.id, rel=RelationType.SERVES))

            system = rng.choice(ctx.systems)
            edges.append(Edge(src=system.id, dst=equip.id, rel=RelationType.CONTAINS))

    # Hiérarchie fonctionnelle entre équipements
    if ctx.equipments:
        shuffled = list(ctx.equipments)
        rng.shuffle(shuffled)
        functional_layers: List[List[Node]] = []
        remaining = shuffled
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

    # Points de mesure
    quantity_weights = {q: 1.0 for q in POINT_QUANTITIES}
    quantity_weights.update({
        "temperature": 3.0, "power": 3.0, "status": 2.0, "co2": 1.5, "humidity": 1.5
    })

    points_per_equip = _allocate_per_bucket(num_points, len(ctx.equipments), rng) if ctx.equipments else []
    for equip, count in zip(ctx.equipments, points_per_equip):
        for i in range(max(1, min(10, count))):
            quantity = _sample_from_weights(quantity_weights, rng)
            point = _create_node(
                factory, "point", NodeType.POINT,
                f"Point {equip.id}-{quantity}-{i}",
                {"quantity": quantity, "unit": _get_unit(quantity)},
                building_id
            )
            ctx.points.append(point)
            nodes.append(point)
            edges.append(Edge(src=equip.id, dst=point.id, rel=RelationType.HAS_POINT))
            measures.append(MeasuresEdge(src=point.id, quantity=quantity))

            if quantity in {"command", "setpoint"} and rng.random() < 0.7:
                edges.append(Edge(src=point.id, dst=equip.id, rel=RelationType.CONTROLS))

    # Arbre de compteurs
    if num_meters > 0:
        root_meter = _create_node(
            factory, "meter", NodeType.METER,
            f"Compteur Principal - {building_name}",
            {"meter_type": "electricity", "is_root": True},
            building_id
        )
        ctx.meters.append(root_meter)
        nodes.append(root_meter)

        meter_tree: List[List[Node]] = [[root_meter]]
        remaining_meters = num_meters - 1

        depth = 0
        while remaining_meters > 0 and depth < 6:
            parents = meter_tree[depth]
            level: List[Node] = []
            for parent in parents:
                if remaining_meters <= 0:
                    break
                children_count = rng.randint(2, 4)
                for _ in range(children_count):
                    if remaining_meters <= 0:
                        break
                    meter = _create_node(
                        factory, "meter", NodeType.METER,
                        f"Sous-compteur {factory.count('meter')}",
                        {
                            "meter_type": rng.choice(["electricity", "water", "gas", "thermal"]),
                            "level": depth + 1,
                        },
                        building_id
                    )
                    ctx.meters.append(meter)
                    nodes.append(meter)
                    level.append(meter)
                    edges.append(Edge(src=parent.id, dst=meter.id, rel=RelationType.FEEDS))
                    remaining_meters -= 1
            if level:
                meter_tree.append(level)
                depth += 1
            else:
                break

        # Connecter compteurs feuilles aux équipements
        leaf_meters = meter_tree[-1] if meter_tree else ctx.meters
        for equip in ctx.equipments:
            meter = rng.choice(leaf_meters)
            edges.append(Edge(src=meter.id, dst=equip.id, rel=RelationType.FEEDS))

        # Points sur les compteurs
        for meter in ctx.meters:
            for qty in ["power", "energy", "voltage", "current"]:
                if rng.random() < 0.5:
                    point = _create_node(
                        factory, "point", NodeType.POINT,
                        f"Point {meter.id}-{qty}",
                        {"quantity": qty, "unit": _get_unit(qty)},
                        building_id
                    )
                    ctx.points.append(point)
                    nodes.append(point)
                    edges.append(Edge(src=meter.id, dst=point.id, rel=RelationType.HAS_POINT))
                    measures.append(MeasuresEdge(src=point.id, quantity=qty))

    # AV Systems (salles de réunion du bâtiment)
    meeting_rooms = [s for s in ctx.spaces if s.properties.get("usage") == "meeting_room"]
    if meeting_rooms:
        for i, room in enumerate(meeting_rooms[:min(10, len(meeting_rooms))]):
            av_system = _create_node(
                factory, "avsystem", NodeType.AV_SYSTEM,
                f"AV System {building_id}-{i + 1}",
                {"room_capacity": room.properties.get("capacity", 10)},
                building_id
            )
            nodes.append(av_system)
            edges.append(Edge(src=av_system.id, dst=room.id, rel=RelationType.LOCATED_IN))
            edges.append(Edge(src=av_system.id, dst=room.id, rel=RelationType.SERVES))

            display = _create_node(
                factory, "display", NodeType.DISPLAY,
                f"Display {factory.count('display')}",
                {"size_inches": rng.choice([55, 65, 75, 85]), "resolution": "4K"},
                building_id
            )
            nodes.append(display)
            edges.append(Edge(src=av_system.id, dst=display.id, rel=RelationType.HAS_PART))

            for qty in ["av_status", "display_status"]:
                point = _create_node(
                    factory, "point", NodeType.POINT,
                    f"Point {av_system.id}-{qty}",
                    {"quantity": qty, "unit": "enum"},
                    building_id
                )
                ctx.points.append(point)
                nodes.append(point)
                edges.append(Edge(src=av_system.id, dst=point.id, rel=RelationType.HAS_POINT))
                measures.append(MeasuresEdge(src=point.id, quantity=qty))

    return ctx


# =============================================================================
# Domaines transversaux
# =============================================================================

def _generate_it_domain(
    factory: IdFactory,
    rng: Random,
    main_building: BuildingContext,
    num_devices: int,
    nodes: List[Node],
    edges: List[Edge],
    measures: List[MeasuresEdge],
    all_points: List[Node],
) -> None:
    """Génère le domaine IT/Datacenter (centralisé)."""
    building_id = main_building.building_id
    technical_spaces = [s for s in main_building.spaces if s.properties.get("usage") == "technical"]
    dc_space = rng.choice(technical_spaces) if technical_spaces else rng.choice(main_building.spaces)

    datacenter = _create_node(
        factory, "datacenter", NodeType.DATACENTER, "Datacenter Principal",
        {"tier": rng.choice([2, 3, 4]), "pue_target": round(rng.uniform(1.2, 1.8), 2)},
        building_id
    )
    nodes.append(datacenter)
    edges.append(Edge(src=datacenter.id, dst=dc_space.id, rel=RelationType.LOCATED_IN))

    num_racks = max(1, num_devices // 20)
    racks: List[Node] = []
    for i in range(num_racks):
        rack = _create_node(
            factory, "rack", NodeType.RACK, f"Rack-{i + 1}",
            {"units": 42, "power_capacity_kw": rng.randint(5, 20)},
            building_id
        )
        racks.append(rack)
        nodes.append(rack)
        edges.append(Edge(src=datacenter.id, dst=rack.id, rel=RelationType.CONTAINS))

    device_allocation = _allocate_per_bucket(num_devices, 3, rng)
    num_servers, num_network, num_storage = device_allocation

    servers: List[Node] = []
    for i in range(num_servers):
        server = _create_node(
            factory, "server", NodeType.SERVER, f"Server-{i + 1}",
            {
                "cpu_cores": rng.choice([8, 16, 32, 64]),
                "ram_gb": rng.choice([32, 64, 128, 256]),
                "os": rng.choice(["Linux", "Windows Server", "VMware ESXi"]),
            },
            building_id
        )
        servers.append(server)
        nodes.append(server)
        rack = rng.choice(racks)
        edges.append(Edge(src=rack.id, dst=server.id, rel=RelationType.HOSTS))

        for qty in ["cpu_usage", "memory_usage", "disk_usage", "network_throughput"]:
            point = _create_node(
                factory, "point", NodeType.POINT, f"Point {server.id}-{qty}",
                {"quantity": qty, "unit": _get_unit(qty)},
                building_id
            )
            all_points.append(point)
            nodes.append(point)
            edges.append(Edge(src=server.id, dst=point.id, rel=RelationType.HAS_POINT))
            measures.append(MeasuresEdge(src=point.id, quantity=qty))

    network_devices: List[Node] = []
    for i in range(num_network):
        device = _create_node(
            factory, "netdev", NodeType.NETWORK_DEVICE, f"Switch-{i + 1}",
            {"device_type": rng.choice(["switch", "router", "firewall"]), "ports": rng.choice([24, 48, 96])},
            building_id
        )
        network_devices.append(device)
        nodes.append(device)
        rack = rng.choice(racks)
        edges.append(Edge(src=rack.id, dst=device.id, rel=RelationType.HOSTS))

    for i in range(num_storage):
        storage = _create_node(
            factory, "storage", NodeType.STORAGE, f"Storage-{i + 1}",
            {"capacity_tb": rng.choice([10, 50, 100, 500]), "type": rng.choice(["SAN", "NAS", "Object"])},
            building_id
        )
        nodes.append(storage)
        rack = rng.choice(racks)
        edges.append(Edge(src=rack.id, dst=storage.id, rel=RelationType.HOSTS))

    for server in servers:
        if network_devices:
            switch = rng.choice(network_devices)
            edges.append(Edge(src=switch.id, dst=server.id, rel=RelationType.NETWORK_LINK))


def _generate_parking_domain(
    factory: IdFactory,
    rng: Random,
    site: Node,
    num_spots: int,
    nodes: List[Node],
    edges: List[Edge],
    measures: List[MeasuresEdge],
    all_points: List[Node],
) -> None:
    """Génère le domaine parking (associé au site)."""
    parking_zone = _create_node(
        factory, "parkzone", NodeType.PARKING_ZONE, "Parking Principal",
        {"type": rng.choice(["underground", "surface", "multi-level"])},
        0  # Site level
    )
    nodes.append(parking_zone)
    edges.append(Edge(src=site.id, dst=parking_zone.id, rel=RelationType.CONTAINS))

    num_levels = max(1, num_spots // 100)
    parking_levels: List[Node] = []
    for i in range(num_levels):
        level = _create_node(
            factory, "parklevel", NodeType.PARKING_LEVEL,
            f"Niveau Parking {i - num_levels // 2}",
            {"level": i - num_levels // 2},
            0
        )
        parking_levels.append(level)
        nodes.append(level)
        edges.append(Edge(src=parking_zone.id, dst=level.id, rel=RelationType.CONTAINS))

    spots_per_level = _allocate_per_bucket(num_spots, len(parking_levels), rng)
    parking_spots: List[Node] = []
    for level, count in zip(parking_levels, spots_per_level):
        for j in range(count):
            spot = _create_node(
                factory, "parkspot", NodeType.PARKING_SPOT,
                f"Place {level.properties['level']}-{j + 1}",
                {
                    "spot_type": rng.choice(["standard", "handicap", "ev_charging", "reserved"]),
                    "covered": rng.random() < 0.7,
                },
                0
            )
            parking_spots.append(spot)
            nodes.append(spot)
            edges.append(Edge(src=level.id, dst=spot.id, rel=RelationType.CONTAINS))

    # Bornes de recharge
    ev_spots = [s for s in parking_spots if s.properties.get("spot_type") == "ev_charging"]
    for spot in ev_spots[:len(ev_spots) // 2]:
        station = _create_node(
            factory, "charger", NodeType.CHARGING_STATION,
            f"Borne {factory.count('charger')}",
            {"power_kw": rng.choice([7, 11, 22, 50, 150]), "connector": rng.choice(["Type2", "CCS", "CHAdeMO"])},
            0
        )
        nodes.append(station)
        edges.append(Edge(src=station.id, dst=spot.id, rel=RelationType.LOCATED_IN))

        for qty in ["charging_power", "battery_level"]:
            point = _create_node(
                factory, "point", NodeType.POINT, f"Point {station.id}-{qty}",
                {"quantity": qty, "unit": _get_unit(qty)},
                0
            )
            all_points.append(point)
            nodes.append(point)
            edges.append(Edge(src=station.id, dst=point.id, rel=RelationType.HAS_POINT))
            measures.append(MeasuresEdge(src=point.id, quantity=qty))


def _generate_security_domain(
    factory: IdFactory,
    rng: Random,
    all_spaces: List[Node],
    num_devices: int,
    nodes: List[Node],
    edges: List[Edge],
    measures: List[MeasuresEdge],
    all_points: List[Node],
) -> None:
    """Génère le domaine sécurité (cross-buildings)."""
    num_zones = max(1, num_devices // 10)
    security_zones: List[Node] = []
    for i in range(num_zones):
        sec_zone = _create_node(
            factory, "seczone", NodeType.SECURITY_ZONE,
            f"Zone Sécurité {i + 1}",
            {"security_level": rng.choice(["low", "medium", "high", "restricted"])},
            0  # Cross-building
        )
        security_zones.append(sec_zone)
        nodes.append(sec_zone)

    device_alloc = _allocate_per_bucket(num_devices, 3, rng)
    num_access, num_cameras, num_alarms = device_alloc

    for i in range(num_access):
        space = rng.choice(all_spaces)
        building_id = space.properties.get("building_id", 0)
        access = _create_node(
            factory, "access", NodeType.ACCESS_POINT, f"Lecteur Badge {i + 1}",
            {"access_type": rng.choice(["badge", "biometric", "pin", "badge+pin"])},
            building_id
        )
        nodes.append(access)
        edges.append(Edge(src=access.id, dst=space.id, rel=RelationType.LOCATED_IN))
        edges.append(Edge(src=access.id, dst=space.id, rel=RelationType.SECURES))
        sec_zone = rng.choice(security_zones)
        edges.append(Edge(src=sec_zone.id, dst=access.id, rel=RelationType.CONTAINS))

        point = _create_node(
            factory, "point", NodeType.POINT, f"Point {access.id}-access_event",
            {"quantity": "access_event", "unit": "event"},
            building_id
        )
        all_points.append(point)
        nodes.append(point)
        edges.append(Edge(src=access.id, dst=point.id, rel=RelationType.HAS_POINT))
        measures.append(MeasuresEdge(src=point.id, quantity="access_event"))

    for i in range(num_cameras):
        space = rng.choice(all_spaces)
        building_id = space.properties.get("building_id", 0)
        camera = _create_node(
            factory, "camera", NodeType.CAMERA, f"Caméra {i + 1}",
            {"resolution": rng.choice(["1080p", "4K"]), "ptz": rng.random() < 0.3},
            building_id
        )
        nodes.append(camera)
        edges.append(Edge(src=camera.id, dst=space.id, rel=RelationType.LOCATED_IN))
        edges.append(Edge(src=camera.id, dst=space.id, rel=RelationType.MONITORS))
        sec_zone = rng.choice(security_zones)
        edges.append(Edge(src=sec_zone.id, dst=camera.id, rel=RelationType.CONTAINS))


def _generate_organization_domain(
    factory: IdFactory,
    rng: Random,
    all_spaces: List[Node],
    num_persons: int,
    nodes: List[Node],
    edges: List[Edge],
) -> None:
    """Génère le domaine organisation."""
    organization = _create_node(
        factory, "org", NodeType.ORGANIZATION, "Entreprise ABC",
        {"sector": rng.choice(["tech", "finance", "healthcare", "manufacturing"])},
        0
    )
    nodes.append(organization)

    dept_names = ["IT", "HR", "Finance", "Operations", "Sales", "R&D", "Legal", "Marketing"]
    departments: List[Node] = []
    for dept_name in dept_names[:max(2, num_persons // 100)]:
        dept = _create_node(
            factory, "dept", NodeType.DEPARTMENT, f"Département {dept_name}",
            {"code": dept_name[:3].upper()},
            0
        )
        departments.append(dept)
        nodes.append(dept)
        edges.append(Edge(src=organization.id, dst=dept.id, rel=RelationType.CONTAINS))

    teams: List[Node] = []
    for dept in departments:
        num_teams = rng.randint(2, 5)
        for t in range(num_teams):
            team = _create_node(
                factory, "team", NodeType.TEAM, f"Équipe {dept.properties['code']}-{t + 1}",
                {},
                0
            )
            teams.append(team)
            nodes.append(team)
            edges.append(Edge(src=dept.id, dst=team.id, rel=RelationType.CONTAINS))

    first_names = ["Alice", "Bob", "Claire", "David", "Emma", "François", "Gina", "Hugo", "Iris", "Jean"]
    last_names = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau"]

    for i in range(num_persons):
        person = _create_node(
            factory, "person", NodeType.PERSON,
            f"{rng.choice(first_names)} {rng.choice(last_names)}",
            {
                "email": f"person{i + 1}@company.com",
                "role": rng.choice(["employee", "manager", "director", "intern"]),
            },
            0
        )
        nodes.append(person)
        team = rng.choice(teams)
        edges.append(Edge(src=person.id, dst=team.id, rel=RelationType.BELONGS_TO))

        if all_spaces and rng.random() < 0.8:
            work_space = rng.choice(all_spaces)
            edges.append(Edge(src=person.id, dst=work_space.id, rel=RelationType.WORKS_IN))


def _generate_tenant_domain(
    factory: IdFactory,
    rng: Random,
    all_spaces: List[Node],
    nodes: List[Node],
    edges: List[Edge],
) -> None:
    """Génère le domaine locataires."""
    num_tenants = max(1, len(all_spaces) // 50)
    for i in range(num_tenants):
        tenant = _create_node(
            factory, "tenant", NodeType.TENANT, f"Locataire {i + 1}",
            {"sector": rng.choice(["tech", "finance", "consulting", "legal"])},
            0
        )
        nodes.append(tenant)
        tenant_spaces = rng.sample(all_spaces, min(rng.randint(5, 20), len(all_spaces)))
        for space in tenant_spaces:
            edges.append(Edge(src=tenant.id, dst=space.id, rel=RelationType.OCCUPIES))


def _generate_contract_domain(
    factory: IdFactory,
    rng: Random,
    all_equipments: List[Node],
    num_contracts: int,
    nodes: List[Node],
    edges: List[Edge],
) -> None:
    """Génère le domaine contractuel."""
    provider_names = ["EDF", "Engie", "Veolia", "Dalkia", "Cofely", "Spie", "Vinci Facilities"]
    providers: List[Node] = []
    for name in provider_names[:min(len(provider_names), num_contracts // 5 + 1)]:
        provider = _create_node(
            factory, "provider", NodeType.PROVIDER, name,
            {"type": rng.choice(["energy", "maintenance", "cleaning", "security"])},
            0
        )
        providers.append(provider)
        nodes.append(provider)

    contract_types = ["maintenance", "energy_supply", "cleaning", "security", "it_support"]
    for i in range(num_contracts):
        contract = _create_node(
            factory, "contract", NodeType.CONTRACT,
            f"Contrat {contract_types[i % len(contract_types)].title()} {i + 1}",
            {
                "contract_type": contract_types[i % len(contract_types)],
                "start_date": f"20{rng.randint(20, 23)}-01-01",
                "end_date": f"20{rng.randint(24, 28)}-12-31",
                "annual_value": rng.randint(10000, 500000),
            },
            0
        )
        nodes.append(contract)

        provider = rng.choice(providers)
        edges.append(Edge(src=contract.id, dst=provider.id, rel=RelationType.PROVIDED_BY))

        if all_equipments:
            covered_equips = rng.sample(all_equipments, min(rng.randint(10, 50), len(all_equipments)))
            for equip in covered_equips:
                edges.append(Edge(src=equip.id, dst=contract.id, rel=RelationType.COVERED_BY))


# =============================================================================
# Fonctions auxiliaires
# =============================================================================

def _get_unit(quantity: str) -> str:
    """Retourne l'unité pour une quantité."""
    units = {
        "temperature": "°C", "humidity": "%", "co2": "ppm", "pressure": "Pa",
        "power": "kW", "energy": "kWh", "voltage": "V", "current": "A",
        "flow": "m³/h", "illuminance": "lux", "noise_level": "dB",
        "cpu_usage": "%", "memory_usage": "%", "disk_usage": "%",
        "network_throughput": "Mbps", "network_latency": "ms",
        "charging_power": "kW", "battery_level": "%",
        "people_count": "count", "air_quality": "AQI",
    }
    return units.get(quantity, "unit")


def _compute_max_depth(nodes: List[Node], edges: List[Edge]) -> int:
    """Calcule la profondeur maximale du graphe."""
    adjacency: Dict[str, List[str]] = defaultdict(list)
    for edge in edges:
        adjacency[edge.src].append(edge.dst)

    max_depth = 0
    visited = set()

    def dfs(node_id: str, depth: int) -> int:
        if depth > 15 or node_id in visited:
            return depth
        visited.add(node_id)
        max_d = depth
        for neighbor in adjacency.get(node_id, []):
            max_d = max(max_d, dfs(neighbor, depth + 1))
        visited.discard(node_id)
        return max_d

    for node in nodes[:100]:
        max_depth = max(max_depth, dfs(node.id, 0))

    return max_depth


def _generate_timeseries(
    points: List[Node],
    measures: List[MeasuresEdge],
    profile: ScaleProfile,
    rng: Random
) -> List[TimeseriesChunk]:
    """Génère les séries temporelles pour les points sélectionnés.

    Seuls les points avec des mesures continues (fréquence > 0) génèrent
    des timeseries. Les événements rares (alarmes, états, accès) n'ont pas
    de timeseries régulières.
    """
    timeseries: List[TimeseriesChunk] = []

    start_time = int((datetime.now() - timedelta(days=profile.duration_days)).timestamp())
    end_time = int(datetime.now().timestamp())

    point_quantities = {m.src: m.quantity for m in measures}

    for point in points:
        quantity = point_quantities.get(point.id, point.properties.get("quantity"))
        if not quantity:
            continue

        frequency_minutes = _get_sampling_frequency(quantity)

        # Skip event-based quantities (frequency = 0)
        if frequency_minutes == 0:
            continue

        values = _generate_values(quantity, profile.duration_days, frequency_minutes, rng)

        chunk = TimeseriesChunk(
            point_id=point.id,
            start_time=start_time,
            end_time=end_time,
            frequency_seconds=frequency_minutes * 60,
            values=values
        )
        timeseries.append(chunk)

    return timeseries


def _get_sampling_frequency(quantity: str) -> int:
    """Fréquence d'échantillonnage en minutes selon le type de quantité.

    Classification réaliste smart building:
    - Mesures continues (15min): température, CO2, humidité, puissance
    - Compteurs énergie (60min): kWh, m³
    - Mesures IT rapides (5min): CPU, RAM, réseau
    - Événements rares: retourne 0 (pas de timeseries régulières)
    """
    # Mesures continues - 15 min (96 samples/jour)
    continuous_15min = {
        "temperature", "humidity", "co2", "air_quality",
        "power", "flow", "people_count", "charging_power",
    }

    # Mesures moyennes - 30 min (48 samples/jour)
    continuous_30min = {
        "pressure", "illuminance", "voltage", "current",
    }

    # Compteurs énergie - 60 min (24 samples/jour)
    hourly = {
        "energy", "water_consumption", "gas_consumption", "thermal_energy",
    }

    # IT/SCADA rapide - 5 min (288 samples/jour)
    fast_5min = {
        "cpu_usage", "memory_usage", "network_throughput", "network_latency",
    }

    # IT lent - 60 min
    slow_hourly = {
        "disk_usage", "noise_level",
    }

    # Événements rares - PAS de timeseries continues
    # Ces quantités génèrent des événements discrets, pas des séries régulières
    event_based = {
        "status", "command", "setpoint", "mode", "alarm_state",
        "occupancy", "presence", "workspace_status", "space_reservation_status",
        "access_event", "intrusion_status", "camera_status", "ssi_status",
        "spot_status", "av_status", "display_status", "asset_status",
        "maintenance_due", "battery_level", "runtime_hours", "audio_level",
        "power_factor", "frequency",
    }

    if quantity in continuous_15min:
        return 15
    elif quantity in continuous_30min:
        return 30
    elif quantity in hourly:
        return 60
    elif quantity in fast_5min:
        return 5
    elif quantity in slow_hourly:
        return 60
    elif quantity in event_based:
        return 0  # Pas de timeseries régulières
    else:
        return 60  # Défaut: horaire


def _generate_values(quantity: str, duration_days: int, freq_minutes: int, rng: Random) -> List[float]:
    """Génère des valeurs réalistes pour une quantité."""
    total_points = (duration_days * 24 * 60) // freq_minutes

    if quantity == "temperature":
        base = 21.0
        return [round(base + 3 * math.sin(2 * math.pi * i / 96) + rng.gauss(0, 0.5), 1)
                for i in range(total_points)]

    elif quantity == "power":
        base = 500.0
        return [max(0, round(base * (0.3 + 0.7 * math.sin(math.pi * (i % 96) / 96) ** 2) + rng.gauss(0, 50), 0))
                for i in range(total_points)]

    elif quantity == "co2":
        values = []
        current = 400.0
        for i in range(total_points):
            hour = (i * freq_minutes / 60) % 24
            if 8 <= hour <= 18:
                current += rng.gauss(5, 2)
                current -= 0.1 * (current - 400)
            else:
                current -= 0.2 * (current - 400)
            current = max(350, min(2000, current))
            values.append(round(current, 0))
        return values

    elif quantity in ["cpu_usage", "memory_usage", "disk_usage"]:
        base = 30 if quantity != "disk_usage" else 60
        return [max(0, min(100, round(base + rng.gauss(0, 15), 1))) for _ in range(total_points)]

    elif quantity == "network_throughput":
        return [max(0, round(100 + rng.gauss(0, 30), 1)) for _ in range(total_points)]

    elif quantity == "humidity":
        return [max(20, min(80, round(50 + rng.gauss(0, 10), 1))) for _ in range(total_points)]

    elif quantity == "charging_power":
        return [rng.choice([0, 0, 0, 7, 11, 22]) for _ in range(total_points)]

    elif quantity == "people_count":
        values = []
        for i in range(total_points):
            hour = (i * freq_minutes / 60) % 24
            if 8 <= hour <= 18:
                values.append(max(0, int(rng.gauss(10, 5))))
            else:
                values.append(max(0, int(rng.gauss(1, 1))))
        return values

    else:
        return [round(rng.gauss(100, 10), 1) for _ in range(total_points)]


# =============================================================================
# Extraction par scale et duration
# =============================================================================

def extract_subset(
    dataset: Dataset,
    scale: str = "large",
    duration_days: Optional[int] = None,
) -> Dataset:
    """Extrait un sous-ensemble du dataset par scale et durée.

    Args:
        dataset: Dataset complet
        scale: "small" (building 1), "medium" (1-5), "large" (tous)
        duration_days: Nombre de jours à garder (None = tout)

    Returns:
        Dataset filtré
    """
    building_ids = SCALE_BUILDINGS.get(scale)

    # Filtrer les nodes
    if building_ids is None:
        filtered_nodes = dataset.nodes
    else:
        filtered_nodes = [
            n for n in dataset.nodes
            if n.properties.get("building_id", 0) in building_ids or n.properties.get("building_id", 0) == 0
        ]

    valid_ids = {n.id for n in filtered_nodes}

    # Filtrer les edges
    filtered_edges = [
        e for e in dataset.edges
        if e.src in valid_ids and e.dst in valid_ids
    ]

    # Filtrer les measures
    filtered_measures = [
        m for m in dataset.measures
        if m.src in valid_ids
    ]

    # Filtrer les timeseries
    filtered_ts = [
        ts for ts in dataset.timeseries
        if ts.point_id in valid_ids
    ]

    # Filtrer par durée si spécifié
    if duration_days is not None:
        cutoff_time = int((datetime.now() - timedelta(days=duration_days)).timestamp())
        new_ts = []
        for ts in filtered_ts:
            if ts.end_time >= cutoff_time:
                # Calculer combien de valeurs garder
                total_seconds = ts.end_time - ts.start_time
                keep_seconds = min(duration_days * 86400, total_seconds)
                keep_values = int(keep_seconds / ts.frequency_seconds)
                new_ts.append(TimeseriesChunk(
                    point_id=ts.point_id,
                    start_time=ts.end_time - keep_seconds,
                    end_time=ts.end_time,
                    frequency_seconds=ts.frequency_seconds,
                    values=ts.values[-keep_values:] if keep_values < len(ts.values) else ts.values,
                ))
        filtered_ts = new_ts

    return Dataset(
        nodes=filtered_nodes,
        edges=filtered_edges,
        measures=filtered_measures,
        timeseries=filtered_ts,
    )


# =============================================================================
# Génération streaming (pour gros datasets)
# =============================================================================

def generate_graph_only(profile: ScaleProfile, seed: int) -> Tuple[Dict, Summary, List[Tuple[Node, str]]]:
    """Génère uniquement la structure du graphe sans les timeseries.

    Utilisé pour le mode streaming où les timeseries sont générées par chunks
    séparément pour éviter l'explosion mémoire.

    Args:
        profile: Profil de volumétrie
        seed: Graine pour reproductibilité

    Returns:
        Tuple (graph_data dict, summary, list of (point_node, quantity) for timeseries)
    """
    rng = Random(seed)
    factory = IdFactory()

    nodes: List[Node] = []
    edges: List[Edge] = []
    measures: List[MeasuresEdge] = []
    building_contexts: List[BuildingContext] = []

    # Déterminer le nombre de bâtiments
    num_buildings = _get_num_buildings(profile)

    # Calculer la répartition des ressources par bâtiment
    building_weights = {i: BUILDING_WEIGHTS.get(i, 0.05) for i in range(1, num_buildings + 1)}

    floors_per_building = _allocate_by_weights(profile.floors, building_weights)
    spaces_per_building = _allocate_by_weights(profile.spaces, building_weights)
    equips_per_building = _allocate_by_weights(profile.equipments, building_weights)
    points_per_building = _allocate_by_weights(profile.points, building_weights)
    meters_per_building = _allocate_by_weights(profile.meters, building_weights)

    # SITE (racine unique pour tout le campus)
    site = Node(
        id=factory.new("site"),
        type=NodeType.SITE,
        name="Campus Principal",
        properties={"area_hectares": rng.randint(5, 50), "country": "FR", "building_id": 0}
    )
    nodes.append(site)

    # GÉNÉRATION PAR BÂTIMENT
    building_names = [
        "Bâtiment Principal", "Tour Nord", "Aile Est", "Pavillon Sud", "Annexe Ouest",
        "Centre Technique", "Bâtiment R&D", "Administration", "Services", "Logistique"
    ]

    for bld_idx in range(1, num_buildings + 1):
        ctx = _generate_building(
            factory=factory,
            rng=rng,
            site=site,
            building_id=bld_idx,
            building_name=building_names[bld_idx - 1] if bld_idx <= len(building_names) else f"Bâtiment {bld_idx}",
            num_floors=floors_per_building.get(bld_idx, 5),
            num_spaces=spaces_per_building.get(bld_idx, 50),
            num_equipments=equips_per_building.get(bld_idx, 100),
            num_points=points_per_building.get(bld_idx, 500),
            num_meters=meters_per_building.get(bld_idx, 20),
            nodes=nodes,
            edges=edges,
            measures=measures,
        )
        building_contexts.append(ctx)

    # DOMAINES TRANSVERSAUX
    all_spaces = [s for ctx in building_contexts for s in ctx.spaces]
    all_equipments = [e for ctx in building_contexts for e in ctx.equipments]
    all_points = [p for ctx in building_contexts for p in ctx.points]

    if profile.it_devices > 0:
        _generate_it_domain(
            factory, rng, building_contexts[0], profile.it_devices,
            nodes, edges, measures, all_points
        )

    if profile.parking_spots > 0:
        _generate_parking_domain(
            factory, rng, site, profile.parking_spots,
            nodes, edges, measures, all_points
        )

    if profile.security_devices > 0:
        _generate_security_domain(
            factory, rng, all_spaces, profile.security_devices,
            nodes, edges, measures, all_points
        )

    if profile.persons > 0:
        _generate_organization_domain(
            factory, rng, all_spaces, profile.persons,
            nodes, edges
        )

    _generate_tenant_domain(factory, rng, all_spaces, nodes, edges)

    if profile.contracts > 0:
        _generate_contract_domain(
            factory, rng, all_equipments, profile.contracts,
            nodes, edges
        )

    # Préparer la liste des points pour timeseries
    ts_points = [p for p in all_points if p.properties.get("quantity") in TIMESERIES_QUANTITIES]
    max_ts_points = int(len(all_points) * TIMESERIES_RATIO)
    if len(ts_points) > max_ts_points:
        ts_points = rng.sample(ts_points, max_ts_points)

    # Associer chaque point à sa quantité
    point_quantities = {m.src: m.quantity for m in measures}
    ts_point_info = [
        (point, point_quantities.get(point.id, point.properties.get("quantity")))
        for point in ts_points
    ]

    # SUMMARY
    node_types = defaultdict(int)
    for node in nodes:
        node_types[node.type.value] += 1

    relation_counts = defaultdict(int)
    for edge in edges:
        relation_counts[edge.rel.value] += 1

    max_depth = _compute_max_depth(nodes, edges)

    building_stats = {}
    for ctx in building_contexts:
        building_stats[ctx.building_id] = {
            "floors": len(ctx.floors),
            "spaces": len(ctx.spaces),
            "equipments": len(ctx.equipments),
            "points": len(ctx.points),
            "meters": len(ctx.meters),
        }

    summary = Summary(
        node_count=len(nodes),
        edge_count=len(edges),
        node_types=dict(node_types),
        relation_counts=dict(relation_counts),
        max_depth=max_depth,
        timeseries_points=len(ts_points),
        timeseries_samples=0,  # Sera calculé après génération streaming
        buildings_count=num_buildings,
        building_stats=building_stats,
    )

    graph_data = {
        'nodes': nodes,
        'edges': edges,
        'measures': measures,
    }

    return graph_data, summary, ts_point_info


def generate_timeseries_streaming(
    point_info: List[Tuple[Node, str]],
    profile: ScaleProfile,
    seed: int
) -> List[TimeseriesChunk]:
    """Génère les timeseries pour un sous-ensemble de points.

    Utilisé pour le mode streaming où on génère les timeseries par chunks.

    Args:
        point_info: Liste de tuples (point_node, quantity)
        profile: Profil de volumétrie (pour duration_days)
        seed: Graine pour reproductibilité

    Returns:
        Liste de TimeseriesChunk pour les points fournis
    """
    rng = Random(seed)
    timeseries: List[TimeseriesChunk] = []

    start_time = int((datetime.now() - timedelta(days=profile.duration_days)).timestamp())
    end_time = int(datetime.now().timestamp())

    for point, quantity in point_info:
        if not quantity:
            continue

        frequency_minutes = _get_sampling_frequency(quantity)
        values = _generate_values(quantity, profile.duration_days, frequency_minutes, rng)

        chunk = TimeseriesChunk(
            point_id=point.id,
            start_time=start_time,
            end_time=end_time,
            frequency_seconds=frequency_minutes * 60,
            values=values
        )
        timeseries.append(chunk)

    return timeseries
