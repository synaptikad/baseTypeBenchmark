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

# Réutiliser les dataclasses de golden.py pour cohérence
from .golden import Node, Edge, TimeseriesPoint


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
        'event': 0,      # événements discrets, traitement spécial
    }

    # Budget rows par défaut selon durée (heures)
    # Dimensionné pour distribution: 20 energy + 30 slow + 50 normal + 10 fast
    DEFAULT_TARGET_ROWS = {
        48: 100000,      # 2 jours
        168: 300000,     # 1 semaine
        720: 1000000,    # 1 mois
        4320: 2000000,   # 6 mois
        8760: 3000000,   # 1 an
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

        # Index pour relations
        self._buildings: List[str] = []
        self._floors: Dict[str, List[str]] = {}  # building_id -> floor_ids
        self._spaces: Dict[str, List[str]] = {}  # floor_id -> space_ids
        self._equipment_by_space: Dict[str, List[str]] = {}
        self._equipment_by_building: Dict[str, List[str]] = {}
        self._points_by_equipment: Dict[str, List[str]] = {}
        self._meters: List[str] = []
        self._submeters: List[str] = []

    def generate(self) -> 'DatasetGenerator':
        """Génère le dataset complet"""
        print(f"Generating dataset with profile '{self.profile_name}', seed={self.seed}")

        # 1. Hiérarchie spatiale
        self._generate_spatial_hierarchy()

        # 2. Équipements et points
        self._generate_equipment_and_points()

        # 3. Tenants
        self._generate_tenants()

        # 4. Zones
        self._generate_zones()

        # 5. Relations additionnelles
        self._generate_additional_relations()

        # 6. Orphelin (pour Q5)
        self._generate_orphan()

        # 7. Timeseries
        self._generate_timeseries()

        print(f"Generated: {len(self.nodes)} nodes, {len(self.edges)} edges, {len(self.timeseries)} timeseries points")
        return self

    def _generate_spatial_hierarchy(self):
        """Génère Site → Buildings → Floors → Spaces"""

        # Site unique
        site_id = "site_1"
        self.nodes.append(Node(
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

            self.nodes.append(Node(
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
            for floor_config in self.profile.floors:
                floor_type = floor_config['type']
                floor_count = floor_config['count']

                for _ in range(floor_count):
                    floor_counter += 1
                    floor_id = f"floor_{b}_{floor_counter}"
                    self._floors[building_id].append(floor_id)
                    self._spaces[floor_id] = []

                    level_index = floor_counter - 1 if floor_type != 'basement' else -(floor_counter)

                    self.nodes.append(Node(
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

                            self.nodes.append(Node(
                                id=space_id,
                                type="Space",
                                name=f"{space_type.replace('_', ' ').title()} {space_counter}",
                                properties={
                                    'floor_id': floor_id,
                                    'building_id': building_id,
                                    'space_type': space_type,
                                    'area_m2': self.rng.uniform(15, 100),
                                    'capacity': self.rng.randint(2, 20)
                                }
                            ))
                            self.edges.append(Edge(floor_id, space_id, "CONTAINS"))

            # Adjacences entre espaces du même étage
            for floor_id in self._floors[building_id]:
                spaces = self._spaces[floor_id]
                for i in range(len(spaces) - 1):
                    self.edges.append(Edge(spaces[i], spaces[i + 1], "ADJACENT_TO"))
                    self.edges.append(Edge(spaces[i + 1], spaces[i], "ADJACENT_TO"))

    def _generate_equipment_and_points(self):
        """Génère les équipements et leurs points selon les configs"""

        for building_id in self._buildings:
            # 1. Compteur principal
            main_meter_id = self._create_equipment(
                'MainMeter', building_id, None, None, is_meter=True
            )
            self._meters.append(main_meter_id)

            # 2. Sous-compteurs
            for i in range(self.profile.meters.get('electrical', {}).get('per_building', 3)):
                submeter_id = self._create_equipment(
                    'SubMeter', building_id, None, None, is_meter=True
                )
                self._submeters.append(submeter_id)
                self.edges.append(Edge(main_meter_id, submeter_id, "FEEDS"))

            # 3. Équipements HVAC principaux
            ahu_ids = []
            for floor_id in self._floors[building_id]:
                # AHU par étage (si technical_hvac)
                spaces_on_floor = self._spaces[floor_id]
                technical_spaces = [s for s in spaces_on_floor
                                   if 'technical' in self._get_node(s).properties.get('space_type', '')]

                if technical_spaces:
                    ahu_id = self._create_equipment('AHU', building_id, floor_id, technical_spaces[0])
                    ahu_ids.append(ahu_id)
                    # AHU alimenté par sous-compteur
                    if self._submeters:
                        self.edges.append(Edge(self.rng.choice(self._submeters), ahu_id, "FEEDS"))
                    self.edges.append(Edge(ahu_id, building_id, "SERVES"))

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

                    # Capteurs CO2 dans grands espaces
                    if 'open' in space_type or 'conference' in space_type:
                        co2_id = self._create_equipment('CO2_Sensor', building_id, floor_id, space_id)
                        self.edges.append(Edge(co2_id, space_id, "MONITORS"))

                    # Sécurité
                    if 'lobby' in space_type or 'entry' in space_type:
                        badge_id = self._create_equipment('BadgeReader', building_id, floor_id, space_id)
                        self.edges.append(Edge(badge_id, space_id, "SECURES"))
                        self.edges.append(Edge(badge_id, space_id, "GRANTS_ACCESS"))

                        cam_id = self._create_equipment('IPCamera', building_id, floor_id, space_id)
                        self.edges.append(Edge(cam_id, space_id, "MONITORS"))

                    # IT dans server_room
                    if 'server' in space_type or 'technical_it' in space_type:
                        ups_id = self._create_equipment('UPS', building_id, floor_id, space_id)
                        self.edges.append(Edge(main_meter_id, ups_id, "FEEDS"))

                        for _ in range(self.rng.randint(2, 5)):
                            server_id = self._create_equipment('RackServer', building_id, floor_id, space_id)
                            self.edges.append(Edge(ups_id, server_id, "FEEDS"))

                        switch_id = self._create_equipment('NetworkSwitch', building_id, floor_id, space_id)
                        self.edges.append(Edge(ups_id, switch_id, "FEEDS"))

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

        # Génération JSONB
        protocol = self.protocol_gen.generate_for_equipment(config)
        metadata = self.metadata_gen.generate(config)
        capabilities = self.capabilities_gen.generate_capabilities(equipment_type)
        tags = self.capabilities_gen.generate_tags(equipment_type, config)

        # Créer le nœud
        self.nodes.append(Node(
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

            # Éviter les doublons
            if any(n.id == point_id for n in self.nodes):
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

            self.nodes.append(Node(
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

            self.nodes.append(Node(
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

    def _generate_zones(self):
        """Génère les zones logiques"""
        zone_types = ['thermal', 'security', 'fire']

        for building_id in self._buildings:
            for zone_type in zone_types:
                zone_id = f"zone_{building_id}_{zone_type}"

                self.nodes.append(Node(
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
        self.nodes.append(Node(
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

    def _generate_orphan(self):
        """Génère un équipement orphelin (sans relations) pour Q5"""
        orphan_id = "orphan_1"

        self.nodes.append(Node(
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
        """Génère les données timeseries selon frequency et budget rows"""
        # Grouper les points mesurables par frequency
        measurable_quantities = ['temperature', 'humidity', 'co2', 'power', 'energy', 'flow', 'pressure']
        points_by_freq = {'energy': [], 'slow': [], 'normal': [], 'fast': [], 'event': []}

        for n in self.nodes:
            if n.type == 'Point':
                quantity = n.properties.get('quantity', '')
                freq = n.properties.get('frequency', 'normal')
                if quantity in measurable_quantities and freq in points_by_freq:
                    points_by_freq[freq].append(n)
                elif freq == 'event' and freq in points_by_freq:
                    points_by_freq['event'].append(n)

        # Budget target (CLI override ou défaut)
        target_rows = self.target_rows or self._get_default_target_rows()

        # Calculer rows par point selon frequency
        duration_sec = self.duration_hours * 3600
        days = self.duration_hours / 24

        def rows_for_freq(freq, quantity=''):
            step = self.FREQUENCY_STEP_SECONDS[freq]
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

        # Limites de points par fréquence pour distribution équilibrée
        max_points_per_freq = {
            'energy': 20,   # tous les compteurs
            'slow': 30,     # échantillon
            'normal': 50,   # échantillon
            'fast': 10,     # petit échantillon (coûteux en rows)
        }

        # Sélectionner points par priorité jusqu'au budget
        selected = []
        rows_used = 0

        for freq in ['energy', 'slow', 'normal', 'fast']:
            rows_per_point = rows_for_freq(freq)
            max_points = max_points_per_freq[freq]
            count = 0
            for point in points_by_freq[freq]:
                if count >= max_points:
                    break
                if rows_used + rows_per_point <= target_rows:
                    selected.append((point, freq, rows_per_point))
                    rows_used += rows_per_point
                    count += 1

        # Ajouter events (budget séparé, toujours inclus, max 10 points)
        event_points = points_by_freq['event'][:10]
        for point in event_points:
            quantity = point.properties.get('quantity', '')
            rows = rows_for_freq('event', quantity)
            selected.append((point, 'event', rows))
            rows_used += rows

        # Sanity check
        if rows_used > target_rows * 1.1:  # 10% marge pour events
            print(f"WARNING: Budget dépassé: {rows_used} > {target_rows}")

        # Log breakdown
        breakdown = {}
        for _, freq, rows in selected:
            breakdown[freq] = breakdown.get(freq, 0) + rows
        print(f"Timeseries: {len(selected)} points, {rows_used} rows")
        print(f"  Breakdown: {breakdown}")

        # Générer les données
        base_time = self.reference_date
        end_time = base_time + timedelta(hours=self.duration_hours)

        for point, freq, _ in selected:
            quantity = point.properties.get('quantity', 'status')
            step_sec = self.FREQUENCY_STEP_SECONDS[freq]

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

    def _get_default_target_rows(self) -> int:
        """Budget rows par défaut selon durée"""
        for threshold, budget in sorted(self.DEFAULT_TARGET_ROWS.items()):
            if self.duration_hours <= threshold:
                return budget
        return self.DEFAULT_TARGET_ROWS[8760]

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
        """Récupère un nœud par ID"""
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

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

        print(f"Exported to Parquet: {output_dir}")
        return output_dir

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
