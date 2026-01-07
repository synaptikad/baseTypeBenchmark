"""
Golden Dataset Generator - Benchmark BaseType V3
Dataset minimal pour validation des 23 queries.
Généré par AGENT-C
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

# ===========================================================================
# DATACLASSES
# ===========================================================================

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


# ===========================================================================
# GOLDEN DATASET CLASS
# ===========================================================================

class GoldenDataset:
    """
    Dataset minimal pour validation benchmark.

    Structure créée :
    - 1 Site → 1 Building → 2 Floors → 4 Spaces (2 par étage)
    - Chaîne énergie : MainMeter → SubMeter → AHU → VAV×2
    - Capteurs : TemperatureSensor×4, CO2_Sensor×2
    - Sécurité : BadgeReader×2, IPCamera×2
    - IT : UPS → Server×2, Switch
    - 1 Tenant avec METERS_TENANT
    - 1 Orphelin (équipement sans relations)
    - Adjacences entre espaces
    """

    def __init__(self):
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.timeseries: List[TimeseriesPoint] = []

        # Créer les données
        self._create_spatial_hierarchy()
        self._create_energy_chain()
        self._create_hvac_sensors()
        self._create_security_equipment()
        self._create_it_equipment()
        self._create_tenants()
        self._create_zones()
        self._create_contracts()
        self._create_orphan()
        self._create_adjacency()
        self._create_timeseries()

    # -------------------------------------------------------------------------
    # SPATIAL HIERARCHY
    # -------------------------------------------------------------------------

    def _create_spatial_hierarchy(self):
        """Site → Building → Floors → Spaces"""

        # Site
        self.nodes.append(Node(
            id="site_1",
            type="Site",
            name="Campus Alpha",
            properties={"address": "123 Tech Park", "gps_coords": {"lat": 48.8566, "lon": 2.3522}}
        ))

        # Building
        self.nodes.append(Node(
            id="building_1",
            type="Building",
            name="Building A",
            properties={"site_id": "site_1", "gross_area_m2": 5000.0, "address": "Building A, Campus Alpha"}
        ))
        self.edges.append(Edge("site_1", "building_1", "CONTAINS"))

        # Floors
        for i in range(1, 3):  # 2 étages
            floor_type = "ground" if i == 1 else "standard"
            self.nodes.append(Node(
                id=f"floor_{i}",
                type="Floor",
                name=f"Floor {i}",
                properties={"building_id": "building_1", "floor_type": floor_type, "level_index": i}
            ))
            self.edges.append(Edge("building_1", f"floor_{i}", "CONTAINS"))

            # Spaces (2 par étage)
            for j in range(1, 3):
                space_type = "office" if j == 1 else "meeting_room"
                self.nodes.append(Node(
                    id=f"space_{i}_{j}",
                    type="Space",
                    name=f"Space {i}-{j}",
                    properties={
                        "floor_id": f"floor_{i}",
                        "building_id": "building_1",
                        "space_type": space_type,
                        "area_m2": 50.0 if space_type == "office" else 25.0,
                        "capacity": 6 if space_type == "office" else 10
                    }
                ))
                self.edges.append(Edge(f"floor_{i}", f"space_{i}_{j}", "CONTAINS"))

    # -------------------------------------------------------------------------
    # ENERGY CHAIN (pour Q1, Q2, Q18, Q21)
    # -------------------------------------------------------------------------

    def _create_energy_chain(self):
        """MainMeter → SubMeter → AHU → VAV×2"""

        # MainMeter
        self.nodes.append(Node(
            id="meter_main_1",
            type="Equipment",
            name="Main Electrical Meter",
            properties={
                "equipment_type": "MainMeter",
                "domain": "Electrical",
                "building_id": "building_1"
            },
            metadata={
                "manufacturer": "Schneider",
                "model": "PM5500",
                "serial_number": "SN-MAIN-001",
                "installation_date": "2020-01-15",
                "warranty_end": "2025-01-15",
                "maintenance_priority": "critical"
            },
            tags=["brick:Electrical_Meter", "haystack:elec-meter", "main"]
        ))

        # SubMeter
        self.nodes.append(Node(
            id="submeter_1",
            type="Equipment",
            name="HVAC SubMeter",
            properties={
                "equipment_type": "SubMeter",
                "domain": "Metering",
                "building_id": "building_1"
            },
            metadata={
                "manufacturer": "Schneider",
                "model": "PM3200",
                "serial_number": "SN-SUB-001",
                "installation_date": "2020-06-01",
                "warranty_end": "2024-06-01",  # EXPIRÉ
                "maintenance_priority": "high"
            },
            tags=["brick:Electrical_Meter", "haystack:elec-meter", "hvac"]
        ))
        self.edges.append(Edge("meter_main_1", "submeter_1", "FEEDS"))

        # Point énergie sur SubMeter
        self.nodes.append(Node(
            id="point_submeter_1_energy",
            type="Point",
            name="HVAC Energy",
            properties={
                "quantity": "energy",
                "unit": "kWh",
                "equipment_id": "submeter_1",
                "building_id": "building_1",
                "frequency": "15min"
            },
            protocol={
                "type": "BACnet",
                "device_id": 1234,
                "object_type": "analog-input",
                "object_instance": 1,
                "property": "present-value"
            },
            calibration={
                "last_date": "2023-01-15",
                "next_date": "2024-01-15",  # ÉCHU
                "offset": 0.0,
                "technician": "Tech A"
            }
        ))
        self.edges.append(Edge("submeter_1", "point_submeter_1_energy", "HAS_POINT"))

        # AHU (Air Handling Unit)
        self.nodes.append(Node(
            id="ahu_1",
            type="Equipment",
            name="AHU Building A",
            properties={
                "equipment_type": "AHU",
                "domain": "HVAC",
                "building_id": "building_1",
                "floor_id": "floor_1"
            },
            capabilities=["heating", "cooling", "humidity_control", "air_filtration"],
            metadata={
                "manufacturer": "Carrier",
                "model": "39M",
                "serial_number": "SN-AHU-001",
                "installation_date": "2020-01-20",
                "warranty_end": "2025-01-20",
                "maintenance_priority": "critical",
                "firmware_version": "2.3.1"
            },
            tags=["brick:AHU", "haystack:ahu", "primary"],
            protocol={
                "type": "BACnet",
                "device_id": 100,
                "network": 1,
                "address": "100.1.1.1"
            }
        ))
        self.edges.append(Edge("submeter_1", "ahu_1", "FEEDS"))
        self.edges.append(Edge("ahu_1", "building_1", "SERVES"))

        # VAV×2
        for i in range(1, 3):
            self.nodes.append(Node(
                id=f"vav_{i}",
                type="Equipment",
                name=f"VAV Box {i}",
                properties={
                    "equipment_type": "VAV",
                    "domain": "HVAC",
                    "building_id": "building_1",
                    "floor_id": f"floor_{i}",
                    "space_id": f"space_{i}_1"
                },
                capabilities=["variable_air_volume", "reheat"] if i == 1 else ["variable_air_volume"],
                metadata={
                    "manufacturer": "Trane",
                    "model": "?"  if i == 2 else "VAV-123",
                    "serial_number": f"SN-VAV-00{i}",
                    "installation_date": "2020-02-01",
                    "warranty_end": "2025-02-01",
                    "maintenance_priority": "medium"
                },
                tags=[f"brick:VAV", "haystack:vav", f"zone_{i}"],
                protocol={
                    "type": "BACnet",
                    "device_id": 1234,  # Même device que point_submeter pour Q14
                    "network": 1,
                    "address": f"100.1.1.{10+i}"
                }
            ))
            self.edges.append(Edge("ahu_1", f"vav_{i}", "FEEDS"))
            self.edges.append(Edge(f"vav_{i}", f"space_{i}_1", "SERVES"))
            self.edges.append(Edge(f"vav_{i}", f"space_{i}_1", "LOCATED_IN"))

    # -------------------------------------------------------------------------
    # HVAC SENSORS (pour Q4, Q13)
    # -------------------------------------------------------------------------

    def _create_hvac_sensors(self):
        """Temperature sensors et CO2 sensors"""

        # Temperature sensors (4 : 1 par space)
        for floor in range(1, 3):
            for space in range(1, 3):
                sensor_id = f"temp_sensor_{floor}_{space}"
                self.nodes.append(Node(
                    id=sensor_id,
                    type="Equipment",
                    name=f"Temperature Sensor {floor}-{space}",
                    properties={
                        "equipment_type": "TemperatureSensor",
                        "domain": "HVAC",
                        "building_id": "building_1",
                        "floor_id": f"floor_{floor}",
                        "space_id": f"space_{floor}_{space}"
                    },
                    metadata={
                        "manufacturer": "Siemens",
                        "model": "QAA2012",
                        "installation_date": "2020-03-01"
                    },
                    protocol={
                        "type": "BACnet",
                        "device_id": 1234,  # Même device pour Q14
                        "network": 1
                    }
                ))
                self.edges.append(Edge(sensor_id, f"space_{floor}_{space}", "MONITORS"))
                self.edges.append(Edge(sensor_id, f"space_{floor}_{space}", "LOCATED_IN"))

                # Point température
                point_id = f"point_{sensor_id}_temp"
                self.nodes.append(Node(
                    id=point_id,
                    type="Point",
                    name=f"Temperature {floor}-{space}",
                    properties={
                        "quantity": "temperature",
                        "unit": "°C",
                        "equipment_id": sensor_id,
                        "building_id": "building_1",
                        "frequency": "5min"
                    },
                    protocol={
                        "type": "BACnet",
                        "device_id": 1234,
                        "object_type": "analog-input",
                        "object_instance": 100 + floor * 10 + space
                    },
                    range_info={"min": 15.0, "max": 30.0, "unit": "°C"},
                    calibration={
                        "last_date": "2023-06-01",
                        "next_date": "2025-06-01",  # Valide
                        "offset": 0.1,
                        "technician": "Tech B"
                    }
                ))
                self.edges.append(Edge(sensor_id, point_id, "HAS_POINT"))

        # CO2 sensors (2 : 1 par floor, dans space_X_1)
        for floor in range(1, 3):
            sensor_id = f"co2_sensor_{floor}"
            self.nodes.append(Node(
                id=sensor_id,
                type="Equipment",
                name=f"CO2 Sensor Floor {floor}",
                properties={
                    "equipment_type": "CO2_Sensor",
                    "domain": "HVAC",
                    "building_id": "building_1",
                    "floor_id": f"floor_{floor}",
                    "space_id": f"space_{floor}_1"
                },
                protocol={"type": "Modbus", "address": f"10.0.{floor}.1", "register": 100}
            ))
            self.edges.append(Edge(sensor_id, f"space_{floor}_1", "MONITORS"))

            # Point CO2
            point_id = f"point_{sensor_id}_co2"
            self.nodes.append(Node(
                id=point_id,
                type="Point",
                name=f"CO2 Level Floor {floor}",
                properties={
                    "quantity": "co2",
                    "unit": "ppm",
                    "equipment_id": sensor_id,
                    "building_id": "building_1"
                },
                range_info={"min": 400, "max": 2000, "unit": "ppm"},
                calibration={
                    "last_date": "2022-01-01",
                    "next_date": "2023-06-01",  # ÉCHU
                    "offset": 0.0,
                    "technician": "Tech C"
                }
            ))
            self.edges.append(Edge(sensor_id, point_id, "HAS_POINT"))

    # -------------------------------------------------------------------------
    # SECURITY EQUIPMENT (pour Q10)
    # -------------------------------------------------------------------------

    def _create_security_equipment(self):
        """Badge readers et cameras"""

        # Badge readers (1 par floor)
        for floor in range(1, 3):
            reader_id = f"badge_reader_{floor}"
            self.nodes.append(Node(
                id=reader_id,
                type="Equipment",
                name=f"Badge Reader Floor {floor}",
                properties={
                    "equipment_type": "BadgeReader",
                    "domain": "Security",
                    "building_id": "building_1",
                    "floor_id": f"floor_{floor}",
                    "space_id": f"space_{floor}_1"
                }
            ))
            self.edges.append(Edge(reader_id, f"space_{floor}_1", "SECURES"))
            self.edges.append(Edge(reader_id, f"space_{floor}_1", "GRANTS_ACCESS"))

        # IP Cameras (2, lobby + parking)
        for i, location in enumerate(["lobby", "parking"], 1):
            camera_id = f"camera_{i}"
            space_id = "space_1_1" if location == "lobby" else "space_2_1"
            self.nodes.append(Node(
                id=camera_id,
                type="Equipment",
                name=f"IP Camera {location.title()}",
                properties={
                    "equipment_type": "IPCamera",
                    "domain": "Security",
                    "building_id": "building_1"
                }
            ))
            self.edges.append(Edge(camera_id, space_id, "MONITORS"))

    # -------------------------------------------------------------------------
    # IT EQUIPMENT (pour Q11)
    # -------------------------------------------------------------------------

    def _create_it_equipment(self):
        """UPS → Servers, Switch"""

        # UPS
        self.nodes.append(Node(
            id="ups_1",
            type="Equipment",
            name="Main UPS",
            properties={
                "equipment_type": "UPS",
                "domain": "Electrical",
                "building_id": "building_1"
            },
            capabilities=["battery_backup", "surge_protection"],
            metadata={
                "manufacturer": "APC",
                "model": "Smart-UPS 3000",
                "serial_number": "SN-UPS-001",
                "warranty_end": "2024-12-31"  # Expire bientôt
            }
        ))
        self.edges.append(Edge("meter_main_1", "ups_1", "FEEDS"))

        # Servers
        for i in range(1, 3):
            server_id = f"server_{i}"
            self.nodes.append(Node(
                id=server_id,
                type="Equipment",
                name=f"Rack Server {i}",
                properties={
                    "equipment_type": "RackServer",
                    "domain": "IT",
                    "building_id": "building_1"
                }
            ))
            self.edges.append(Edge("ups_1", server_id, "FEEDS"))

        # Switch
        self.nodes.append(Node(
            id="switch_1",
            type="Equipment",
            name="Network Switch",
            properties={
                "equipment_type": "NetworkSwitch",
                "domain": "IT",
                "building_id": "building_1"
            }
        ))
        self.edges.append(Edge("ups_1", "switch_1", "FEEDS"))
        self.edges.append(Edge("switch_1", "server_1", "NETWORK_LINK"))
        self.edges.append(Edge("switch_1", "server_2", "NETWORK_LINK"))

    # -------------------------------------------------------------------------
    # TENANTS (pour Q8, Q9)
    # -------------------------------------------------------------------------

    def _create_tenants(self):
        """Locataires avec comptage"""

        self.nodes.append(Node(
            id="tenant_1",
            type="Tenant",
            name="TechCorp Inc.",
            properties={
                "contract_start": "2021-01-01",
                "contract_end": "2026-12-31"
            }
        ))

        # Tenant occupe des espaces
        self.edges.append(Edge("tenant_1", "space_1_1", "OCCUPIES"))
        self.edges.append(Edge("tenant_1", "space_1_2", "OCCUPIES"))

        # SubMeter mesure le tenant
        self.edges.append(Edge("submeter_1", "tenant_1", "METERS_TENANT"))

    # -------------------------------------------------------------------------
    # ZONES (pour Q23)
    # -------------------------------------------------------------------------

    def _create_zones(self):
        """Zones logiques"""

        self.nodes.append(Node(
            id="zone_thermal_1",
            type="Zone",
            name="Thermal Zone A",
            properties={
                "zone_type": "thermal",
                "description": "Zone thermique principale"
            }
        ))

        # Équipements membres de la zone
        self.edges.append(Edge("vav_1", "zone_thermal_1", "MEMBER_OF"))
        self.edges.append(Edge("vav_2", "zone_thermal_1", "MEMBER_OF"))
        self.edges.append(Edge("submeter_1", "zone_thermal_1", "METERS_ZONE"))

    # -------------------------------------------------------------------------
    # CONTRACTS (pour Q15)
    # -------------------------------------------------------------------------

    def _create_contracts(self):
        """Contrats de maintenance"""

        self.nodes.append(Node(
            id="contract_1",
            type="Contract",
            name="HVAC Maintenance Contract",
            properties={
                "contract_type": "maintenance",
                "start_date": "2022-01-01",
                "end_date": "2025-12-31",
                "provider": "ClimaTech Services"
            }
        ))

        # Équipements couverts
        self.edges.append(Edge("ahu_1", "contract_1", "COVERED_BY"))
        self.edges.append(Edge("vav_1", "contract_1", "COVERED_BY"))
        self.edges.append(Edge("vav_2", "contract_1", "COVERED_BY"))

    # -------------------------------------------------------------------------
    # ORPHAN (pour Q5)
    # -------------------------------------------------------------------------

    def _create_orphan(self):
        """Équipement orphelin sans relations"""

        self.nodes.append(Node(
            id="orphan_1",
            type="Equipment",
            name="Orphan Sensor",
            properties={
                "equipment_type": "TemperatureSensor",
                "domain": "HVAC",
                "building_id": "building_1"
            }
        ))
        # Pas d'edges ! C'est le but pour Q5

    # -------------------------------------------------------------------------
    # ADJACENCY (pour Q23)
    # -------------------------------------------------------------------------

    def _create_adjacency(self):
        """Relations d'adjacence entre espaces"""

        # Espaces du même étage sont adjacents
        self.edges.append(Edge("space_1_1", "space_1_2", "ADJACENT_TO"))
        self.edges.append(Edge("space_1_2", "space_1_1", "ADJACENT_TO"))  # Symétrique
        self.edges.append(Edge("space_2_1", "space_2_2", "ADJACENT_TO"))
        self.edges.append(Edge("space_2_2", "space_2_1", "ADJACENT_TO"))

    # -------------------------------------------------------------------------
    # TIMESERIES (pour Q6, Q7, Q12, Q13)
    # -------------------------------------------------------------------------

    def _create_timeseries(self):
        """Données timeseries sur 24h"""

        base_time = datetime(2024, 1, 15, 0, 0, 0)

        # Points à générer
        point_configs = [
            ("point_submeter_1_energy", lambda h: 100 + h * 5 + (h % 3)),  # Énergie croissante
            ("point_temp_sensor_1_1_temp", lambda h: 20 + (h % 8) * 0.5),  # Température variable
            ("point_temp_sensor_1_2_temp", lambda h: 21 + (h % 6) * 0.3),
            ("point_temp_sensor_2_1_temp", lambda h: 19 + (h % 10) * 0.4),
            ("point_temp_sensor_2_2_temp", lambda h: 22 + (h % 4) * 0.2),
            ("point_co2_sensor_1_co2", lambda h: 450 + h * 20 if 8 <= h <= 18 else 400),
            ("point_co2_sensor_2_co2", lambda h: 420 + h * 15 if 8 <= h <= 18 else 380),
        ]

        for point_id, value_fn in point_configs:
            for hour in range(24):
                self.timeseries.append(TimeseriesPoint(
                    point_id=point_id,
                    timestamp=base_time + timedelta(hours=hour),
                    value=float(value_fn(hour))
                ))


# ===========================================================================
# EXPORT FUNCTIONS
# ===========================================================================

def export_to_dicts(dataset: GoldenDataset) -> Dict[str, Any]:
    """Exporte le dataset en dictionnaires pour inspection"""
    return {
        "nodes": [
            {
                "id": n.id,
                "type": n.type,
                "name": n.name,
                "properties": n.properties,
                "capabilities": n.capabilities,
                "metadata": n.metadata,
                "tags": n.tags,
                "protocol": n.protocol,
                "calibration": n.calibration,
                "range": n.range_info
            }
            for n in dataset.nodes
        ],
        "edges": [
            {"source": e.source_id, "target": e.target_id, "type": e.rel_type, "properties": e.properties}
            for e in dataset.edges
        ],
        "timeseries": [
            {"point_id": t.point_id, "timestamp": t.timestamp.isoformat(), "value": t.value}
            for t in dataset.timeseries
        ]
    }


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    print("Generating Golden Dataset...")
    dataset = GoldenDataset()

    print(f"\n=== STATISTIQUES ===")
    print(f"Nodes: {len(dataset.nodes)}")
    print(f"Edges: {len(dataset.edges)}")
    print(f"Timeseries points: {len(dataset.timeseries)}")

    # Comptage par type
    node_types = {}
    for n in dataset.nodes:
        node_types[n.type] = node_types.get(n.type, 0) + 1
    print(f"\nNode types: {node_types}")

    rel_types = {}
    for e in dataset.edges:
        rel_types[e.rel_type] = rel_types.get(e.rel_type, 0) + 1
    print(f"Relation types: {rel_types}")

    # Vérifications critiques
    print(f"\n=== VÉRIFICATIONS ===")
    orphans = [n for n in dataset.nodes if n.id == "orphan_1"]
    print(f"Orphan exists: {len(orphans) == 1}")

    feeds = [e for e in dataset.edges if e.rel_type == "FEEDS"]
    print(f"FEEDS relations: {len(feeds)}")

    bacnet_points = [n for n in dataset.nodes
                     if n.type == "Point" and n.protocol.get("device_id") == 1234]
    print(f"Points BACnet device_id=1234: {len(bacnet_points)}")

    # Calibrations échues (avant 2024-06-01)
    overdue = [n for n in dataset.nodes
               if n.calibration.get("next_date", "9999") < "2024-06-01"]
    print(f"Calibrations échues: {len(overdue)}")

    print("\n=== EXPORT JSON (sample) ===")
    export = export_to_dicts(dataset)
    print(f"Sample node: {json.dumps(export['nodes'][0], indent=2, default=str)}")

    print("\nGolden dataset generation complete.")
