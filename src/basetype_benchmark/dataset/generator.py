"""
Dataset Generator - Benchmark BaseType V3
Génère des datasets de différentes tailles à partir des configs equipment et profiles.

Usage:
    python -m src.basetype_benchmark.dataset.generator --profile small --output data/generated
    python -m src.basetype_benchmark.dataset.generator --profile medium --seed 42
"""

import argparse
import random
import yaml
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import math

# Dataclasses partagées pour la génération de données
from .models import Node, Edge, TimeseriesPoint


# ===========================================================================
# CONFIGURATION LOADERS
# ===========================================================================

@dataclass
class EquipmentConfig:
    """Configuration d'un type d'équipement depuis config/equipment/*.yaml"""
    code: str
    domain: str
    haystack: str
    brick: str
    protocols: List[str]
    points: List[Dict[str, Any]]

    @classmethod
    def from_yaml(cls, filepath: Path) -> 'EquipmentConfig':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        eq = data.get('equipment', {})
        return cls(
            code=eq.get('code', ''),
            domain=eq.get('domain', ''),
            haystack=eq.get('haystack', ''),
            brick=eq.get('brick', ''),
            protocols=eq.get('protocols', []),
            points=data.get('points', [])
        )


@dataclass
class ProfileConfig:
    """Configuration d'un profil depuis config/profiles/*.yaml"""
    profile: str
    seed: int
    buildings: int
    floors: List[Dict[str, Any]]
    tenants: int
    meters: Dict[str, Any]
    targets: Dict[str, int]
    space_distribution: Dict[str, Dict[str, int]]
    durations: List[Dict[str, Any]]

    @classmethod
    def from_yaml(cls, filepath: Path) -> 'ProfileConfig':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            profile=data.get('profile', 'custom'),
            seed=data.get('seed', 42),
            buildings=data.get('buildings', 1),
            floors=data.get('floors', []),
            tenants=data.get('tenants', 1),
            meters=data.get('meters', {}),
            targets=data.get('targets', {}),
            space_distribution=data.get('space_distribution', {}),
            durations=data.get('durations', [])
        )


# ===========================================================================
# EQUIPMENT REGISTRY
# ===========================================================================

class EquipmentRegistry:
    """Registre de tous les types d'équipements disponibles"""

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.equipment_types: Dict[str, EquipmentConfig] = {}
        self._load_all()

    def _load_all(self):
        """Charge tous les fichiers equipment/*.yaml"""
        equipment_dir = self.config_dir / "equipment"
        if not equipment_dir.exists():
            raise FileNotFoundError(f"Equipment config directory not found: {equipment_dir}")

        for yaml_file in equipment_dir.glob("*.yaml"):
            try:
                config = EquipmentConfig.from_yaml(yaml_file)
                # Utiliser le nom du fichier (sans extension) comme clé
                name = yaml_file.stem
                self.equipment_types[name] = config
            except Exception as e:
                print(f"Warning: Failed to load {yaml_file}: {e}")

    def get(self, name: str) -> Optional[EquipmentConfig]:
        return self.equipment_types.get(name)

    def get_by_domain(self, domain: str) -> List[Tuple[str, EquipmentConfig]]:
        return [(n, c) for n, c in self.equipment_types.items() if c.domain == domain]

    def list_domains(self) -> List[str]:
        return list(set(c.domain for c in self.equipment_types.values()))


# ===========================================================================
# PROTOCOL GENERATOR
# ===========================================================================

class ProtocolGenerator:
    """Génère les propriétés protocol réalistes selon le type d'équipement"""

    BACNET_VENDORS = {
        'Schneider': 10, 'Siemens': 7, 'Honeywell': 19,
        'Johnson Controls': 5, 'Trane': 102, 'Carrier': 56,
        'Daikin': 212, 'Delta': 127
    }

    MODBUS_VENDORS = ['Schneider', 'ABB', 'Socomec', 'Janitza', 'Carlo Gavazzi']

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.bacnet_device_counter = 1000
        self.modbus_address_counter = 1

    def generate_bacnet(self, equipment_type: str) -> Dict[str, Any]:
        """Génère un protocol BACnet"""
        vendor = self.rng.choice(list(self.BACNET_VENDORS.keys()))
        self.bacnet_device_counter += self.rng.randint(1, 10)
        return {
            'type': 'BACnet',
            'device_id': self.bacnet_device_counter,
            'network': self.rng.randint(1, 5),
            'address': f"192.168.{self.rng.randint(1, 10)}.{self.rng.randint(1, 254)}:47808",
            'vendor_id': self.BACNET_VENDORS[vendor]
        }

    def generate_modbus(self, equipment_type: str) -> Dict[str, Any]:
        """Génère un protocol Modbus"""
        self.modbus_address_counter += 1
        is_tcp = self.rng.random() > 0.3
        return {
            'type': 'Modbus_TCP' if is_tcp else 'Modbus_RTU',
            'address': f"192.168.{self.rng.randint(1, 10)}.{self.modbus_address_counter}" if is_tcp else str(self.modbus_address_counter),
            'port': 502 if is_tcp else None,
            'unit_id': self.rng.randint(1, 247)
        }

    def generate_snmp(self, equipment_type: str) -> Dict[str, Any]:
        """Génère un protocol SNMP pour IT"""
        return {
            'type': 'SNMP',
            'version': self.rng.choice(['v2c', 'v3']),
            'address': f"192.168.{self.rng.randint(1, 10)}.{self.rng.randint(1, 254)}",
            'community': 'public' if self.rng.random() > 0.5 else 'private'
        }

    def generate_onvif(self, equipment_type: str) -> Dict[str, Any]:
        """Génère un protocol ONVIF pour caméras"""
        return {
            'type': 'ONVIF',
            'address': f"192.168.{self.rng.randint(1, 10)}.{self.rng.randint(1, 254)}",
            'port': 80,
            'profile': self.rng.choice(['S', 'G', 'T'])
        }

    def generate_osdp(self, equipment_type: str) -> Dict[str, Any]:
        """Génère un protocol OSDP pour contrôle d'accès"""
        return {
            'type': 'OSDP',
            'address': self.rng.randint(0, 126),
            'baud_rate': self.rng.choice([9600, 19200, 38400, 115200]),
            'secure_channel': self.rng.random() > 0.3
        }

    def generate_dali(self, equipment_type: str) -> Dict[str, Any]:
        """Génère un protocol DALI pour éclairage"""
        return {
            'type': 'DALI',
            'short_address': self.rng.randint(0, 63),
            'group': self.rng.randint(0, 15) if self.rng.random() > 0.5 else None,
            'version': self.rng.choice(['DALI', 'DALI-2'])
        }

    def generate_ipmi(self, equipment_type: str) -> Dict[str, Any]:
        """Génère un protocol IPMI/Redfish pour serveurs"""
        return {
            'type': self.rng.choice(['IPMI', 'Redfish']),
            'address': f"192.168.{self.rng.randint(1, 10)}.{self.rng.randint(1, 254)}",
            'port': 623 if self.rng.random() > 0.5 else 443
        }

    def generate_for_equipment(self, equipment_config: EquipmentConfig) -> Dict[str, Any]:
        """Génère le protocol approprié selon les protocols supportés"""
        protocols = equipment_config.protocols
        if not protocols:
            return {}

        # Priorité: BACnet > Modbus > SNMP > ONVIF > OSDP > DALI > IPMI
        if 'bacnet' in protocols:
            return self.generate_bacnet(equipment_config.code)
        elif 'modbus' in protocols or 'modbus_tcp' in protocols or 'modbus_rtu' in protocols:
            return self.generate_modbus(equipment_config.code)
        elif 'snmp' in protocols:
            return self.generate_snmp(equipment_config.code)
        elif 'onvif' in protocols:
            return self.generate_onvif(equipment_config.code)
        elif 'osdp' in protocols:
            return self.generate_osdp(equipment_config.code)
        elif 'dali' in protocols:
            return self.generate_dali(equipment_config.code)
        elif 'ipmi' in protocols or 'redfish' in protocols:
            return self.generate_ipmi(equipment_config.code)
        else:
            # Protocol générique
            return {'type': protocols[0].upper()}


# ===========================================================================
# METADATA GENERATOR
# ===========================================================================

class MetadataGenerator:
    """Génère les métadonnées réalistes pour équipements"""

    MANUFACTURERS = {
        'HVAC': ['Carrier', 'Trane', 'Daikin', 'Johnson Controls', 'Honeywell', 'Siemens'],
        'Electrical': ['Schneider', 'ABB', 'Legrand', 'Eaton', 'Socomec'],
        'Security': ['Axis', 'Hikvision', 'HID', 'Genetec', 'Bosch'],
        'IT': ['Dell', 'HP', 'Cisco', 'Juniper', 'APC'],
        'Lighting': ['Philips', 'Osram', 'Zumtobel', 'Trilux', 'Tridonic'],
        'Parking': ['Skidata', 'Came', 'Nice', 'FAAC'],
        'BMS': ['Siemens', 'Honeywell', 'Schneider', 'Johnson Controls'],
        'Metering': ['Schneider', 'Janitza', 'Socomec', 'Carlo Gavazzi']
    }

    def __init__(self, rng: random.Random, reference_date: datetime):
        self.rng = rng
        self.reference_date = reference_date

    def generate(self, equipment_config: EquipmentConfig) -> Dict[str, Any]:
        """Génère les métadonnées pour un équipement"""
        domain = equipment_config.domain
        manufacturers = self.MANUFACTURERS.get(domain, self.MANUFACTURERS['BMS'])
        manufacturer = self.rng.choice(manufacturers)

        # Date d'installation (1-10 ans avant référence)
        days_ago = self.rng.randint(365, 3650)
        installation_date = self.reference_date - timedelta(days=days_ago)

        # Garantie (3-5 ans après installation)
        warranty_years = self.rng.randint(3, 5)
        warranty_end = installation_date + timedelta(days=warranty_years * 365)

        # Dernière maintenance (0-12 mois avant référence)
        last_maintenance = self.reference_date - timedelta(days=self.rng.randint(0, 365))

        metadata = {
            'manufacturer': manufacturer,
            'model': f"{equipment_config.code}-{self.rng.randint(100, 999)}",
            'serial_number': f"SN-{manufacturer[:3].upper()}-{self.rng.randint(100000, 999999)}",
            'installation_date': installation_date.strftime('%Y-%m-%d'),
            'warranty_end': warranty_end.strftime('%Y-%m-%d'),
            'maintenance_priority': self.rng.choice(['low', 'medium', 'high', 'critical']),
            'last_maintenance': last_maintenance.strftime('%Y-%m-%d'),
        }

        # Firmware pour certains équipements
        if domain in ['HVAC', 'IT', 'Security']:
            metadata['firmware_version'] = f"{self.rng.randint(1, 5)}.{self.rng.randint(0, 9)}.{self.rng.randint(0, 99)}"

        return metadata


# ===========================================================================
# CAPABILITIES & TAGS GENERATOR
# ===========================================================================

class CapabilitiesGenerator:
    """Génère capabilities et tags selon le type d'équipement"""

    CAPABILITIES_BY_TYPE = {
        'AHU': ['heating', 'cooling', 'humidity_control', 'air_filtration', 'heat_recovery', 'economizer'],
        'VAV': ['variable_air_volume', 'reheat', 'cooling_only'],
        'FCU': ['heating', 'cooling', 'fan_coil'],
        'Chiller': ['cooling', 'free_cooling', 'ice_storage'],
        'Boiler': ['heating', 'condensing', 'modulating'],
        'CRAC': ['cooling', 'humidity_control', 'precision_cooling', 'hot_aisle_containment'],
        'CoolingTower': ['heat_rejection', 'free_cooling', 'variable_speed_fans'],
        'UPS': ['battery_backup', 'surge_protection', 'power_conditioning'],
        'NetworkSwitch': ['poe', 'layer3', 'managed', 'stacking'],
        'IPCamera': ['ptz', 'night_vision', 'motion_detection', 'audio'],
        'BadgeReader': ['biometric', 'pin_code', 'mobile_credential'],
    }

    BRICK_TAGS = {
        'AHU': 'brick:Air_Handling_Unit',
        'VAV': 'brick:Variable_Air_Volume_Box',
        'FCU': 'brick:Fan_Coil_Unit',
        'Chiller': 'brick:Chiller',
        'Boiler': 'brick:Boiler',
        'CRAC': 'brick:Computer_Room_Air_Conditioning',
        'CoolingTower': 'brick:Cooling_Tower',
        'MainMeter': 'brick:Electrical_Meter',
        'SubMeter': 'brick:Electrical_Sub_Meter',
        'TemperatureSensor': 'brick:Temperature_Sensor',
        'CO2_Sensor': 'brick:CO2_Sensor',
    }

    HAYSTACK_TAGS = {
        'AHU': 'haystack:ahu',
        'VAV': 'haystack:vav',
        'FCU': 'haystack:fcu',
        'Chiller': 'haystack:chiller',
        'Boiler': 'haystack:boiler',
        'CRAC': 'haystack:crac',
        'CoolingTower': 'haystack:coolingTower',
        'MainMeter': 'haystack:elec-meter',
        'SubMeter': 'haystack:sub-meter',
    }

    def __init__(self, rng: random.Random):
        self.rng = rng

    def generate_capabilities(self, equipment_type: str) -> List[str]:
        """Génère la liste des capabilities pour un équipement"""
        available = self.CAPABILITIES_BY_TYPE.get(equipment_type, [])
        if not available:
            return []
        # Sélectionner 1 à N capabilities
        n = self.rng.randint(1, min(4, len(available)))
        return self.rng.sample(available, n)

    def generate_tags(self, equipment_type: str, equipment_config: EquipmentConfig) -> List[str]:
        """Génère les tags sémantiques"""
        tags = []

        # Tag Brick
        brick_tag = f"brick:{equipment_config.brick}" if equipment_config.brick else self.BRICK_TAGS.get(equipment_type)
        if brick_tag:
            tags.append(brick_tag)

        # Tag Haystack
        haystack_tag = f"haystack:{equipment_config.haystack}" if equipment_config.haystack else self.HAYSTACK_TAGS.get(equipment_type)
        if haystack_tag:
            tags.append(haystack_tag)

        # Tags additionnels aléatoires
        if self.rng.random() > 0.7:
            tags.append(self.rng.choice(['critical', 'primary', 'redundant', 'backup']))

        return tags


# ===========================================================================
# CALIBRATION GENERATOR
# ===========================================================================

class CalibrationGenerator:
    """Génère les données de calibration pour les points de mesure"""

    def __init__(self, rng: random.Random, reference_date: datetime):
        self.rng = rng
        self.reference_date = reference_date

    def generate(self, point_type: str, quantity: str) -> Dict[str, Any]:
        """Génère les données de calibration pour un point"""
        # Seulement pour les mesures, pas les commandes
        if point_type not in ['mesure', 'etat']:
            return {}

        # Dernière calibration (0-24 mois avant référence)
        days_since_last = self.rng.randint(0, 730)
        last_date = self.reference_date - timedelta(days=days_since_last)

        # Prochaine calibration (12-24 mois après dernière)
        next_interval = self.rng.randint(365, 730)
        next_date = last_date + timedelta(days=next_interval)

        # ~20% des calibrations sont échues
        if self.rng.random() < 0.2:
            next_date = self.reference_date - timedelta(days=self.rng.randint(1, 180))

        return {
            'last_date': last_date.strftime('%Y-%m-%d'),
            'next_date': next_date.strftime('%Y-%m-%d'),
            'offset': round(self.rng.uniform(-0.5, 0.5), 2),
            'technician': self.rng.choice(['Tech A', 'Tech B', 'Tech C', 'Vendor Service'])
        }


# ===========================================================================
# RANGE GENERATOR
# ===========================================================================

class RangeGenerator:
    """Génère les plages de mesure pour les points"""

    RANGES_BY_QUANTITY = {
        'temperature': {'min': -20, 'max': 50, 'unit': '°C', 'precision': 0.1},
        'humidity': {'min': 0, 'max': 100, 'unit': '%', 'precision': 1},
        'co2': {'min': 0, 'max': 5000, 'unit': 'ppm', 'precision': 1},
        'pressure': {'min': 0, 'max': 1000, 'unit': 'Pa', 'precision': 1},
        'flow': {'min': 0, 'max': 50000, 'unit': 'm³/h', 'precision': 10},
        'power': {'min': 0, 'max': 1000, 'unit': 'kW', 'precision': 0.1},
        'energy': {'min': 0, 'max': 1000000, 'unit': 'kWh', 'precision': 1},
        'voltage': {'min': 0, 'max': 500, 'unit': 'V', 'precision': 0.1},
        'current': {'min': 0, 'max': 1000, 'unit': 'A', 'precision': 0.1},
        'speed': {'min': 0, 'max': 100, 'unit': '%', 'precision': 1},
        'position': {'min': 0, 'max': 100, 'unit': '%', 'precision': 1},
    }

    def generate(self, quantity: str) -> Dict[str, Any]:
        """Génère la plage de mesure pour une quantity"""
        return self.RANGES_BY_QUANTITY.get(quantity, {})


# ===========================================================================
# MAIN GENERATOR CLASS
# ===========================================================================

class DatasetGenerator:
    """
    Générateur principal de dataset.

    Génère un dataset complet (nodes, edges, timeseries) selon un profil donné,
    en utilisant les configurations d'équipements de config/equipment/.
    """

    # Mapping durée -> heures
    DURATION_HOURS = {
        '2d': 48,
        '1w': 168,      # 7 * 24
        '1m': 720,      # 30 * 24
        '6m': 4320,     # 180 * 24
        '1y': 8760,     # 365 * 24
    }

    # Mapping frequency -> step en secondes
    FREQUENCY_STEP_SECONDS = {
        'fast': 60,      # 1 minute
        'normal': 300,   # 5 minutes
        'slow': 900,     # 15 minutes
        'energy': 900,   # 15 minutes (cumulative)
        'daily': 86400,  # 1 jour (métriques journalières)
        'event': 0,      # événements discrets, traitement spécial
    }

    # Profils d'événements par quantity (events/jour)
    EVENT_PROFILES = {
        'status': 5.0,    # ~5 events/jour (comm_status, breaker_status)
        'alarm': 1.0,     # ~1 event/jour (overload_alarm, power_quality_alarm)
        'fault': 0.14,    # ~1 event/semaine (sensor_fault)
        'default': 1.0,   # fallback
    }

    def __init__(self,
                 config_dir: Path,
                 profile: str = 'small',
                 seed: int = None,
                 reference_date: datetime = None,
                 duration: str = '2d',
                 target_rows: int = None):

        self.config_dir = Path(config_dir)
        self.profile_name = profile
        self.duration = duration
        self.duration_hours = self.DURATION_HOURS.get(duration, 48)
        self.target_rows = target_rows

        # Charger le profil
        profile_path = self.config_dir / "profiles" / f"{profile}.yaml"
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_path}")
        self.profile = ProfileConfig.from_yaml(profile_path)

        # Seed (priorité: paramètre > profil > défaut)
        self.seed = seed or self.profile.seed or 42
        self.rng = random.Random(self.seed)

        # Date de référence
        self.reference_date = reference_date or datetime(2024, 1, 15, 0, 0, 0)

        # Charger le registre d'équipements
        self.equipment_registry = EquipmentRegistry(self.config_dir)

        # Générateurs spécialisés
        self.protocol_gen = ProtocolGenerator(self.rng)
        self.metadata_gen = MetadataGenerator(self.rng, self.reference_date)
        self.capabilities_gen = CapabilitiesGenerator(self.rng)
        self.calibration_gen = CalibrationGenerator(self.rng, self.reference_date)
        self.range_gen = RangeGenerator()

        # Collections de sortie
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.timeseries: List[TimeseriesPoint] = []
        self._node_index: Dict[str, Node] = {}  # id -> Node for O(1) lookup

        # Index pour relations
        self._buildings: List[str] = []
        self._floors: Dict[str, List[str]] = {}  # building_id -> floor_ids
        self._spaces: Dict[str, List[str]] = {}  # floor_id -> space_ids
        self._equipment_by_space: Dict[str, List[str]] = {}
        self._equipment_by_building: Dict[str, List[str]] = {}
        self._points_by_equipment: Dict[str, List[str]] = {}
        self._meters: List[str] = []
        self._submeters: List[str] = []
        self._dali_gateways: Dict[str, str] = {}  # floor_id -> dali_gateway_id
        self._technicians: List[str] = []
        self._fire_panels: Dict[str, str] = {}  # building_id -> fire_panel_id
        self._chillers: List[str] = []  # Chiller equipment per building
        self._boilers: List[str] = []  # Boiler equipment per building

    def generate(self) -> 'DatasetGenerator':
        """Génère le dataset complet"""
        print(f"Generating dataset with profile '{self.profile_name}', seed={self.seed}")

        # 1. Hiérarchie spatiale
        self._generate_spatial_hierarchy()

        # 2. Équipements et points
        self._generate_equipment_and_points()

        # 3. Tenants
        self._generate_tenants()

        # 3b. Schedules and Leases
        self._generate_schedules_and_leases()

        # 4. Zones
        self._generate_zones()

        # 5. Relations additionnelles
        self._generate_additional_relations()

        # 6. Maintenance entities (Technicians, WorkOrders, Alarms)
        self._generate_maintenance_entities()

        # 7. Orphelin (pour Q5)
        self._generate_orphan()

        # 8. Timeseries
        self._generate_timeseries()

        print(f"Generated: {len(self.nodes)} nodes, {len(self.edges)} edges, {len(self.timeseries)} timeseries points")
        return self

    def _add_node(self, node: Node) -> None:
        """Ajoute un nœud à la liste et à l'index"""
        self.nodes.append(node)
        self._node_index[node.id] = node

    def _generate_spatial_hierarchy(self):
        """Génère Site → Buildings → Floors → Spaces"""

        # Site unique
        site_id = "site_1"
        self._add_node(Node(
            id=site_id,
            type="Site",
            name="Campus Principal",
            properties={'address': '1 Rue du Benchmark', 'gps_coords': {'lat': 48.8566, 'lon': 2.3522}}
        ))

        # Buildings
        for b in range(1, self.profile.buildings + 1):
            building_id = f"building_{b}"
            self._buildings.append(building_id)
            self._floors[building_id] = []
            self._equipment_by_building[building_id] = []

            self._add_node(Node(
                id=building_id,
                type="Building",
                name=f"Bâtiment {chr(64 + b)}",  # A, B, C...
                properties={
                    'site_id': site_id,
                    'address': f"Bâtiment {chr(64 + b)}, Campus Principal",
                    'gross_area_m2': self.rng.uniform(5000, 20000)
                }
            ))
            self.edges.append(Edge(site_id, building_id, "CONTAINS"))

            # Floors
            floor_counter = 0
            basement_counter = 0
            above_ground_counter = -1  # Will be 0 for ground floor
            for floor_config in self.profile.floors:
                floor_type = floor_config['type']
                floor_count = floor_config['count']

                for _ in range(floor_count):
                    floor_counter += 1
                    floor_id = f"floor_{b}_{floor_counter}"
                    self._floors[building_id].append(floor_id)
                    self._spaces[floor_id] = []

                    # Correct level_index: basement = -1, -2, ...; ground = 0; standard = 1, 2, ...
                    if floor_type == 'basement':
                        basement_counter += 1
                        level_index = -basement_counter
                    else:
                        above_ground_counter += 1
                        level_index = above_ground_counter

                    self._add_node(Node(
                        id=floor_id,
                        type="Floor",
                        name=f"Étage {level_index}" if level_index >= 0 else f"Sous-sol {-level_index}",
                        properties={
                            'building_id': building_id,
                            'floor_type': floor_type,
                            'level_index': level_index
                        }
                    ))
                    self.edges.append(Edge(building_id, floor_id, "CONTAINS"))

                    # Spaces selon distribution
                    space_dist = self.profile.space_distribution.get(floor_type, {})
                    space_counter = 0
                    for space_type, count in space_dist.items():
                        for _ in range(count):
                            space_counter += 1
                            space_id = f"space_{b}_{floor_counter}_{space_counter}"
                            self._spaces[floor_id].append(space_id)
                            self._equipment_by_space[space_id] = []

                            # Q27: is_exit for emergency exit spaces (stairwell, lobby, corridor on ground floor)
                            is_exit_space = space_type in ['stairwell', 'lobby', 'corridor'] and level_index == 0

                            self._add_node(Node(
                                id=space_id,
                                type="Space",
                                name=f"{space_type.replace('_', ' ').title()} {space_counter}",
                                properties={
                                    'floor_id': floor_id,
                                    'building_id': building_id,
                                    'space_type': space_type,
                                    'level_index': level_index,
                                    'area_m2': self.rng.uniform(15, 100),
                                    'capacity': self.rng.randint(2, 20),
                                    'is_exit': is_exit_space
                                }
                            ))
                            self.edges.append(Edge(floor_id, space_id, "CONTAINS"))

            # Adjacences entre espaces du même étage
            for floor_id in self._floors[building_id]:
                spaces = self._spaces[floor_id]
                for i in range(len(spaces) - 1):
                    # Q27: distance property for weighted shortest path
                    distance = self.rng.uniform(5.0, 25.0)  # meters
                    self.edges.append(Edge(spaces[i], spaces[i + 1], "ADJACENT_TO", {'distance': distance}))
                    self.edges.append(Edge(spaces[i + 1], spaces[i], "ADJACENT_TO", {'distance': distance}))

                # Q27: EMERGENCY_EXIT edges from all spaces to exit spaces on same floor
                exit_spaces = [s for s in spaces if self._get_node(s).properties.get('is_exit', False)]
                non_exit_spaces = [s for s in spaces if not self._get_node(s).properties.get('is_exit', False)]
                for exit_space in exit_spaces:
                    for space in non_exit_spaces:
                        # Distance proportional to position difference (simplified)
                        dist = self.rng.uniform(10.0, 50.0)
                        self.edges.append(Edge(space, exit_space, "EMERGENCY_EXIT", {'distance': dist}))

    def _generate_equipment_and_points(self):
        """Génère les équipements et leurs points selon les configs"""

        for building_id in self._buildings:
            # Collect all technical spaces for this building (for meter placement)
            all_technical_elec_spaces = []
            all_technical_hvac_spaces = []
            for floor_id in self._floors[building_id]:
                for space_id in self._spaces[floor_id]:
                    space_node = self._get_node(space_id)
                    space_type = space_node.properties.get('space_type', '')
                    if 'technical_elec' in space_type:
                        all_technical_elec_spaces.append(space_id)
                    elif 'technical_hvac' in space_type:
                        all_technical_hvac_spaces.append(space_id)

            # Determine technical space for meters (prefer electrical, fallback to hvac)
            meter_technical_spaces = all_technical_elec_spaces if all_technical_elec_spaces else all_technical_hvac_spaces

            # Fire Alarm Panel - one per building in first technical_elec space
            if all_technical_elec_spaces:
                tech_space = all_technical_elec_spaces[0]
                # Get floor_id from the space
                space_node = self._get_node(tech_space)
                floor_id = space_node.properties.get('floor_id') if space_node else None
                fire_panel = self._create_equipment('FireAlarmPanel', building_id, floor_id, tech_space)
                self.edges.append(Edge(fire_panel, tech_space, "LOCATED_IN"))
                self.edges.append(Edge(fire_panel, building_id, "SERVES"))
                self._fire_panels[building_id] = fire_panel

            # 0a. Transformer_HT_BT - One per building (before MainMeter)
            # Located in technical_elec space, feeds main meter
            transformer_id = None
            if all_technical_elec_spaces:
                tech_space = all_technical_elec_spaces[0]
                space_node = self._get_node(tech_space)
                floor_id = space_node.properties.get('floor_id') if space_node else None
                transformer_id = self._create_equipment('Transformer_HT_BT', building_id, floor_id, tech_space)
                self.edges.append(Edge(transformer_id, tech_space, "LOCATED_IN"))

            # 0b. Generator - One per building (backup power)
            # Located in technical_elec or basement, backs up main meter
            generator_id = None
            generator_space = None
            if all_technical_elec_spaces:
                generator_space = all_technical_elec_spaces[0]
            # Could also use basement if available - for now use technical_elec
            if generator_space:
                space_node = self._get_node(generator_space)
                floor_id = space_node.properties.get('floor_id') if space_node else None
                generator_id = self._create_equipment('Generator', building_id, floor_id, generator_space)
                self.edges.append(Edge(generator_id, generator_space, "LOCATED_IN"))

            # 1. Compteur principal
            main_meter_id = self._create_equipment(
                'MainMeter', building_id, None, None, is_meter=True
            )
            self._meters.append(main_meter_id)

            # MainMeter edges: LOCATED_IN technical space, SERVES building
            if meter_technical_spaces:
                self.edges.append(Edge(main_meter_id, meter_technical_spaces[0], "LOCATED_IN"))
            self.edges.append(Edge(main_meter_id, building_id, "SERVES"))

            # Connect Transformer to MainMeter (Transformer FEEDS MainMeter)
            if transformer_id:
                self.edges.append(Edge(transformer_id, main_meter_id, "FEEDS"))

            # Connect Generator as backup to MainMeter (Generator BACKS_UP MainMeter)
            if generator_id:
                self.edges.append(Edge(generator_id, main_meter_id, "BACKS_UP"))

            # 2. Sous-compteurs
            floors_list = list(self._floors[building_id])
            for i in range(self.profile.meters.get('electrical', {}).get('per_building', 3)):
                submeter_id = self._create_equipment(
                    'SubMeter', building_id, None, None, is_meter=True
                )
                self._submeters.append(submeter_id)
                self.edges.append(Edge(main_meter_id, submeter_id, "FEEDS"))

                # SubMeter edges: LOCATED_IN technical space, SERVES floor or building
                if meter_technical_spaces:
                    # Distribute submeters across available technical spaces
                    tech_space = meter_technical_spaces[i % len(meter_technical_spaces)]
                    self.edges.append(Edge(submeter_id, tech_space, "LOCATED_IN"))

                # SubMeter SERVES a floor (if available) or the building
                if floors_list:
                    served_floor = floors_list[i % len(floors_list)]
                    self.edges.append(Edge(submeter_id, served_floor, "SERVES"))
                else:
                    self.edges.append(Edge(submeter_id, building_id, "SERVES"))

            # 3. Équipements HVAC principaux
            ahu_ids = []
            for floor_id in self._floors[building_id]:
                # AHU par étage (si technical_hvac)
                spaces_on_floor = self._spaces[floor_id]
                technical_hvac_spaces = [s for s in spaces_on_floor
                                         if 'technical_hvac' in self._get_node(s).properties.get('space_type', '')]

                for tech_space in technical_hvac_spaces:
                    ahu_id = self._create_equipment('AHU', building_id, floor_id, tech_space)
                    ahu_ids.append(ahu_id)
                    # AHU localisé dans le local technique
                    self.edges.append(Edge(ahu_id, tech_space, "LOCATED_IN"))
                    # AHU alimenté par sous-compteur
                    if self._submeters:
                        self.edges.append(Edge(self.rng.choice(self._submeters), ahu_id, "FEEDS"))
                    self.edges.append(Edge(ahu_id, building_id, "SERVES"))

                    # Capteur température dans le local technique (pour Q4)
                    temp_sensor = self._create_equipment('TemperatureSensor', building_id, floor_id, tech_space)
                    self.edges.append(Edge(temp_sensor, tech_space, "LOCATED_IN"))
                    self.edges.append(Edge(temp_sensor, tech_space, "MONITORS"))

                # Équipements électriques dans technical_elec (TGBT, etc.)
                technical_elec_spaces = [s for s in spaces_on_floor
                                         if 'technical_elec' in self._get_node(s).properties.get('space_type', '')]
                for elec_space in technical_elec_spaces:
                    # Capteur température pour surveillance TGBT
                    temp_sensor = self._create_equipment('TemperatureSensor', building_id, floor_id, elec_space)
                    self.edges.append(Edge(temp_sensor, elec_space, "LOCATED_IN"))
                    self.edges.append(Edge(temp_sensor, elec_space, "MONITORS"))

            # ===== CENTRAL HVAC EQUIPMENT (Chiller, Boiler, CoolingTower) =====
            # Find basement and rooftop floors for placement
            basement_floor = None
            rooftop_floor = None
            basement_tech_space = None
            rooftop_tech_space = None

            for floor_id in self._floors[building_id]:
                floor_node = self._get_node(floor_id)
                if floor_node:
                    floor_type = floor_node.properties.get('floor_type', '')
                    level_index = floor_node.properties.get('level_index', 0)

                    # Find technical spaces on this floor
                    spaces_on_floor = self._spaces.get(floor_id, [])
                    tech_spaces = [s for s in spaces_on_floor
                                   if 'technical' in self._get_node(s).properties.get('space_type', '')]

                    if floor_type == 'basement' and tech_spaces:
                        basement_floor = floor_id
                        basement_tech_space = tech_spaces[0]
                    elif floor_type == 'rooftop' and tech_spaces:
                        rooftop_floor = floor_id
                        rooftop_tech_space = tech_spaces[0]
                    elif level_index == max(f.properties.get('level_index', 0)
                                            for f in [self._get_node(fid) for fid in self._floors[building_id]]
                                            if f) and tech_spaces:
                        # Use highest floor as rooftop if no explicit rooftop
                        if not rooftop_floor:
                            rooftop_floor = floor_id
                            rooftop_tech_space = tech_spaces[0]

            # Fallback: use first available technical space if basement not found
            if not basement_tech_space and all_technical_hvac_spaces:
                basement_tech_space = all_technical_hvac_spaces[0]
                space_node = self._get_node(basement_tech_space)
                basement_floor = space_node.properties.get('floor_id') if space_node else self._floors[building_id][0]

            # Chiller - One per building (in basement or rooftop technical space)
            if basement_tech_space:
                chiller = self._create_equipment('Chiller', building_id, basement_floor, basement_tech_space)
                self.edges.append(Edge(chiller, basement_tech_space, "LOCATED_IN"))
                self.edges.append(Edge(chiller, building_id, "SERVES"))
                # Chiller supplies AHUs
                for ahu_id in ahu_ids:
                    self.edges.append(Edge(chiller, ahu_id, "SUPPLIES"))
                # Fed by electrical
                if self._submeters:
                    self.edges.append(Edge(self.rng.choice(self._submeters), chiller, "FEEDS"))
                self._chillers.append(chiller)

            # Boiler - One per building (same location as chiller)
            if basement_tech_space:
                boiler = self._create_equipment('Boiler', building_id, basement_floor, basement_tech_space)
                self.edges.append(Edge(boiler, basement_tech_space, "LOCATED_IN"))
                self.edges.append(Edge(boiler, building_id, "SERVES"))
                # Boiler supplies AHUs
                for ahu_id in ahu_ids:
                    self.edges.append(Edge(boiler, ahu_id, "SUPPLIES"))
                self._boilers.append(boiler)

            # CoolingTower - One per building on rooftop
            if rooftop_tech_space:
                cooling_tower = self._create_equipment('CoolingTower', building_id, rooftop_floor, rooftop_tech_space)
                self.edges.append(Edge(cooling_tower, rooftop_tech_space, "LOCATED_IN"))
                # Cooling tower supplies chiller
                if self._chillers:
                    self.edges.append(Edge(cooling_tower, self._chillers[-1], "SUPPLIES"))

            # 4. VAV/FCU par espace (offices, meeting rooms)
            for floor_id in self._floors[building_id]:
                for space_id in self._spaces[floor_id]:
                    space_node = self._get_node(space_id)
                    space_type = space_node.properties.get('space_type', '')

                    # VAV ou FCU selon type d'espace
                    if 'office' in space_type or 'meeting' in space_type:
                        eq_type = 'VAV' if self.rng.random() > 0.3 else 'FCU'
                        eq_id = self._create_equipment(eq_type, building_id, floor_id, space_id)
                        self.edges.append(Edge(eq_id, space_id, "SERVES"))
                        self.edges.append(Edge(eq_id, space_id, "LOCATED_IN"))

                        # Alimenté par AHU
                        if ahu_ids:
                            self.edges.append(Edge(self.rng.choice(ahu_ids), eq_id, "FEEDS"))

                    # Capteurs de température
                    if 'office' in space_type or 'meeting' in space_type or 'lobby' in space_type:
                        sensor_id = self._create_equipment('TemperatureSensor', building_id, floor_id, space_id)
                        self.edges.append(Edge(sensor_id, space_id, "MONITORS"))
                        self.edges.append(Edge(sensor_id, space_id, "LOCATED_IN"))

                    # CO2 sensor - expanded to all offices and meeting rooms
                    if 'office' in space_type or 'meeting' in space_type:
                        co2_id = self._create_equipment('CO2_Sensor', building_id, floor_id, space_id)
                        self.edges.append(Edge(co2_id, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(co2_id, space_id, "MONITORS"))

                    # Occupancy sensor - for presence detection in occupied spaces
                    if any(x in space_type for x in ['office', 'meeting', 'corridor', 'lobby', 'restroom']):
                        occupancy = self._create_equipment('Occupancy_Sensor', building_id, floor_id, space_id)
                        self.edges.append(Edge(occupancy, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(occupancy, space_id, "MONITORS"))

                    # Humidity sensor - in offices and technical spaces
                    if 'office' in space_type or 'technical' in space_type:
                        humidity = self._create_equipment('Humidity_Sensor', building_id, floor_id, space_id)
                        self.edges.append(Edge(humidity, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(humidity, space_id, "MONITORS"))

                    # Water leak sensor - in technical spaces and restrooms
                    if 'technical' in space_type or 'restroom' in space_type:
                        water_leak = self._create_equipment('WaterLeakSensor', building_id, floor_id, space_id)
                        self.edges.append(Edge(water_leak, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(water_leak, space_id, "MONITORS"))

                    # Air quality sensor - in open spaces and lobbies
                    if 'open' in space_type or 'lobby' in space_type:
                        air_quality = self._create_equipment('AirQuality_Sensor', building_id, floor_id, space_id)
                        self.edges.append(Edge(air_quality, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(air_quality, space_id, "MONITORS"))

                    # Sécurité
                    if 'lobby' in space_type or 'entry' in space_type:
                        badge_id = self._create_equipment('BadgeReader', building_id, floor_id, space_id)
                        self.edges.append(Edge(badge_id, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(badge_id, space_id, "SECURES"))
                        self.edges.append(Edge(badge_id, space_id, "GRANTS_ACCESS"))

                        cam_id = self._create_equipment('IPCamera', building_id, floor_id, space_id)
                        self.edges.append(Edge(cam_id, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(cam_id, space_id, "MONITORS"))

                    # IT dans server_room
                    if 'server' in space_type or 'technical_it' in space_type:
                        ups_id = self._create_equipment('UPS', building_id, floor_id, space_id)
                        self.edges.append(Edge(ups_id, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(main_meter_id, ups_id, "FEEDS"))

                        # PDU - Power Distribution Unit, in server_room, fed by UPS
                        pdu_id = self._create_equipment('PDU', building_id, floor_id, space_id)
                        self.edges.append(Edge(pdu_id, space_id, "LOCATED_IN"))
                        # UPS feeds PDU
                        self.edges.append(Edge(ups_id, pdu_id, "FEEDS"))

                        # Create servers - PDU feeds servers (instead of UPS directly)
                        server_ids = []
                        for _ in range(self.rng.randint(2, 5)):
                            server_id = self._create_equipment('RackServer', building_id, floor_id, space_id)
                            self.edges.append(Edge(server_id, space_id, "LOCATED_IN"))
                            server_ids.append(server_id)

                        # PDU feeds servers
                        for server_id in server_ids:
                            self.edges.append(Edge(pdu_id, server_id, "FEEDS"))

                        switch_id = self._create_equipment('NetworkSwitch', building_id, floor_id, space_id)
                        self.edges.append(Edge(switch_id, space_id, "LOCATED_IN"))
                        # PDU also feeds network switch
                        self.edges.append(Edge(pdu_id, switch_id, "FEEDS"))

                        # Capteur température pour datacenter
                        temp_sensor = self._create_equipment('TemperatureSensor', building_id, floor_id, space_id)
                        self.edges.append(Edge(temp_sensor, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(temp_sensor, space_id, "MONITORS"))

                        # CRAC - Computer Room AC in server_room or technical_it spaces
                        crac = self._create_equipment('CRAC', building_id, floor_id, space_id)
                        self.edges.append(Edge(crac, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(crac, space_id, "SERVES"))
                        # CRAC supplied by chiller
                        if self._chillers:
                            self.edges.append(Edge(self._chillers[-1], crac, "SUPPLIES"))

                    # ===== FIRE SAFETY EQUIPMENT =====

                    # SmokeDetector - in every space except parking
                    if 'parking' not in space_type:
                        smoke_detector = self._create_equipment('SmokeDetector', building_id, floor_id, space_id)
                        self.edges.append(Edge(smoke_detector, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(smoke_detector, space_id, "MONITORS"))
                        # Connected to fire panel
                        if building_id in self._fire_panels:
                            self.edges.append(Edge(self._fire_panels[building_id], smoke_detector, "MONITORS"))

                    # ManualCallPoint - in corridors and near exits
                    if 'corridor' in space_type:
                        mcp = self._create_equipment('ManualCallPoint', building_id, floor_id, space_id)
                        self.edges.append(Edge(mcp, space_id, "LOCATED_IN"))
                        # Connected to fire panel
                        if building_id in self._fire_panels:
                            self.edges.append(Edge(mcp, self._fire_panels[building_id], "TRIGGERS"))

                    # Sprinkler - in offices, meeting rooms, storage
                    if 'office' in space_type or 'meeting' in space_type or 'storage' in space_type:
                        sprinkler = self._create_equipment('Sprinkler', building_id, floor_id, space_id)
                        self.edges.append(Edge(sprinkler, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(sprinkler, space_id, "SERVES"))

                    # FireExtinguisher - in corridors and technical spaces
                    if 'corridor' in space_type or 'technical' in space_type:
                        fire_ext = self._create_equipment('FireExtinguisher', building_id, floor_id, space_id)
                        self.edges.append(Edge(fire_ext, space_id, "LOCATED_IN"))

            # 6. Lighting equipment
            # DALI Gateway - one per floor in a technical space
            for floor_id in self._floors[building_id]:
                spaces_on_floor = self._spaces[floor_id]
                # Prefer technical_elec, fallback to technical_hvac
                technical_spaces = [s for s in spaces_on_floor
                                    if 'technical_elec' in self._get_node(s).properties.get('space_type', '')]
                if not technical_spaces:
                    technical_spaces = [s for s in spaces_on_floor
                                        if 'technical_hvac' in self._get_node(s).properties.get('space_type', '')]

                if technical_spaces:
                    tech_space = technical_spaces[0]
                    dali_gw = self._create_equipment('DALI_Gateway', building_id, floor_id, tech_space)
                    self.edges.append(Edge(dali_gw, tech_space, "LOCATED_IN"))
                    # Connect to submeter
                    if self._submeters:
                        self.edges.append(Edge(self.rng.choice(self._submeters), dali_gw, "FEEDS"))
                    self._dali_gateways[floor_id] = dali_gw

            # LED Drivers and Emergency Lighting per space
            for floor_id in self._floors[building_id]:
                dali_gw = self._dali_gateways.get(floor_id)

                for space_id in self._spaces[floor_id]:
                    space_node = self._get_node(space_id)
                    space_type = space_node.properties.get('space_type', '')

                    # LED_Driver_DALI2 - in office and meeting spaces
                    if 'office' in space_type or 'meeting' in space_type:
                        led_driver = self._create_equipment('LED_Driver_DALI2', building_id, floor_id, space_id)
                        self.edges.append(Edge(led_driver, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(led_driver, space_id, "SERVES"))
                        # Connected to DALI gateway
                        if dali_gw:
                            self.edges.append(Edge(dali_gw, led_driver, "CONTROLS"))

                    # Emergency_Lighting - in corridors and stairwells
                    if 'corridor' in space_type or 'stairwell' in space_type:
                        emergency_light = self._create_equipment('Emergency_Lighting', building_id, floor_id, space_id)
                        self.edges.append(Edge(emergency_light, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(emergency_light, space_id, "SERVES"))

            # 7. Parking equipment (typically in basement)
            # Track parking sensors per floor for controller assignment
            parking_sensors_by_floor: Dict[str, List[str]] = {}
            parking_spaces_per_floor: Dict[str, List[str]] = {}

            # First pass: identify parking spaces per floor
            for floor_id in self._floors[building_id]:
                parking_spaces_per_floor[floor_id] = []
                parking_sensors_by_floor[floor_id] = []
                for space_id in self._spaces[floor_id]:
                    space_node = self._get_node(space_id)
                    space_type = space_node.properties.get('space_type', '')
                    if 'parking' in space_type:
                        parking_spaces_per_floor[floor_id].append(space_id)

            # Second pass: create parking equipment
            for floor_id in self._floors[building_id]:
                parking_spaces = parking_spaces_per_floor[floor_id]
                if not parking_spaces:
                    continue

                first_parking_space = True
                for space_id in parking_spaces:
                    # BarrierGate - At parking entry/exit (only at first parking space per floor)
                    if first_parking_space:
                        # Create 1-2 barriers per parking area
                        num_barriers = self.rng.randint(1, 2)
                        for _ in range(num_barriers):
                            barrier = self._create_equipment('BarrierGate', building_id, floor_id, space_id)
                            self.edges.append(Edge(barrier, space_id, "LOCATED_IN"))
                            self.edges.append(Edge(barrier, space_id, "CONTROLS"))  # Controls access
                        first_parking_space = False

                    # ParkingSensorMagnetic - Multiple per parking space (2-5 sensors representing spots)
                    num_sensors = self.rng.randint(2, 5)
                    for _ in range(num_sensors):
                        sensor = self._create_equipment('ParkingSensorMagnetic', building_id, floor_id, space_id)
                        self.edges.append(Edge(sensor, space_id, "LOCATED_IN"))
                        self.edges.append(Edge(sensor, space_id, "MONITORS"))
                        parking_sensors_by_floor[floor_id].append(sensor)

                    # EVChargerLevel2 - 1-2 per parking area (only at first space to avoid duplication)
                    if space_id == parking_spaces[0]:
                        num_chargers = self.rng.randint(1, 2)
                        for _ in range(num_chargers):
                            charger = self._create_equipment('EVChargerLevel2', building_id, floor_id, space_id)
                            self.edges.append(Edge(charger, space_id, "LOCATED_IN"))
                            self.edges.append(Edge(charger, space_id, "SERVES"))
                            # Fed by electrical
                            if self._submeters:
                                self.edges.append(Edge(self.rng.choice(self._submeters), charger, "FEEDS"))

                    # IPCamera - For parking security
                    cam = self._create_equipment('IPCamera', building_id, floor_id, space_id)
                    self.edges.append(Edge(cam, space_id, "LOCATED_IN"))
                    self.edges.append(Edge(cam, space_id, "MONITORS"))

                # ParkingGuidanceController - One per parking floor (after all sensors are created)
                if parking_sensors_by_floor[floor_id]:
                    # Place controller in first parking space
                    controller_space = parking_spaces[0]
                    controller = self._create_equipment('ParkingGuidanceController', building_id, floor_id, controller_space)
                    self.edges.append(Edge(controller, controller_space, "LOCATED_IN"))
                    # Controller monitors all sensors on this floor
                    for sensor_id in parking_sensors_by_floor[floor_id]:
                        self.edges.append(Edge(controller, sensor_id, "CONTROLS"))

    def _create_equipment(self, equipment_type: str, building_id: str,
                          floor_id: str = None, space_id: str = None,
                          is_meter: bool = False) -> str:
        """Crée un équipement avec ses points"""

        # Charger la config
        config = self.equipment_registry.get(equipment_type)
        if not config:
            # Config par défaut si pas trouvée
            config = EquipmentConfig(
                code=equipment_type[:3].upper(),
                domain='BMS',
                haystack=equipment_type.lower(),
                brick=equipment_type,
                protocols=['bacnet'],
                points=[]
            )

        # ID unique
        eq_count = len([n for n in self.nodes if n.type == 'Equipment']) + 1
        eq_id = f"eq_{equipment_type.lower()}_{eq_count}"

        # Propriétés de base
        properties = {
            'equipment_type': equipment_type,
            'domain': config.domain,
            'building_id': building_id,
        }
        if floor_id:
            properties['floor_id'] = floor_id
        if space_id:
            properties['space_id'] = space_id

        # Q29: critical property for essential infrastructure equipment
        critical_types = ['Transformer_HT_BT', 'Generator', 'FireAlarmPanel', 'MainMeter', 'UPS']
        if equipment_type in critical_types:
            properties['critical'] = True

        # Génération JSONB
        protocol = self.protocol_gen.generate_for_equipment(config)
        metadata = self.metadata_gen.generate(config)
        capabilities = self.capabilities_gen.generate_capabilities(equipment_type)
        tags = self.capabilities_gen.generate_tags(equipment_type, config)

        # Créer le nœud
        self._add_node(Node(
            id=eq_id,
            type="Equipment",
            name=f"{equipment_type} {eq_count}",
            properties=properties,
            capabilities=capabilities,
            metadata=metadata,
            tags=tags,
            protocol=protocol
        ))

        # Indexer
        self._equipment_by_building.setdefault(building_id, []).append(eq_id)
        if space_id:
            self._equipment_by_space.setdefault(space_id, []).append(eq_id)
        self._points_by_equipment[eq_id] = []

        # Créer les points
        self._create_points_for_equipment(eq_id, config, building_id)

        return eq_id

    def _create_points_for_equipment(self, equipment_id: str, config: EquipmentConfig, building_id: str):
        """Crée les points de mesure pour un équipement"""

        # Utiliser les points définis dans la config, ou un sous-ensemble
        points_config = config.points

        # Limiter le nombre de points pour les gros équipements
        max_points = min(len(points_config), 10) if points_config else 3
        selected_points = points_config[:max_points] if points_config else []

        # Points par défaut si aucun défini
        if not selected_points:
            selected_points = [
                {'id': 'value', 'type': 'mesure', 'unit': '-', 'quantity': 'status'},
                {'id': 'status', 'type': 'etat', 'values': ['ok', 'fault']},
                {'id': 'fault', 'type': 'alarme'}
            ]

        for point_config in selected_points:
            point_count = len(self.nodes) + 1
            point_id = f"point_{equipment_id}_{point_config.get('id', 'value')}"

            # Éviter les doublons (O(1) via index)
            if point_id in self._node_index:
                point_id = f"{point_id}_{point_count}"

            quantity = point_config.get('quantity', 'status')
            unit = point_config.get('unit', '-')
            point_type = point_config.get('type', 'mesure')

            # Générer protocol pour le point (BACnet avec même device_id que l'équipement parent)
            eq_node = self._get_node(equipment_id)
            point_protocol = {}
            if eq_node and eq_node.protocol.get('type') == 'BACnet':
                point_protocol = {
                    'type': 'BACnet',
                    'device_id': eq_node.protocol.get('device_id'),
                    'object_type': 'analogInput' if point_type == 'mesure' else 'binaryInput',
                    'object_instance': len(self._points_by_equipment.get(equipment_id, [])) + 1
                }

            # Calibration et range
            calibration = self.calibration_gen.generate(point_type, quantity)
            range_info = self.range_gen.generate(quantity)

            self._add_node(Node(
                id=point_id,
                type="Point",
                name=f"{point_config.get('desc', quantity)} - {equipment_id}",
                properties={
                    'quantity': quantity,
                    'unit': unit,
                    'equipment_id': equipment_id,
                    'building_id': building_id,
                    'frequency': point_config.get('freq', 'normal')
                },
                protocol=point_protocol,
                calibration=calibration,
                range_info=range_info
            ))

            self.edges.append(Edge(equipment_id, point_id, "HAS_POINT"))
            self._points_by_equipment.setdefault(equipment_id, []).append(point_id)

    def _generate_tenants(self):
        """Génère les locataires"""
        for t in range(1, self.profile.tenants + 1):
            tenant_id = f"tenant_{t}"

            self._add_node(Node(
                id=tenant_id,
                type="Tenant",
                name=f"Locataire {t} SARL",
                properties={
                    'contract_start': (self.reference_date - timedelta(days=self.rng.randint(365, 1825))).strftime('%Y-%m-%d'),
                    'contract_end': (self.reference_date + timedelta(days=self.rng.randint(365, 1825))).strftime('%Y-%m-%d')
                }
            ))

            # Associer à des espaces
            if self._buildings:
                building = self.rng.choice(self._buildings)
                floors = self._floors.get(building, [])
                if floors:
                    floor = self.rng.choice(floors)
                    spaces = self._spaces.get(floor, [])
                    # Occuper 1-3 espaces
                    for space_id in self.rng.sample(spaces, min(3, len(spaces))):
                        self.edges.append(Edge(tenant_id, space_id, "OCCUPIES"))

            # Associer un sous-compteur
            if self._submeters:
                submeter = self.rng.choice(self._submeters)
                self.edges.append(Edge(submeter, tenant_id, "METERS_TENANT"))

    def _generate_schedules_and_leases(self):
        """Generate Schedule and Lease nodes for buildings and tenants."""

        # Track schedules by building for equipment linkage
        schedules: Dict[str, Dict[str, str]] = {}  # building_id -> {schedule_type: schedule_id}

        # 1. Schedule nodes - For building operations
        schedule_types = ['occupancy', 'hvac', 'lighting', 'access']
        for building_id in self._buildings:
            schedules[building_id] = {}
            for stype in schedule_types:
                schedule_id = f"schedule_{building_id}_{stype}"
                self._add_node(Node(
                    id=schedule_id,
                    type="Schedule",
                    name=f"Schedule {stype.title()} - {building_id}",
                    properties={
                        'schedule_type': stype,
                        'timezone': 'Europe/Paris',
                        'entries': [
                            {'day': 'weekday', 'start': '07:00', 'end': '19:00', 'mode': 'occupied'},
                            {'day': 'weekend', 'start': '09:00', 'end': '14:00', 'mode': 'reduced'}
                        ]
                    }
                ))
                # Building follows schedule
                self.edges.append(Edge(building_id, schedule_id, "HAS_SCHEDULE"))
                schedules[building_id][stype] = schedule_id

        # 2. Lease nodes - For tenant contracts
        tenant_ids = [n.id for n in self.nodes if n.type == "Tenant"]
        for tenant_id in tenant_ids:
            tenant_node = self._get_node(tenant_id)
            lease_id = f"lease_{tenant_id}"
            self._add_node(Node(
                id=lease_id,
                type="Lease",
                name=f"Bail {tenant_node.name}",
                properties={
                    'start_date': tenant_node.properties.get('contract_start'),
                    'end_date': tenant_node.properties.get('contract_end'),
                    'rent_per_m2': round(self.rng.uniform(200, 500), 2),
                    'charges_per_m2': round(self.rng.uniform(50, 100), 2),
                    'deposit_months': self.rng.randint(2, 6)
                }
            ))
            # Tenant has lease
            self.edges.append(Edge(tenant_id, lease_id, "HAS_LEASE"))

            # Lease covers spaces (from tenant OCCUPIES edges)
            for edge in self.edges:
                if edge.source_id == tenant_id and edge.rel_type == "OCCUPIES":
                    self.edges.append(Edge(lease_id, edge.target_id, "COVERS"))

        # 3. Equipment follows schedules
        # Collect HVAC and Lighting equipment by building
        hvac_types = {'AHU', 'VAV', 'FCU', 'Chiller', 'Boiler', 'HeatPump', 'CoolingTower', 'RTU'}
        lighting_types = {'LED_Driver_DALI2', 'DALI_Gateway', 'Emergency_Lighting'}

        for node in self.nodes:
            if node.type != "Equipment":
                continue

            eq_type = node.properties.get('equipment_type', '')
            building_id = node.properties.get('building_id')

            if not building_id or building_id not in schedules:
                continue

            # HVAC equipment follows hvac schedule
            if eq_type in hvac_types:
                if 'hvac' in schedules[building_id]:
                    self.edges.append(Edge(node.id, schedules[building_id]['hvac'], "FOLLOWS"))

            # Lighting follows lighting schedule
            if eq_type in lighting_types:
                if 'lighting' in schedules[building_id]:
                    self.edges.append(Edge(node.id, schedules[building_id]['lighting'], "FOLLOWS"))

    def _generate_zones(self):
        """Génère les zones logiques"""
        zone_types = ['thermal', 'security', 'fire']

        for building_id in self._buildings:
            for zone_type in zone_types:
                zone_id = f"zone_{building_id}_{zone_type}"

                self._add_node(Node(
                    id=zone_id,
                    type="Zone",
                    name=f"Zone {zone_type.title()} - {building_id}",
                    properties={
                        'zone_type': zone_type,
                        'description': f"Zone {zone_type} du bâtiment"
                    }
                ))

                # Associer des équipements à la zone
                equipments = self._equipment_by_building.get(building_id, [])
                for eq_id in self.rng.sample(equipments, min(5, len(equipments))):
                    self.edges.append(Edge(eq_id, zone_id, "MEMBER_OF"))

    def _generate_additional_relations(self):
        """Génère des relations supplémentaires"""
        # Contrats de maintenance
        contract_id = "contract_maintenance_1"
        self._add_node(Node(
            id=contract_id,
            type="Contract",
            name="Contrat Maintenance CVC",
            properties={
                'contract_type': 'maintenance',
                'start_date': (self.reference_date - timedelta(days=365)).strftime('%Y-%m-%d'),
                'end_date': (self.reference_date + timedelta(days=730)).strftime('%Y-%m-%d'),
                'provider': 'MaintenancePro SARL'
            }
        ))

        # Couvrir les AHU
        for eq_id in [n.id for n in self.nodes
                      if n.type == 'Equipment' and n.properties.get('equipment_type') == 'AHU']:
            self.edges.append(Edge(eq_id, contract_id, "COVERED_BY"))

    def _generate_maintenance_entities(self):
        """Generate maintenance management entities: Technicians, WorkOrders, Alarms"""

        # Predefined lists for random selection
        technician_names = [
            'John Smith', 'Maria Garcia', 'David Chen', 'Sarah Johnson', 'Michael Brown',
            'Emily Davis', 'James Wilson', 'Anna Martinez', 'Robert Taylor', 'Lisa Anderson',
            'William Thomas', 'Jennifer White', 'Charles Harris', 'Patricia Martin', 'Daniel Lee'
        ]
        companies = ['Internal', 'MaintenancePro', 'HVACService', 'ElecService']
        specialties_pool = ['HVAC', 'Electrical', 'Security', 'IT', 'Fire', 'BMS']
        certifications_pool = ['HVAC-R', 'Electrical License', 'Fire Safety', 'OSHA']
        workorder_types = ['preventive', 'corrective', 'inspection']
        workorder_statuses = ['open', 'in_progress', 'completed', 'on_hold']
        workorder_priorities = ['low', 'medium', 'high', 'critical']
        alarm_severities = ['info', 'warning', 'critical']
        alarm_triggers = [
            ('High temperature', 'temperature'),
            ('Low pressure', 'pressure'),
            ('Communication failure', 'comm'),
            ('Power fluctuation', 'power'),
            ('Sensor fault', 'sensor'),
            ('Filter clogged', 'filter'),
            ('Humidity out of range', 'humidity'),
            ('CO2 level exceeded', 'co2'),
            ('Fan failure', 'fan'),
            ('Valve stuck', 'valve')
        ]

        technician_counter = 0
        workorder_counter = 0
        alarm_counter = 0

        for building_id in self._buildings:
            # Get all equipment for this building
            building_equipment = self._equipment_by_building.get(building_id, [])
            if not building_equipment:
                continue

            # 1. Generate Technicians (3-5 per building)
            num_technicians = self.rng.randint(3, 5)
            building_technicians = []

            for t in range(num_technicians):
                technician_counter += 1
                tech_id = f"technician_{technician_counter}"
                name = self.rng.choice(technician_names)

                # Random specialties (1-3)
                num_specialties = self.rng.randint(1, 3)
                specialties = self.rng.sample(specialties_pool, num_specialties)

                # Random certifications (0-2)
                num_certs = self.rng.randint(0, 2)
                certifications = self.rng.sample(certifications_pool, num_certs) if num_certs > 0 else []

                self._add_node(Node(
                    id=tech_id,
                    type="Technician",
                    name=f"Tech {name}",
                    properties={
                        'company': self.rng.choice(companies),
                        'specialties': specialties,
                        'certifications': certifications
                    }
                ))

                building_technicians.append(tech_id)
                self._technicians.append(tech_id)

            # 2. Generate WorkOrders (10-20 per building)
            num_workorders = self.rng.randint(10, 20)

            for w in range(num_workorders):
                workorder_counter += 1
                wo_id = f"workorder_{workorder_counter}"
                wo_type = self.rng.choice(workorder_types)
                wo_status = self.rng.choice(workorder_statuses)
                wo_priority = self.rng.choice(workorder_priorities)

                # Select a random equipment for this work order
                target_equipment_id = self.rng.choice(building_equipment)
                target_equipment = self._get_node(target_equipment_id)
                equipment_type = target_equipment.properties.get('equipment_type', 'Equipment') if target_equipment else 'Equipment'

                # Generate dates
                created_days_ago = self.rng.randint(1, 180)
                created_at = self.reference_date - timedelta(days=created_days_ago)
                due_days_after_created = self.rng.randint(1, 30)
                due_date = created_at + timedelta(days=due_days_after_created)

                # Completed date only if status is 'completed'
                completed_at = None
                if wo_status == 'completed':
                    completed_days_after_created = self.rng.randint(1, due_days_after_created)
                    completed_at = created_at + timedelta(days=completed_days_after_created)

                self._add_node(Node(
                    id=wo_id,
                    type="WorkOrder",
                    name=f"WO-{workorder_counter:04d}",
                    properties={
                        'title': f"{wo_type.title()} - {equipment_type}",
                        'status': wo_status,
                        'priority': wo_priority,
                        'type': wo_type,
                        'created_at': created_at.strftime('%Y-%m-%d'),
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'completed_at': completed_at.strftime('%Y-%m-%d') if completed_at else None
                    }
                ))

                # WorkOrder ASSIGNED_TO Technician
                assigned_tech = self.rng.choice(building_technicians)
                self.edges.append(Edge(wo_id, assigned_tech, "ASSIGNED_TO"))

                # WorkOrder CONCERNS Equipment
                self.edges.append(Edge(wo_id, target_equipment_id, "CONCERNS"))

            # 3. Generate Alarms (5-15 per building, mix of active and historical)
            num_alarms = self.rng.randint(5, 15)

            for a in range(num_alarms):
                alarm_counter += 1
                alarm_id = f"alarm_{alarm_counter}"
                severity = self.rng.choice(alarm_severities)
                trigger_msg, trigger_type = self.rng.choice(alarm_triggers)

                # Select a random equipment that triggered the alarm
                trigger_equipment_id = self.rng.choice(building_equipment)
                trigger_equipment = self._get_node(trigger_equipment_id)
                equipment_name = trigger_equipment.name if trigger_equipment else 'Unknown'

                # Generate message based on trigger type
                message = f"{trigger_msg} detected on {equipment_name}"

                # Generate timestamps
                triggered_days_ago = self.rng.randint(0, 90)
                triggered_at = self.reference_date - timedelta(days=triggered_days_ago)

                # Determine if alarm is active or resolved
                is_active = self.rng.random() < 0.3  # 30% chance of being active

                acknowledged_at = None
                resolved_at = None

                if not is_active or self.rng.random() < 0.7:  # 70% of alarms are acknowledged
                    ack_hours_after = self.rng.randint(1, 48)
                    acknowledged_at = triggered_at + timedelta(hours=ack_hours_after)

                if not is_active:
                    # Resolved alarms have a resolution time
                    resolve_hours_after_ack = self.rng.randint(1, 72)
                    if acknowledged_at:
                        resolved_at = acknowledged_at + timedelta(hours=resolve_hours_after_ack)
                    else:
                        resolved_at = triggered_at + timedelta(hours=resolve_hours_after_ack)

                self._add_node(Node(
                    id=alarm_id,
                    type="Alarm",
                    name=f"ALM-{alarm_counter:04d}",
                    properties={
                        'severity': severity,
                        'message': message,
                        'triggered_at': triggered_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'acknowledged_at': acknowledged_at.strftime('%Y-%m-%d %H:%M:%S') if acknowledged_at else None,
                        'resolved_at': resolved_at.strftime('%Y-%m-%d %H:%M:%S') if resolved_at else None,
                        'active': is_active
                    }
                ))

                # Alarm TRIGGERED_BY Equipment
                self.edges.append(Edge(alarm_id, trigger_equipment_id, "TRIGGERED_BY"))

                # Alarm ACKNOWLEDGED_BY Technician (if acknowledged)
                if acknowledged_at:
                    ack_tech = self.rng.choice(building_technicians)
                    self.edges.append(Edge(alarm_id, ack_tech, "ACKNOWLEDGED_BY"))

    def _generate_orphan(self):
        """Génère un équipement orphelin (sans relations) pour Q5"""
        orphan_id = "orphan_1"

        self._add_node(Node(
            id=orphan_id,
            type="Equipment",
            name="Orphan Sensor",
            properties={
                'equipment_type': 'TemperatureSensor',
                'domain': 'BMS',
                'building_id': self._buildings[0] if self._buildings else 'building_1'
            }
        ))
        # PAS d'edges pour cet équipement

    def _generate_timeseries(self):
        """Génère les données timeseries pour TOUS les points mesurables.

        Chaque point avec une quantity mesurable reçoit des timeseries selon
        sa fréquence définie. Cela garantit un dataset cohérent où toutes les
        queries timeseries (Q6-Q13, Q31) fonctionnent correctement.

        La taille du dataset est contrôlée par:
        - La durée (2d, 1w, 1m, 6m, 1y)
        - Le profil (small, medium, large) qui détermine le nombre de points
        """
        # Quantities qui génèrent des timeseries continues
        measurable_quantities = [
            'temperature', 'humidity', 'co2', 'power', 'energy',
            'flow', 'pressure', 'concentration', 'position',
            'speed', 'level', 'current', 'voltage', 'power_factor',
            'active_power', 'reactive_power', 'setpoint', 'count'
        ]

        # Frequencies supportées (event = discret)
        valid_frequencies = {'energy', 'slow', 'normal', 'fast', 'event', 'daily'}

        # Collecter TOUS les points mesurables
        points_by_freq = {f: [] for f in valid_frequencies}

        for n in self.nodes:
            if n.type == 'Point':
                quantity = n.properties.get('quantity', '')
                freq = n.properties.get('frequency', 'normal')

                # Points avec quantity mesurable → timeseries régulières
                if quantity in measurable_quantities:
                    target_freq = freq if freq in valid_frequencies else 'normal'
                    points_by_freq[target_freq].append(n)
                # Points event (status, alarm, fault) → timeseries discrètes
                elif freq == 'event':
                    points_by_freq['event'].append(n)

        # Calculer rows par point selon frequency
        duration_sec = self.duration_hours * 3600
        days = self.duration_hours / 24

        def rows_for_freq(freq, quantity=''):
            step = self.FREQUENCY_STEP_SECONDS.get(freq, 300)
            if step == 0:  # event - selon profil
                if 'status' in quantity:
                    rate = self.EVENT_PROFILES['status']
                elif 'alarm' in quantity:
                    rate = self.EVENT_PROFILES['alarm']
                elif 'fault' in quantity:
                    rate = self.EVENT_PROFILES['fault']
                else:
                    rate = self.EVENT_PROFILES['default']
                return max(1, int(rate * days))
            return duration_sec // step

        # Sélectionner TOUS les points (pas de limite)
        selected = []
        rows_estimate = 0

        for freq in valid_frequencies:
            for point in points_by_freq[freq]:
                quantity = point.properties.get('quantity', '')
                rows = rows_for_freq(freq, quantity)
                selected.append((point, freq, rows))
                rows_estimate += rows

        # Log breakdown
        breakdown = {}
        points_breakdown = {}
        for _, freq, rows in selected:
            breakdown[freq] = breakdown.get(freq, 0) + rows
            points_breakdown[freq] = points_breakdown.get(freq, 0) + 1

        print(f"Timeseries: {len(selected)} points, {rows_estimate:,} rows estimated")
        print(f"  Points by freq: {points_breakdown}")
        print(f"  Rows by freq: {breakdown}")

        # Générer les données
        base_time = self.reference_date
        end_time = base_time + timedelta(hours=self.duration_hours)

        for point, freq, _ in selected:
            quantity = point.properties.get('quantity', 'status')
            step_sec = self.FREQUENCY_STEP_SECONDS.get(freq, 300)

            if step_sec == 0:  # event: timestamps aléatoires
                self._generate_event_timeseries(point, base_time, end_time)
            else:  # régulier
                current = base_time
                while current < end_time:
                    value = self._generate_value(quantity, current.hour)
                    self.timeseries.append(TimeseriesPoint(
                        point_id=point.id,
                        timestamp=current,
                        value=value
                    ))
                    current += timedelta(seconds=step_sec)

        # Sanity check final
        print(f"  Actual rows: {len(self.timeseries)}")

    def _generate_event_timeseries(self, point, start: datetime, end: datetime):
        """Génère des événements discrets selon profil quantity"""
        quantity = point.properties.get('quantity', '')
        days = max(1, (end - start).total_seconds() / 86400)

        # Déterminer profil selon quantity
        if 'status' in quantity:
            events_per_day = self.EVENT_PROFILES['status']
        elif 'alarm' in quantity:
            events_per_day = self.EVENT_PROFILES['alarm']
        elif 'fault' in quantity:
            events_per_day = self.EVENT_PROFILES['fault']
        else:
            events_per_day = self.EVENT_PROFILES['default']

        # Garantir au moins 1 événement
        n_events = max(1, int(events_per_day * days))

        # Générer timestamps aléatoires sur toute la période
        total_seconds = int((end - start).total_seconds())
        for _ in range(n_events):
            offset = self.rng.randint(0, total_seconds)
            ts = start + timedelta(seconds=offset)
            self.timeseries.append(TimeseriesPoint(
                point_id=point.id,
                timestamp=ts,
                value=float(self.rng.randint(0, 1))
            ))

    def _generate_value(self, quantity: str, hour: int) -> float:
        """Génère une valeur réaliste selon la quantity et l'heure"""
        if quantity == 'temperature':
            # Température: 18-24°C avec variation journalière
            base = 21 + 3 * math.sin((hour - 6) * math.pi / 12)
            return round(base + self.rng.uniform(-0.5, 0.5), 1)

        elif quantity == 'humidity':
            return round(45 + 10 * math.sin(hour * math.pi / 12) + self.rng.uniform(-5, 5), 1)

        elif quantity == 'co2':
            # CO2: plus élevé pendant heures de bureau
            if 8 <= hour <= 18:
                return round(600 + 200 * math.sin((hour - 8) * math.pi / 10) + self.rng.uniform(-50, 50))
            return round(400 + self.rng.uniform(-20, 20))

        elif quantity == 'power':
            # Puissance: pics le matin et l'après-midi
            if 8 <= hour <= 18:
                return round(50 + 30 * abs(math.sin((hour - 8) * math.pi / 5)) + self.rng.uniform(-5, 5), 1)
            return round(10 + self.rng.uniform(-2, 2), 1)

        elif quantity == 'energy':
            # Énergie: cumulative
            return round(hour * 5 + self.rng.uniform(0, 2), 1)

        elif quantity == 'flow':
            return round(1000 + 500 * math.sin(hour * math.pi / 12) + self.rng.uniform(-100, 100))

        elif quantity == 'pressure':
            return round(100 + self.rng.uniform(-5, 5))

        else:
            return round(self.rng.uniform(0, 100), 1)

    def _get_node(self, node_id: str) -> Optional[Node]:
        """Récupère un nœud par ID (O(1) via index)"""
        return self._node_index.get(node_id)

    # =========================================================================
    # QUERY PARAMS GENERATION
    # =========================================================================

    def _generate_query_params(self) -> Dict[str, Any]:
        """Extract guaranteed-valid IDs from generated dataset for queries."""
        params: Dict[str, Any] = {}

        # 1. Building with complete hierarchy (floors → spaces → equipment)
        for building_id in self._buildings:
            floors = self._floors.get(building_id, [])
            if not floors:
                continue
            has_offices = False
            for floor_id in floors:
                spaces = self._spaces.get(floor_id, [])
                for space_id in spaces:
                    space_node = self._get_node(space_id)
                    if space_node and 'office' in space_node.properties.get('space_type', ''):
                        has_offices = True
                        break
                if has_offices:
                    break
            if has_offices:
                params["building_id"] = building_id
                params["building_with_offices_id"] = building_id
                break

        # Fallback if no building with offices found
        if "building_id" not in params and self._buildings:
            params["building_id"] = self._buildings[0]

        # 2. Floor with temperature sensors (for Q4)
        # Find a floor that has equipment with temp points via LOCATED_IN
        floor_with_temp = None
        for building_id, floors in self._floors.items():
            for floor_id in floors:
                spaces = self._spaces.get(floor_id, [])
                for space_id in spaces:
                    # Check if any equipment is LOCATED_IN this space
                    for edge in self.edges:
                        if edge.rel_type == "LOCATED_IN" and edge.target_id == space_id:
                            eq_id = edge.source_id
                            # Check if equipment has temp points
                            for e2 in self.edges:
                                if e2.source_id == eq_id and e2.rel_type == "HAS_POINT":
                                    point = self._get_node(e2.target_id)
                                    if point and "temp" in point.name.lower():
                                        floor_with_temp = floor_id
                                        break
                            if floor_with_temp:
                                break
                    if floor_with_temp:
                        break
                if floor_with_temp:
                    break
            if floor_with_temp:
                break

        # Fallback to first floor if no floor with temp found
        if floor_with_temp:
            params["floor_id"] = floor_with_temp
        else:
            for building_id, floors in self._floors.items():
                if floors:
                    params["floor_id"] = floors[0]
                    break

        # 3. Space with SERVES relationship (for Q3 - equipment serving a space)
        # Prioritize SERVES since Q3 specifically queries SERVES relationships
        space_with_serves = None
        space_with_any = None
        for edge in self.edges:
            target = self._get_node(edge.target_id)
            if target and target.type == "Space":
                if edge.rel_type == "SERVES":
                    space_with_serves = edge.target_id
                    break
                elif space_with_any is None and edge.rel_type in {"MONITORS", "LOCATED_IN"}:
                    space_with_any = edge.target_id
        params["space_id"] = space_with_serves or space_with_any

        # 4. Equipment in FEEDS chain (prefer middle of chain)
        # Q22 (Equipment Siblings) needs equipment that has a FEEDS parent
        feeds_sources = {e.source_id for e in self.edges if e.rel_type == "FEEDS"}
        feeds_targets = {e.target_id for e in self.edges if e.rel_type == "FEEDS"}
        middle = feeds_sources & feeds_targets
        # Filter to only Equipment nodes (not spaces)
        middle_equipment = set()
        for nid in middle:
            node = self._get_node(nid)
            if node and node.type == "Equipment":
                middle_equipment.add(nid)
        # Filter targets to Equipment only
        target_equipment = set()
        for nid in feeds_targets:
            node = self._get_node(nid)
            if node and node.type == "Equipment":
                target_equipment.add(nid)
        # Prefer equipment in middle of chain, then any target (has parent)
        if middle_equipment:
            params["equipment_id"] = list(middle_equipment)[0]
        elif target_equipment:
            params["equipment_id"] = list(target_equipment)[0]
        elif feeds_sources:
            params["equipment_id"] = list(feeds_sources)[0]

        # 5. MainMeter with FEEDS downstream
        for node in self.nodes:
            if node.type == "Equipment" and node.properties.get("equipment_type") == "MainMeter":
                has_feeds = any(e.source_id == node.id and e.rel_type == "FEEDS" for e in self.edges)
                if has_feeds:
                    params["meter_id"] = node.id
                    break

        # 6. UPS feeding equipment
        for node in self.nodes:
            if node.type == "Equipment" and node.properties.get("equipment_type") == "UPS":
                has_feeds = any(e.source_id == node.id and e.rel_type == "FEEDS" for e in self.edges)
                if has_feeds:
                    params["ups_id"] = node.id
                    break

        # 7. Tenant with METERS_TENANT relation
        for edge in self.edges:
            if edge.rel_type == "METERS_TENANT":
                params["tenant_id"] = edge.target_id
                break

        # 8. Point with timeseries data
        point_ids_with_ts = {ts.point_id for ts in self.timeseries}
        if point_ids_with_ts:
            params["point_id"] = list(point_ids_with_ts)[0]

        # 9. HVAC → Space path for Q20
        hvac_types = {"AHU", "VAV", "FCU", "RTU"}
        for node in self.nodes:
            if node.type == "Equipment" and node.properties.get("equipment_type") in hvac_types:
                for edge in self.edges:
                    if edge.source_id == node.id and edge.rel_type == "SERVES":
                        target = self._get_node(edge.target_id)
                        if target and target.type == "Space":
                            params["hvac_source_equipment_id"] = node.id
                            params["hvac_target_space_id"] = edge.target_id
                            break
                if "hvac_source_equipment_id" in params:
                    break

        # 10. Critical equipment for Q21 (server fed by UPS)
        if params.get("ups_id"):
            for edge in self.edges:
                if edge.source_id == params["ups_id"] and edge.rel_type == "FEEDS":
                    target = self._get_node(edge.target_id)
                    if target and target.type == "Equipment":
                        params["critical_equipment_id"] = edge.target_id
                        break

        # 11. Date range from timeseries
        if self.timeseries:
            timestamps = [ts.timestamp for ts in self.timeseries]
            params["date_start"] = min(timestamps).strftime("%Y-%m-%dT%H:%M:%SZ")
            params["date_end"] = max(timestamps).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 12. Default values
        params.setdefault("reference_date", self.reference_date.strftime("%Y-%m-%d"))
        params.setdefault("days_ahead", 90)
        params.setdefault("co2_factor", 0.0569)
        params.setdefault("max_hops", 3)
        params.setdefault("tag_pattern", "^brick:")
        params.setdefault("source_type", "MainMeter")

        # 12b. Capability - find one that actually exists in HVAC equipment
        hvac_types = {"AHU", "VAV", "FCU", "Chiller", "Boiler", "HeatPump", "CoolingTower"}
        existing_capability = None
        for node in self.nodes:
            eq_type = node.properties.get("equipment_type", "")
            if eq_type in hvac_types and node.capabilities:
                # Prefer humidity_control if it exists, otherwise take any
                if "humidity_control" in node.capabilities:
                    existing_capability = "humidity_control"
                    break
                elif existing_capability is None:
                    existing_capability = node.capabilities[0]
        params.setdefault("capability", existing_capability or "humidity_control")

        # 13. Device ID from BACnet protocol
        for node in self.nodes:
            if node.protocol.get("device_id"):
                params["device_id"] = node.protocol["device_id"]
                break
        params.setdefault("device_id", 1234)

        # 14. Q27: Non-exit space on a floor that has exits (ground floor)
        # Find a space that is NOT an exit but is on the same floor as exit spaces
        non_exit_space_for_q27 = None
        for node in self.nodes:
            if node.type == "Space" and not node.properties.get("is_exit", False):
                level_index = node.properties.get("level_index")
                if level_index == 0:  # Ground floor
                    non_exit_space_for_q27 = node.id
                    break
        if non_exit_space_for_q27:
            params["evacuation_space_id"] = non_exit_space_for_q27

        # 15. Q28: SubMeter ID for tenant impact chain
        for node in self.nodes:
            if node.type == "Equipment" and node.properties.get("equipment_type") == "SubMeter":
                params["submeter_id"] = node.id
                break

        # 16. Q29: Transformer ID for power paths
        for node in self.nodes:
            if node.type == "Equipment" and node.properties.get("equipment_type") == "Transformer_HT_BT":
                params["transformer_id"] = node.id
                break

        # 17. Q32: Domain for schema validation
        params.setdefault("domain", "HVAC")

        # =====================================================================
        # WRITE QUERY PARAMETERS (QW1-QW8)
        # =====================================================================

        # QW1: Timeseries Append - use existing point with timeseries
        # Generate sample data for batch insert
        if params.get("point_id") and self.timeseries:
            sample_point = params["point_id"]
            # Use reference_date for new timestamps
            ref_date = self.reference_date
            params["qw1_point_ids"] = [sample_point, sample_point, sample_point]
            params["qw1_timestamps"] = [
                (ref_date + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
                for i in range(3)
            ]
            params["qw1_values"] = [21.5, 22.0, 21.8]
            # M1 format: chunks array
            params["qw1_chunks"] = [{
                "point_id": sample_point,
                "date": ref_date.strftime("%Y-%m-%d"),
                "timestamps": params["qw1_timestamps"],
                "values": params["qw1_values"],
            }]

        # QW2: Metadata Update - use equipment_id, add a custom tag
        if params.get("equipment_id"):
            params["qw2_node_id"] = params["equipment_id"]
            params["qw2_tag_key"] = "calibration_status"
            params["qw2_tag_value"] = "verified_2024"

        # QW3: Relation Mutation - create new FEEDS relation
        # Find two equipment that could be connected
        if params.get("meter_id") and params.get("equipment_id"):
            params["qw3_source_id"] = params["meter_id"]
            params["qw3_target_id"] = params["equipment_id"]
            params["qw3_rel_type"] = "FEEDS"

        # QW4: Maintenance Event Append - add event to equipment
        if params.get("equipment_id"):
            params["qw4_equipment_id"] = params["equipment_id"]
            params["qw4_event"] = {
                "date": self.reference_date.strftime("%Y-%m-%d"),
                "type": "preventive",
                "technician": "Tech_Benchmark",
                "description": "Benchmark test maintenance event",
                "cost": 150.0,
                "parts_replaced": ["filter", "belt"],
            }

        # QW5: Deep Calibration Update - update point calibration
        if params.get("point_id"):
            params["qw5_point_id"] = params["point_id"]
            params["qw5_calibration_date"] = self.reference_date.strftime("%Y-%m-%d")
            params["qw5_next_date"] = (self.reference_date + timedelta(days=365)).strftime("%Y-%m-%d")
            params["qw5_technician"] = "Calibration_Corp"

        # QW6: Metadata Merge - merge firmware info into equipment
        if params.get("equipment_id"):
            params["qw6_equipment_id"] = params["equipment_id"]
            params["qw6_metadata_patch"] = {
                "firmware_version": "3.2.1",
                "last_update": self.reference_date.strftime("%Y-%m-%d"),
            }

        # QW7: Add Capability - add new capability to HVAC equipment
        # Find an HVAC equipment that doesn't have 'demand_control_ventilation'
        hvac_for_qw7 = None
        for node in self.nodes:
            eq_type = node.properties.get("equipment_type", "")
            if eq_type in {"AHU", "VAV", "FCU"} and node.capabilities:
                if "demand_control_ventilation" not in node.capabilities:
                    hvac_for_qw7 = node.id
                    break
        if hvac_for_qw7:
            params["qw7_equipment_id"] = hvac_for_qw7
            params["qw7_new_capability"] = "demand_control_ventilation"
        elif params.get("equipment_id"):
            # Fallback to any equipment
            params["qw7_equipment_id"] = params["equipment_id"]
            params["qw7_new_capability"] = "benchmark_capability"

        # QW8: Remove Metadata Key - remove a custom key
        if params.get("equipment_id"):
            params["qw8_node_id"] = params["equipment_id"]
            params["qw8_key_to_remove"] = "legacy_protocol_id"

        return params

    def _write_query_params(self, output_dir: Path):
        """Write queries_params.yaml with validated parameters."""
        params = self._generate_query_params()

        output = {
            "metadata": {
                "generator_version": "3.0",
                "seed": self.seed,
                "generated_at": datetime.now().isoformat(),
                "profile": self.profile_name,
                "duration": self.duration,
            },
            "parameters": params
        }

        params_file = output_dir / "queries_params.yaml"
        with open(params_file, "w", encoding="utf-8") as f:
            yaml.dump(output, f, default_flow_style=False, allow_unicode=True)

        print(f"Generated queries_params.yaml with {len(params)} parameters")

    # =========================================================================
    # EXPORT METHODS
    # =========================================================================

    def export_to_parquet(self, output_dir: Path):
        """Exporte vers Parquet (nécessite pyarrow)"""
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            print("Warning: pyarrow not installed. Falling back to JSON export.")
            return self.export_to_json(output_dir)

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Nodes
        nodes_data = []
        for n in self.nodes:
            nodes_data.append({
                'id': n.id,
                'type': n.type,
                'name': n.name,
                'building_id': n.properties.get('building_id'),
                'properties': json.dumps(n.properties),
                'capabilities': json.dumps(n.capabilities),
                'metadata': json.dumps(n.metadata),
                'tags': json.dumps(n.tags),
                'protocol': json.dumps(n.protocol),
                'calibration': json.dumps(n.calibration),
                'range': json.dumps(n.range_info)
            })

        nodes_table = pa.Table.from_pylist(nodes_data)
        pq.write_table(nodes_table, output_dir / "nodes.parquet")

        # Edges
        edges_data = [{'source_id': e.source_id, 'target_id': e.target_id,
                       'rel_type': e.rel_type, 'properties': json.dumps(e.properties)}
                      for e in self.edges]
        edges_table = pa.Table.from_pylist(edges_data)
        pq.write_table(edges_table, output_dir / "edges.parquet")

        # Timeseries
        ts_data = [{'point_id': t.point_id, 'time': t.timestamp.isoformat(), 'value': t.value}
                   for t in self.timeseries]
        ts_table = pa.Table.from_pylist(ts_data)
        pq.write_table(ts_table, output_dir / "timeseries.parquet")

        # Write queries_params.yaml
        self._write_query_params(output_dir)

        # Generate expected answers for validation
        self._write_expected_answers(output_dir)

        print(f"Exported to Parquet: {output_dir}")
        return output_dir

    def _write_expected_answers(self, output_dir: Path):
        """Generate and write expected answers for Q1-Q23."""
        try:
            from .expected_answers import ExpectedAnswerGenerator, write_expected_answers

            print("Generating expected answers for validation...")

            # Load parameters
            params = self._generate_query_params()

            # Generate answers
            generator = ExpectedAnswerGenerator(
                nodes=self.nodes,
                edges=self.edges,
                timeseries=self.timeseries,
            )

            answers = generator.generate_all(params)

            # Validate: check for empty answers (except Q5 which may legitimately be empty)
            # Q5 is orphan detection - may be empty in well-connected datasets
            empty_queries = []
            for query_id, answer in answers.items():
                if answer.row_count == 0 and query_id not in ("Q5",):
                    empty_queries.append(query_id)

            if empty_queries:
                print(f"WARNING: The following queries have 0 results: {empty_queries}")
                print("  This may indicate missing data or incorrect parameters.")
                for qid in empty_queries:
                    print(f"    {qid}: params={answers[qid].parameters}")

            # Write to disk
            write_expected_answers(answers, output_dir)

            # Summary
            non_empty = sum(1 for a in answers.values() if a.row_count > 0)
            print(f"Expected answers: {non_empty}/{len(answers)} queries have results")

        except Exception as e:
            print(f"Warning: Failed to generate expected answers: {e}")
            import traceback
            traceback.print_exc()

    def export_to_json(self, output_dir: Path):
        """Exporte vers JSON (fallback)"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Nodes
        nodes_data = []
        for n in self.nodes:
            nodes_data.append({
                'id': n.id,
                'type': n.type,
                'name': n.name,
                'properties': n.properties,
                'capabilities': n.capabilities,
                'metadata': n.metadata,
                'tags': n.tags,
                'protocol': n.protocol,
                'calibration': n.calibration,
                'range': n.range_info
            })

        with open(output_dir / "nodes.json", 'w', encoding='utf-8') as f:
            json.dump(nodes_data, f, indent=2, default=str)

        # Edges
        edges_data = [{'source_id': e.source_id, 'target_id': e.target_id,
                       'rel_type': e.rel_type, 'properties': e.properties}
                      for e in self.edges]
        with open(output_dir / "edges.json", 'w', encoding='utf-8') as f:
            json.dump(edges_data, f, indent=2)

        # Timeseries
        ts_data = [{'point_id': t.point_id, 'time': t.timestamp.isoformat(), 'value': t.value}
                   for t in self.timeseries]
        with open(output_dir / "timeseries.json", 'w', encoding='utf-8') as f:
            json.dump(ts_data, f, indent=2)

        # Write queries_params.yaml
        self._write_query_params(output_dir)

        # Generate expected answers for validation
        self._write_expected_answers(output_dir)

        print(f"Exported to JSON: {output_dir}")
        return output_dir


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate benchmark dataset')
    parser.add_argument('--profile', type=str, default='small',
                        help='Profile name (small, medium, large, xlarge)')
    parser.add_argument('--duration', type=str, default='2d',
                        choices=['2d', '1w', '1m', '6m', '1y'],
                        help='Timeseries duration (2d, 1w, 1m, 6m, 1y)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--config-dir', type=str, default='config',
                        help='Config directory path')
    parser.add_argument('--output', type=str, default='data/generated',
                        help='Output directory')
    parser.add_argument('--format', type=str, choices=['parquet', 'json'], default='parquet',
                        help='Output format')
    parser.add_argument('--target-rows', type=int, default=None,
                        help='Budget max de lignes timeseries (défaut: auto selon durée)')

    args = parser.parse_args()

    # Générer
    generator = DatasetGenerator(
        config_dir=Path(args.config_dir),
        profile=args.profile,
        seed=args.seed,
        duration=args.duration,
        target_rows=args.target_rows
    )
    generator.generate()

    # Exporter vers {output}/{profile}-{duration}/
    output_dir = Path(args.output) / f"{args.profile}-{args.duration}"
    if args.format == 'parquet':
        generator.export_to_parquet(output_dir)
    else:
        generator.export_to_json(output_dir)

    # Stats
    print(f"\n=== STATISTIQUES ===")
    print(f"Profile: {args.profile}")
    print(f"Duration: {args.duration} ({generator.duration_hours}h)")
    print(f"Seed: {generator.seed}")
    print(f"Nodes: {len(generator.nodes)}")
    print(f"Edges: {len(generator.edges)}")
    print(f"Timeseries: {len(generator.timeseries)}")

    # Comptage par type
    node_types = {}
    for n in generator.nodes:
        node_types[n.type] = node_types.get(n.type, 0) + 1
    print(f"\nNode types: {node_types}")

    rel_types = {}
    for e in generator.edges:
        rel_types[e.rel_type] = rel_types.get(e.rel_type, 0) + 1
    print(f"Relation types: {rel_types}")

    # Vérifications critiques
    print(f"\n=== VÉRIFICATIONS ===")
    orphans = [n for n in generator.nodes if n.id == 'orphan_1']
    print(f"Orphan exists: {len(orphans) == 1}")

    feeds = [e for e in generator.edges if e.rel_type == 'FEEDS']
    print(f"FEEDS relations: {len(feeds)}")

    bacnet_points = [n for n in generator.nodes
                     if n.type == 'Point' and n.protocol.get('type') == 'BACnet']
    print(f"Points BACnet: {len(bacnet_points)}")

    calibrations_overdue = [n for n in generator.nodes
                           if n.calibration.get('next_date', '9999') < '2024-06-01']
    print(f"Calibrations échues: {len(calibrations_overdue)}")


if __name__ == "__main__":
    main()
