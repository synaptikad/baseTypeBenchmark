"""Generator v2.0 - Smart building dataset generator.

Generates realistic building datasets for database benchmarking.
Based on docs/generator_v2 specifications.

Supports two timeseries generation modes:
- Legacy: Independent Gaussian samples at fixed intervals
- Simulation: Physical simulation with deadband filtering (~7x data reduction)
"""

import json
import random
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple, Any, Callable

import yaml

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    tqdm = None

from .equipment_loader import EquipmentDef, load_exploration, get_equipment_by_type
from .simulation import SimulationEngine, SimulationConfig, PointInfo


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Node:
    """A node in the dataset graph."""
    id: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """An edge (relationship) in the dataset graph."""
    src_id: str
    dst_id: str
    rel_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Point:
    """A point (sensor/actuator) definition."""
    id: str
    name: str
    equipment_id: str
    unit: str
    range_min: float
    range_max: float
    frequency: int  # seconds (0 = event-driven)
    point_type: str  # mesure, commande, etat, alarme


@dataclass
class TSChunk:
    """Timeseries chunk for M1/O1 formats.

    Uses explicit timestamps (not start_ts + idx*freq_sec) to support
    irregular intervals from deadband filtering.
    """
    point_id: str
    chunk_idx: int
    timestamps: List[int]  # Unix timestamps (explicit, for deadband support)
    values: List[float]


@dataclass
class Dataset:
    """Complete generated dataset."""
    nodes: List[Node]
    edges: List[Edge]
    points: List[Point]
    profile: str
    seed: int


# =============================================================================
# CONFIGURATION
# =============================================================================

# Point configuration by type
POINT_CONFIG = {
    "alarm": {"mode": "event", "events_per_day": 0.5},
    "fault": {"mode": "event", "events_per_day": 0.2},
    "status": {"mode": "event", "events_per_day": 2},
    "energy": {"mode": "regular", "frequency": 900},
    "meter": {"mode": "regular", "frequency": 900},
    "temperature": {"mode": "regular", "frequency": 300},
    "temp": {"mode": "regular", "frequency": 300},
    "co2": {"mode": "regular", "frequency": 300},
    "humidity": {"mode": "regular", "frequency": 300},
    "power": {"mode": "regular", "frequency": 300},
    "pressure": {"mode": "regular", "frequency": 1800},
    "illuminance": {"mode": "regular", "frequency": 1800},
    "flow": {"mode": "regular", "frequency": 1800},
    "setpoint": {"mode": "event", "events_per_day": 3},
    "command": {"mode": "event", "events_per_day": 5},
    "mode": {"mode": "event", "events_per_day": 2},
    "count": {"mode": "regular", "frequency": 300},  # PeopleCounter
    "position": {"mode": "regular", "frequency": 60},  # Damper, valve positions
}

# FEEDS rules: source type -> target types
FEEDS_RULES = {
    "TGBT": ["ElectricalPanel", "UPS"],
    "ElectricalPanel": ["LED_Luminaire", "FCU", "AHU"],
    "UPS": ["RackServer", "NetworkSwitch"],
    "Chiller": ["AHU", "FCU"],
    "Boiler": ["AHU"],
    "AHU": ["VAV", "FCU"],
    "MainMeter": ["SubMeter"],
    "SubMeter": [],  # Will be linked to equipment
}

# SERVES rules by equipment scope
SERVES_RULES = {
    "AHU": {"scope": "building", "ratio": 0.3},
    "Chiller": {"scope": "building", "ratio": 0.5},
    "Boiler": {"scope": "building", "ratio": 0.5},
    "FCU": {"scope": "floor", "ratio": 0.2},
    "VAV": {"scope": "floor", "ratio": 0.15},
    # Default: scope=space, ratio=1.0
}

# HAS_PART rules
HAS_PART_RULES = {
    "AHU": ["Fan", "Filter", "Coil", "Damper"],
    "Chiller": ["Compressor", "Condenser", "Evaporator"],
    "TGBT": ["Breaker", "Busbar"],
    "UPS": ["Battery", "Inverter"],
}

# CONTROLS rules: controller type -> controlled equipment types
# Represents BMS control relationships (Brick: controls)
CONTROLS_RULES = {
    "Thermostat": ["FCU", "VAV", "AHU"],
    "Dimmer": ["LED_Luminaire"],
    "VFD": ["Pump", "Fan"],
    "FireAlarmPanel": ["SmokeDetector", "ManualCallPoint", "Emergency_Lighting"],
}

# MONITORS rules: sensor type -> monitored equipment types
# Represents sensor monitoring relationships (inverse of hasPoint conceptually)
MONITORS_RULES = {
    "TemperatureSensor": ["FCU", "AHU", "Chiller"],
    "CO2_Sensor": ["AHU", "VAV"],
    "PressureSensor": ["AHU", "Pump"],
    "FlowSensor": ["Pump", "Chiller"],
    "CO_Sensor": ["ExhaustFan"],
}

# IS_METERED_BY rules: equipment types that are metered
# Represents metering relationships (Haystack: submeterOf)
METERED_EQUIPMENT = [
    "ElectricalPanel", "TGBT", "UPS", "AHU", "Chiller", "Boiler",
    "LED_Luminaire", "FCU", "CRAC", "PassengerElevator",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_yaml_config(path: Path) -> dict:
    """Load a YAML configuration file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_point_config(point_name: str) -> dict:
    """Get point configuration based on name pattern matching."""
    name_lower = point_name.lower()
    for key, config in POINT_CONFIG.items():
        if key in name_lower:
            return config
    return {"mode": "regular", "frequency": 300}  # Default: 5 min


def generate_id(prefix: str, *parts) -> str:
    """Generate a unique ID from parts."""
    return f"{prefix}_" + "_".join(str(p) for p in parts)


# =============================================================================
# MAIN GENERATOR CLASS
# =============================================================================

class DatasetGeneratorV2:
    """Main dataset generator implementing v2.0 specification."""

    def __init__(
        self,
        profile_name: str,
        config_path: Path,
        exploration_path: Optional[Path] = None,
        seed: int = 42
    ):
        """Initialize the generator.

        Args:
            profile_name: Profile to use (small, medium, large)
            config_path: Path to config/ directory
            exploration_path: Path to docs/Exploration/ (optional)
            seed: Random seed for reproducibility
        """
        self.profile_name = profile_name
        self.config_path = Path(config_path)
        self.exploration_path = Path(exploration_path) if exploration_path else None
        self.seed = seed
        self.rng = random.Random(seed)

        # Load configurations
        self.profile = load_yaml_config(self.config_path / "profiles" / f"{profile_name}.yaml")
        self.space_types = load_yaml_config(self.config_path / "space_types.yaml")
        self.distribution = load_yaml_config(self.config_path / "equipment_distribution.yaml")

        # Load equipment definitions from Exploration
        self.equipment_defs: Dict[str, EquipmentDef] = {}
        if self.exploration_path and self.exploration_path.exists():
            self.equipment_defs = load_exploration(self.exploration_path)

        # Generated data
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.points: List[Point] = []

        # Index structures
        self.equipments_by_type: Dict[str, List[Node]] = defaultdict(list)
        self.equipments_by_building: Dict[str, List[Node]] = defaultdict(list)
        self.spaces_by_floor: Dict[str, List[Node]] = defaultdict(list)
        self.spaces_by_building: Dict[str, List[Node]] = defaultdict(list)

    def generate(self) -> Dataset:
        """Generate the complete dataset.

        Returns:
            Dataset with nodes, edges, and points
        """
        # 1. Create spatial structure
        self._create_spatial_structure()

        # 2. Create meters
        self._create_meters()

        # 3. Distribute equipment
        self._distribute_equipment()

        # 4. Create relations
        self._create_feeds_relations()
        self._create_serves_relations()
        self._create_has_part_relations()
        self._create_controls_relations()
        self._create_monitors_relations()
        self._create_is_metered_by_relations()
        self._create_tenants()

        return Dataset(
            nodes=self.nodes,
            edges=self.edges,
            points=self.points,
            profile=self.profile_name,
            seed=self.seed
        )

    def _create_spatial_structure(self) -> None:
        """Create Site -> Building -> Floor -> Space hierarchy."""
        # Site
        site = Node("site_1", "Site", {"name": "Campus"})
        self.nodes.append(site)

        for b in range(self.profile["buildings"]):
            building_id = f"building_{b+1}"
            building = Node(
                building_id, "Building",
                {"name": f"Building {b+1}", "site_id": site.id}
            )
            self.nodes.append(building)
            self.edges.append(Edge(site.id, building.id, "CONTAINS"))

            floor_idx = 0
            for floor_spec in self.profile["floors"]:
                floor_type = floor_spec["type"]
                for _ in range(floor_spec["count"]):
                    floor_id = f"floor_{b+1}_{floor_idx}"
                    floor = Node(
                        floor_id, "Floor",
                        {
                            "name": f"Floor {floor_idx}",
                            "floor_type": floor_type,
                            "building_id": building_id
                        }
                    )
                    self.nodes.append(floor)
                    self.edges.append(Edge(building.id, floor.id, "CONTAINS"))

                    # Create spaces for this floor type
                    floor_dist = self.space_types.get("floor_distribution", {}).get(floor_type, {})
                    space_idx = 0
                    for space_type, count in floor_dist.items():
                        for _ in range(count):
                            space_id = f"space_{b+1}_{floor_idx}_{space_idx}"
                            space = Node(
                                space_id, "Space",
                                {
                                    "name": f"{space_type.replace('_', ' ').title()} {space_idx}",
                                    "space_type": space_type,
                                    "floor_id": floor_id,
                                    "building_id": building_id
                                }
                            )
                            self.nodes.append(space)
                            self.edges.append(Edge(floor.id, space.id, "CONTAINS"))

                            # Index for later use
                            self.spaces_by_floor[floor_id].append(space)
                            self.spaces_by_building[building_id].append(space)

                            space_idx += 1

                    floor_idx += 1

    def _create_meters(self) -> None:
        """Create meters and their FEEDS hierarchy."""
        meter_config = self.profile.get("meters", {"main": 1, "sub_per_main": 5})

        for b in range(self.profile["buildings"]):
            building_id = f"building_{b+1}"

            # Main meter
            main_id = f"meter_main_{b+1}"
            main_meter = Node(
                main_id, "Equipment",
                {
                    "equipment_type": "MainMeter",
                    "name": f"Main Meter B{b+1}",
                    "building_id": building_id,
                    "domain": "Electrical"
                }
            )
            self.nodes.append(main_meter)
            self.equipments_by_type["MainMeter"].append(main_meter)
            self.equipments_by_building[building_id].append(main_meter)

            # Create points for main meter
            self._create_meter_points(main_meter)

            # Sub meters
            sub_count = meter_config.get("sub_per_main", 5)
            for s in range(sub_count):
                sub_id = f"meter_sub_{b+1}_{s}"
                sub_meter = Node(
                    sub_id, "Equipment",
                    {
                        "equipment_type": "SubMeter",
                        "name": f"Sub Meter B{b+1}-{s}",
                        "building_id": building_id,
                        "domain": "Electrical"
                    }
                )
                self.nodes.append(sub_meter)
                self.equipments_by_type["SubMeter"].append(sub_meter)
                self.equipments_by_building[building_id].append(sub_meter)

                # FEEDS: main -> sub
                self.edges.append(Edge(main_id, sub_id, "FEEDS"))

                # Create points for sub meter
                self._create_meter_points(sub_meter)

    def _create_meter_points(self, meter: Node) -> None:
        """Create points for a meter."""
        meter_points = [
            {"name": "active_energy", "unit": "kWh", "range_min": 0, "range_max": 100000},
            {"name": "active_power", "unit": "kW", "range_min": 0, "range_max": 500},
            {"name": "voltage", "unit": "V", "range_min": 380, "range_max": 420},
            {"name": "current", "unit": "A", "range_min": 0, "range_max": 800},
        ]

        for pt_def in meter_points:
            point_id = f"point_{meter.id}_{pt_def['name']}"
            point = Point(
                id=point_id,
                name=pt_def["name"],
                equipment_id=meter.id,
                unit=pt_def["unit"],
                range_min=pt_def["range_min"],
                range_max=pt_def["range_max"],
                frequency=900,  # 15 min
                point_type="mesure"
            )
            self.points.append(point)

            # Create point node
            point_node = Node(
                point_id, "Point",
                {
                    "name": pt_def["name"],
                    "equipment_id": meter.id,
                    "unit": pt_def["unit"]
                }
            )
            self.nodes.append(point_node)
            self.edges.append(Edge(meter.id, point_id, "HAS_POINT"))

    def _distribute_equipment(self) -> None:
        """Distribute equipment to spaces according to distribution matrix."""
        distribution = self.distribution.get("distribution", {})

        for space in self.nodes:
            if space.type != "Space":
                continue

            space_type = space.properties.get("space_type")
            if not space_type or space_type not in distribution:
                continue

            # Get equipment distribution for this space type
            space_dist = distribution[space_type]
            equip_idx = 0

            for domain, equip_specs in space_dist.items():
                for spec in equip_specs:
                    equip_type = spec["type"]
                    min_qty = spec.get("min", 1)
                    max_qty = spec.get("max", 1)
                    qty = self.rng.randint(min_qty, max_qty)

                    for _ in range(qty):
                        equip_id = f"equip_{space.id}_{equip_idx}"
                        equipment = Node(
                            equip_id, "Equipment",
                            {
                                "equipment_type": equip_type,
                                "name": f"{equip_type}-{space.id}-{equip_idx}",
                                "space_id": space.id,
                                "floor_id": space.properties.get("floor_id"),
                                "building_id": space.properties.get("building_id"),
                                "domain": domain
                            }
                        )
                        self.nodes.append(equipment)
                        self.edges.append(Edge(equip_id, space.id, "LOCATED_IN"))

                        # Index
                        self.equipments_by_type[equip_type].append(equipment)
                        self.equipments_by_building[space.properties["building_id"]].append(equipment)

                        # Create points for this equipment
                        self._create_equipment_points(equipment, equip_type, domain)

                        # Create child components if this is a composite equipment
                        if equip_type in HAS_PART_RULES:
                            self._create_components(equipment, equip_type, domain, space)

                        equip_idx += 1

    def _create_components(self, parent: Node, parent_type: str, domain: str, space: Node) -> None:
        """Create child components for composite equipment.

        These are internal components (Fan, Coil, Filter, etc.) that are part of
        larger equipment (AHU, Chiller, etc.).
        """
        child_types = HAS_PART_RULES.get(parent_type, [])

        for i, child_type in enumerate(child_types):
            child_id = f"comp_{parent.id}_{child_type}_{i}"
            child = Node(
                child_id, "Equipment",
                {
                    "equipment_type": child_type,
                    "name": f"{child_type}-{parent.id}",
                    "parent_id": parent.id,
                    "space_id": space.id,
                    "floor_id": space.properties.get("floor_id"),
                    "building_id": space.properties.get("building_id"),
                    "domain": domain,
                    "is_component": True,
                }
            )
            self.nodes.append(child)

            # Index component
            self.equipments_by_type[child_type].append(child)
            self.equipments_by_building[space.properties["building_id"]].append(child)

            # HAS_PART edge is created in _create_has_part_relations

    def _create_equipment_points(self, equipment: Node, equip_type: str, domain: str) -> None:
        """Create points for an equipment based on definitions or defaults."""
        # Try to find equipment definition
        eq_def = None
        for key, ed in self.equipment_defs.items():
            if ed.code == equip_type or key.endswith(f"/{equip_type}"):
                eq_def = ed
                break

        if eq_def and eq_def.points:
            points_def = eq_def.points
        else:
            # Default points
            points_def = self._get_default_points(equip_type, domain)

        for pt_def in points_def:
            point_id = f"point_{equipment.id}_{pt_def['name']}"
            point = Point(
                id=point_id,
                name=pt_def["name"],
                equipment_id=equipment.id,
                unit=pt_def.get("unit", "-"),
                range_min=pt_def.get("range_min", 0),
                range_max=pt_def.get("range_max", 100),
                frequency=pt_def.get("frequency", 300),
                point_type=pt_def.get("type", "mesure")
            )
            self.points.append(point)

            # Create point node
            point_node = Node(
                point_id, "Point",
                {
                    "name": pt_def["name"],
                    "equipment_id": equipment.id,
                    "unit": pt_def.get("unit", "-"),
                    "quantity": self._infer_quantity(pt_def["name"])
                }
            )
            self.nodes.append(point_node)
            self.edges.append(Edge(equipment.id, point_id, "HAS_POINT"))

    def _get_default_points(self, equip_type: str, domain: str) -> List[dict]:
        """Get default points for an equipment type."""
        # Default point sets by equipment type
        defaults = {
            "FCU": [
                {"name": "supply_air_temp", "unit": "°C", "range_min": 12, "range_max": 28, "frequency": 300, "type": "mesure"},
                {"name": "return_air_temp", "unit": "°C", "range_min": 18, "range_max": 26, "frequency": 300, "type": "mesure"},
                {"name": "fan_speed", "unit": "%", "range_min": 0, "range_max": 100, "frequency": 300, "type": "mesure"},
                {"name": "valve_position", "unit": "%", "range_min": 0, "range_max": 100, "frequency": 60, "type": "commande"},
                {"name": "fan_status", "unit": "-", "range_min": 0, "range_max": 1, "frequency": 0, "type": "etat"},
            ],
            "Thermostat": [
                {"name": "zone_temp", "unit": "°C", "range_min": 18, "range_max": 26, "frequency": 300, "type": "mesure"},
                {"name": "setpoint_temp", "unit": "°C", "range_min": 18, "range_max": 26, "frequency": 0, "type": "commande"},
                {"name": "mode", "unit": "-", "range_min": 0, "range_max": 3, "frequency": 0, "type": "commande"},
            ],
            "AHU": [
                {"name": "supply_air_temp", "unit": "°C", "range_min": 12, "range_max": 28, "frequency": 300, "type": "mesure"},
                {"name": "return_air_temp", "unit": "°C", "range_min": 18, "range_max": 26, "frequency": 300, "type": "mesure"},
                {"name": "outdoor_air_temp", "unit": "°C", "range_min": -10, "range_max": 40, "frequency": 300, "type": "mesure"},
                {"name": "supply_fan_speed", "unit": "%", "range_min": 0, "range_max": 100, "frequency": 300, "type": "mesure"},
                {"name": "return_fan_speed", "unit": "%", "range_min": 0, "range_max": 100, "frequency": 300, "type": "mesure"},
                {"name": "heating_valve", "unit": "%", "range_min": 0, "range_max": 100, "frequency": 60, "type": "commande"},
                {"name": "cooling_valve", "unit": "%", "range_min": 0, "range_max": 100, "frequency": 60, "type": "commande"},
                {"name": "damper_position", "unit": "%", "range_min": 0, "range_max": 100, "frequency": 60, "type": "commande"},
                {"name": "filter_dp", "unit": "Pa", "range_min": 0, "range_max": 500, "frequency": 1800, "type": "mesure"},
                {"name": "run_status", "unit": "-", "range_min": 0, "range_max": 1, "frequency": 0, "type": "etat"},
            ],
            "PeopleCounter": [
                {"name": "occupancy_count", "unit": "persons", "range_min": 0, "range_max": 50, "frequency": 300, "type": "mesure"},
                {"name": "in_count", "unit": "persons", "range_min": 0, "range_max": 200, "frequency": 300, "type": "mesure"},
                {"name": "out_count", "unit": "persons", "range_min": 0, "range_max": 200, "frequency": 300, "type": "mesure"},
            ],
            "LED_Luminaire": [
                {"name": "dim_level", "unit": "%", "range_min": 0, "range_max": 100, "frequency": 0, "type": "commande"},
                {"name": "power", "unit": "W", "range_min": 0, "range_max": 100, "frequency": 300, "type": "mesure"},
                {"name": "status", "unit": "-", "range_min": 0, "range_max": 1, "frequency": 0, "type": "etat"},
            ],
            "SmokeDetector": [
                {"name": "alarm", "unit": "-", "range_min": 0, "range_max": 1, "frequency": 0, "type": "alarme"},
                {"name": "fault", "unit": "-", "range_min": 0, "range_max": 1, "frequency": 0, "type": "alarme"},
                {"name": "status", "unit": "-", "range_min": 0, "range_max": 1, "frequency": 0, "type": "etat"},
            ],
        }

        if equip_type in defaults:
            return defaults[equip_type]

        # Generic defaults
        return [
            {"name": "status", "unit": "-", "range_min": 0, "range_max": 1, "frequency": 0, "type": "etat"},
            {"name": "value", "unit": "-", "range_min": 0, "range_max": 100, "frequency": 300, "type": "mesure"},
        ]

    def _infer_quantity(self, point_name: str) -> str:
        """Infer the physical quantity from point name."""
        name_lower = point_name.lower()
        if "temp" in name_lower:
            return "temperature"
        elif "power" in name_lower:
            return "power"
        elif "energy" in name_lower:
            return "energy"
        elif "pressure" in name_lower or "_dp" in name_lower:
            return "pressure"
        elif "flow" in name_lower:
            return "flow"
        elif "humidity" in name_lower:
            return "humidity"
        elif "co2" in name_lower:
            return "co2"
        elif "count" in name_lower or "occupancy" in name_lower:
            return "count"
        elif "position" in name_lower or "valve" in name_lower or "damper" in name_lower:
            return "position"
        elif "speed" in name_lower:
            return "speed"
        elif "status" in name_lower or "mode" in name_lower:
            return "status"
        return "value"

    def _create_feeds_relations(self) -> None:
        """Create FEEDS relations between equipment."""
        for source_type, target_types in FEEDS_RULES.items():
            sources = self.equipments_by_type.get(source_type, [])

            for target_type in target_types:
                targets = self.equipments_by_type.get(target_type, [])

                # Group by building
                for building_id in self.equipments_by_building:
                    bld_sources = [s for s in sources if s.properties.get("building_id") == building_id]
                    bld_targets = [t for t in targets if t.properties.get("building_id") == building_id]

                    if not bld_sources or not bld_targets:
                        continue

                    # Round-robin distribution
                    for i, target in enumerate(bld_targets):
                        source = bld_sources[i % len(bld_sources)]
                        self.edges.append(Edge(source.id, target.id, "FEEDS"))

        # SubMeter -> Equipment (electrical equipment only)
        for building_id, equips in self.equipments_by_building.items():
            sub_meters = [e for e in equips if e.properties.get("equipment_type") == "SubMeter"]
            electrical_equips = [e for e in equips
                                 if e.properties.get("domain") == "Electrical"
                                 and e.properties.get("equipment_type") not in ("MainMeter", "SubMeter")]

            if sub_meters and electrical_equips:
                for i, equip in enumerate(electrical_equips):
                    sub = sub_meters[i % len(sub_meters)]
                    self.edges.append(Edge(sub.id, equip.id, "FEEDS"))

    def _create_serves_relations(self) -> None:
        """Create SERVES relations between equipment and spaces."""
        all_spaces = [n for n in self.nodes if n.type == "Space"]

        for equip in self.nodes:
            if equip.type != "Equipment":
                continue

            equip_type = equip.properties.get("equipment_type", "")
            rule = SERVES_RULES.get(equip_type, {"scope": "space", "ratio": 1.0})
            scope = rule["scope"]
            ratio = rule["ratio"]

            if scope == "space":
                # Serves only its own space
                space_id = equip.properties.get("space_id")
                if space_id:
                    self.edges.append(Edge(equip.id, space_id, "SERVES"))

            elif scope == "floor":
                floor_id = equip.properties.get("floor_id")
                if floor_id:
                    floor_spaces = self.spaces_by_floor.get(floor_id, [])
                    n_served = max(1, int(len(floor_spaces) * ratio))
                    for space in floor_spaces[:n_served]:
                        self.edges.append(Edge(equip.id, space.id, "SERVES"))

            elif scope == "building":
                building_id = equip.properties.get("building_id")
                if building_id:
                    bld_spaces = self.spaces_by_building.get(building_id, [])
                    n_served = max(1, int(len(bld_spaces) * ratio))
                    for space in bld_spaces[:n_served]:
                        self.edges.append(Edge(equip.id, space.id, "SERVES"))

    def _create_has_part_relations(self) -> None:
        """Create HAS_PART relations for composite equipment."""
        for parent_type, child_types in HAS_PART_RULES.items():
            parents = self.equipments_by_type.get(parent_type, [])

            for child_type in child_types:
                children = self.equipments_by_type.get(child_type, [])

                for child in children:
                    # Find parent in same building
                    child_bld = child.properties.get("building_id")
                    parent = next(
                        (p for p in parents if p.properties.get("building_id") == child_bld),
                        None
                    )
                    if parent:
                        self.edges.append(Edge(parent.id, child.id, "HAS_PART"))

    def _create_controls_relations(self) -> None:
        """Create CONTROLS relations between controllers and controlled equipment.

        Represents BMS control relationships (Brick: controls).
        Example: Thermostat CONTROLS FCU
        """
        for controller_type, controlled_types in CONTROLS_RULES.items():
            controllers = self.equipments_by_type.get(controller_type, [])

            for controlled_type in controlled_types:
                controlled = self.equipments_by_type.get(controlled_type, [])

                # Group by building for logical pairing
                for building_id in self.equipments_by_building:
                    bld_controllers = [c for c in controllers if c.properties.get("building_id") == building_id]
                    bld_controlled = [c for c in controlled if c.properties.get("building_id") == building_id]

                    if not bld_controllers or not bld_controlled:
                        continue

                    # Round-robin: each controller controls multiple equipment
                    for i, equip in enumerate(bld_controlled):
                        controller = bld_controllers[i % len(bld_controllers)]
                        self.edges.append(Edge(controller.id, equip.id, "CONTROLS"))

    def _create_monitors_relations(self) -> None:
        """Create MONITORS relations between sensors and monitored equipment.

        Represents sensor monitoring relationships.
        Example: TemperatureSensor MONITORS FCU
        """
        for sensor_type, monitored_types in MONITORS_RULES.items():
            sensors = self.equipments_by_type.get(sensor_type, [])

            for monitored_type in monitored_types:
                monitored = self.equipments_by_type.get(monitored_type, [])

                # Group by building
                for building_id in self.equipments_by_building:
                    bld_sensors = [s for s in sensors if s.properties.get("building_id") == building_id]
                    bld_monitored = [m for m in monitored if m.properties.get("building_id") == building_id]

                    if not bld_sensors or not bld_monitored:
                        continue

                    # Each sensor monitors one or more equipment (round-robin)
                    for i, equip in enumerate(bld_monitored):
                        sensor = bld_sensors[i % len(bld_sensors)]
                        self.edges.append(Edge(sensor.id, equip.id, "MONITORS"))

    def _create_is_metered_by_relations(self) -> None:
        """Create IS_METERED_BY relations between equipment and sub-meters.

        Represents metering relationships (Haystack: submeterOf).
        Example: ElectricalPanel IS_METERED_BY SubMeter
        """
        sub_meters = self.equipments_by_type.get("SubMeter", [])

        if not sub_meters:
            return

        # Collect all metered equipment
        metered_equipment = []
        for equip_type in METERED_EQUIPMENT:
            metered_equipment.extend(self.equipments_by_type.get(equip_type, []))

        # Group by building
        for building_id in self.equipments_by_building:
            bld_meters = [m for m in sub_meters if m.properties.get("building_id") == building_id]
            bld_metered = [e for e in metered_equipment if e.properties.get("building_id") == building_id]

            if not bld_meters or not bld_metered:
                continue

            # Distribute equipment across sub-meters
            for i, equip in enumerate(bld_metered):
                meter = bld_meters[i % len(bld_meters)]
                self.edges.append(Edge(equip.id, meter.id, "IS_METERED_BY"))

    def _create_tenants(self) -> None:
        """Create tenants and OCCUPIES relations."""
        n_tenants = self.profile.get("tenants", 3)

        # Create tenant nodes
        tenants = []
        for i in range(n_tenants):
            tenant_id = f"tenant_{i+1}"
            tenant = Node(
                tenant_id, "Tenant",
                {"name": f"Tenant {i+1}"}
            )
            self.nodes.append(tenant)
            tenants.append(tenant)

        # Distribute occupiable spaces to tenants
        occupiable_types = {
            "office_open", "office_closed", "meeting_small", "meeting_large",
            "conference", "lobby", "kitchen"
        }

        occupiable_spaces = [
            s for s in self.nodes
            if s.type == "Space" and s.properties.get("space_type") in occupiable_types
        ]

        for i, space in enumerate(occupiable_spaces):
            tenant = tenants[i % n_tenants]
            self.edges.append(Edge(tenant.id, space.id, "OCCUPIES"))


# =============================================================================
# TIMESERIES GENERATION
# =============================================================================

def generate_timeseries(
    points: List[Point],
    duration_days: int,
    rng: random.Random,
    start_time: Optional[datetime] = None,
    show_progress: bool = True,
    use_simulation: bool = True,
    simulation_config_path: Optional[Path] = None,
    n_workers: Optional[int] = None,
    mode: str = "vectorized",
) -> Iterator[Tuple[str, datetime, float]]:
    """Generate timeseries data for all points.

    Args:
        points: List of Point objects
        duration_days: Duration in days
        rng: Random number generator
        start_time: Start timestamp (default: 2024-01-01)
        show_progress: Show progress bar (default: True)
        use_simulation: Use physical simulation with deadband (default: True)
        simulation_config_path: Path to simulation.yaml config file
        n_workers: Number of worker processes (for mode='parallel' only)
        mode: Simulation mode:
            - "vectorized": NumPy vectorized (100-500x faster, RECOMMENDED)
            - "sequential": Original Python step-by-step
            - "parallel": Multiprocessing (deprecated; usually slower than vectorized)

    Yields:
        Tuples of (point_id, timestamp, value)
    """
    if start_time is None:
        start_time = datetime(2024, 1, 1)

    if use_simulation:
        # Use physical simulation engine with deadband filtering
        yield from _generate_timeseries_simulation(
            points, duration_days, rng, start_time,
            show_progress, simulation_config_path,
            mode=mode, n_workers=n_workers
        )
    else:
        # Legacy mode: independent Gaussian samples
        yield from _generate_timeseries_legacy(
            points, duration_days, rng, start_time, show_progress
        )


def _generate_timeseries_simulation(
    points: List[Point],
    duration_days: int,
    rng: random.Random,
    start_time: datetime,
    show_progress: bool,
    config_path: Optional[Path] = None,
    mode: str = "vectorized",
    n_workers: Optional[int] = None,
) -> Iterator[Tuple[str, datetime, float]]:
    """Generate timeseries using physical simulation with deadband.

    This mode produces ~7x less data than legacy mode by:
    - Using Ornstein-Uhlenbeck process for temporal correlation
    - Applying deadband filtering (only transmit on significant change)
    - Modeling occupancy and environmental context

    Args:
        mode: Simulation mode ("vectorized", "sequential", "parallel")
        n_workers: Number of worker processes (for parallel mode only)
    """
    # Load simulation config
    if config_path is None:
        config_path = Path("config/simulation.yaml")

    if config_path.exists():
        config = SimulationConfig.load(config_path)
    else:
        config = SimulationConfig.default()

    # Convert Point objects to PointInfo for simulation
    point_infos = [
        PointInfo(
            id=p.id,
            name=p.name,
            equipment_id=p.equipment_id,
            unit=p.unit,
            setpoint=(p.range_min + p.range_max) / 2,
        )
        for p in points
    ]

    # Create simulation engine
    engine = SimulationEngine(
        config=config,
        rng=rng,
        start_time=start_time,
    )

    # Generate samples using the specified mode
    for sample in engine.generate(
        point_infos, duration_days, show_progress,
        mode=mode, n_workers=n_workers
    ):
        yield (sample.point_id, sample.timestamp, sample.value)


def _generate_timeseries_legacy(
    points: List[Point],
    duration_days: int,
    rng: random.Random,
    start_time: datetime,
    show_progress: bool,
) -> Iterator[Tuple[str, datetime, float]]:
    """Legacy timeseries generation: independent Gaussian samples.

    This mode generates samples at fixed intervals without correlation
    or deadband filtering. Useful for comparison or backwards compatibility.
    """
    # Wrap with progress bar if available
    point_iter = points
    if show_progress and HAS_TQDM:
        point_iter = tqdm(
            points,
            desc="Generating timeseries (legacy)",
            unit="points",
            ncols=80,
            leave=True
        )

    for point in point_iter:
        config = get_point_config(point.name)

        if config["mode"] == "regular":
            frequency = config["frequency"]
            if frequency <= 0:
                frequency = 300  # Default 5 min

            samples = (duration_days * 86400) // frequency

            for i in range(samples):
                timestamp = start_time + timedelta(seconds=i * frequency)
                value = generate_gaussian_value(point, rng)
                yield (point.id, timestamp, value)

        elif config["mode"] == "event":
            events_per_day = config.get("events_per_day", 1)
            n_events = int(duration_days * events_per_day)
            n_events = max(1, int(rng.gauss(n_events, n_events * 0.3)))

            timestamps = sorted([
                start_time + timedelta(seconds=rng.randint(0, duration_days * 86400))
                for _ in range(n_events)
            ])

            for ts in timestamps:
                value = generate_event_value(point, rng)
                yield (point.id, ts, value)


def generate_gaussian_value(point: Point, rng: random.Random) -> float:
    """Generate a Gaussian value within the point's range."""
    mean = (point.range_min + point.range_max) / 2
    std = (point.range_max - point.range_min) / 6
    value = rng.gauss(mean, std)
    return round(max(point.range_min, min(point.range_max, value)), 2)


def generate_event_value(point: Point, rng: random.Random) -> float:
    """Generate an event value (binary or discrete)."""
    if point.range_max <= 1:
        return float(rng.choice([0, 1]))
    return float(rng.randint(int(point.range_min), int(point.range_max)))


# =============================================================================
# CHUNKING FOR M1/O1
# =============================================================================

CHUNK_SIZE = 50


def generate_chunks(
    point_id: str,
    samples: List[Tuple[datetime, float]]
) -> Iterator[TSChunk]:
    """Generate timeseries chunks for M1/O1 format.

    Uses explicit timestamps to support irregular intervals from deadband filtering.
    Each chunk contains up to CHUNK_SIZE (timestamp, value) pairs.

    Args:
        point_id: Point identifier
        samples: List of (timestamp, value) tuples

    Yields:
        TSChunk objects with explicit timestamps
    """
    for chunk_idx, i in enumerate(range(0, len(samples), CHUNK_SIZE)):
        chunk_samples = samples[i:i + CHUNK_SIZE]
        if not chunk_samples:
            continue

        yield TSChunk(
            point_id=point_id,
            chunk_idx=chunk_idx,
            timestamps=[int(ts.timestamp()) for ts, _ in chunk_samples],
            values=[v for _, v in chunk_samples]
        )


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for the generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate smart building dataset v2.0")
    parser.add_argument("profile", choices=["small", "medium", "large"],
                        help="Profile to generate")
    parser.add_argument("--config", type=Path, default=Path("config"),
                        help="Path to config directory")
    parser.add_argument("--exploration", type=Path, default=Path("docs/Exploration"),
                        help="Path to Exploration docs")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--stats", action="store_true",
                        help="Print statistics only")

    args = parser.parse_args()

    generator = DatasetGeneratorV2(
        profile_name=args.profile,
        config_path=args.config,
        exploration_path=args.exploration,
        seed=args.seed
    )

    dataset = generator.generate()

    # Print statistics
    node_counts = defaultdict(int)
    for node in dataset.nodes:
        node_counts[node.type] += 1

    edge_counts = defaultdict(int)
    for edge in dataset.edges:
        edge_counts[edge.rel_type] += 1

    print(f"\n=== Dataset {args.profile.upper()} ===")
    print(f"Seed: {dataset.seed}")
    print(f"\nNodes ({len(dataset.nodes)} total):")
    for node_type, count in sorted(node_counts.items()):
        print(f"  {node_type}: {count}")

    print(f"\nEdges ({len(dataset.edges)} total):")
    for rel_type, count in sorted(edge_counts.items()):
        print(f"  {rel_type}: {count}")

    print(f"\nPoints: {len(dataset.points)}")

    # Target comparison
    targets = generator.profile.get("targets", {})
    print(f"\nTarget comparison:")
    print(f"  Spaces: {node_counts['Space']} (target: ~{targets.get('spaces', '?')})")
    print(f"  Equipment: {node_counts['Equipment']} (target: ~{targets.get('equipments', '?')})")
    print(f"  Points: {len(dataset.points)} (target: ~{targets.get('points', '?')})")


if __name__ == "__main__":
    main()
