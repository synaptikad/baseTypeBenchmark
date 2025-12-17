"""Définition du modèle conceptuel pour le dataset synthétique.

Ce modèle pousse volontairement la complexité au maximum pour couvrir
l'ensemble des domaines d'un smart building/campus, au-delà de ce que
la plupart des solutions du marché modélisent aujourd'hui.

Inspiré des ontologies: Haystack v4, Brick Schema, RealEstateCore,
et des patterns observés dans les BOS industriels.

Domaines couverts:
- Spatial: Site, Building, Floor, Space, Zone
- Équipements: HVAC, Électrique, Plomberie, etc.
- Énergie: Compteurs, distribution, points de mesure
- IT/Datacenter: Serveurs, réseau, racks
- Audiovisuel: Écrans, projecteurs, systèmes de conférence
- Parking: Zones, places, véhicules
- Sécurité: Contrôle d'accès, vidéosurveillance, alarmes
- Organisation: Départements, équipes, personnes
- Contractuel: Contrats de maintenance, énergie, fournisseurs
- Exploitation: Tickets, workflows, notes, événements
- Groupements: Nomenclatures, profils, catégories

Patterns architecturaux:
- Multi-context: Un nœud peut appartenir à plusieurs contextes
- Attributs structurés: label, value, unit, category, date
- ControlEndpoint vs Endpoint: distinction commande/mesure
- Hiérarchie Category → Group → Items
- Position calculable pour chaque équipement
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


# =============================================================================
# Types de nœuds - Complexité maximale (~30 types)
# =============================================================================

class NodeType(str, Enum):
    """Types de nœuds couvrant tous les domaines d'un smart building/campus."""

    # --- Domaine Spatial ---
    SITE = "Site"
    BUILDING = "Building"
    FLOOR = "Floor"
    SPACE = "Space"
    ZONE = "Zone"  # Zone fonctionnelle (open space, zone de confort, etc.)

    # --- Domaine Équipements ---
    EQUIPMENT = "Equipment"
    POINT = "Point"
    SENSOR = "Sensor"
    ACTUATOR = "Actuator"
    CONTROLLER = "Controller"
    SYSTEM = "System"  # Système technique (CVC, électrique, etc.)

    # --- Domaine Énergie ---
    METER = "Meter"  # Compteur (électrique, eau, gaz)
    ENERGY_ZONE = "EnergyZone"  # Zone de distribution énergétique

    # --- Domaine IT/Datacenter ---
    DATACENTER = "Datacenter"
    RACK = "Rack"
    SERVER = "Server"
    NETWORK_DEVICE = "NetworkDevice"  # Switch, routeur, firewall
    STORAGE = "Storage"  # Baie de stockage

    # --- Domaine Audiovisuel ---
    AV_SYSTEM = "AVSystem"  # Système AV complet (salle de conf)
    DISPLAY = "Display"  # Écran, moniteur
    PROJECTOR = "Projector"
    SPEAKER = "Speaker"
    CONFERENCE_UNIT = "ConferenceUnit"  # Système visioconférence

    # --- Domaine Parking ---
    PARKING_ZONE = "ParkingZone"
    PARKING_LEVEL = "ParkingLevel"
    PARKING_SPOT = "ParkingSpot"
    VEHICLE = "Vehicle"
    CHARGING_STATION = "ChargingStation"  # Borne de recharge

    # --- Domaine Sécurité ---
    SECURITY_ZONE = "SecurityZone"
    ACCESS_POINT = "AccessPoint"  # Lecteur de badge, porte
    CAMERA = "Camera"
    ALARM = "Alarm"
    INTRUSION_DETECTOR = "IntrusionDetector"

    # --- Domaine Organisation ---
    ORGANIZATION = "Organization"
    DEPARTMENT = "Department"
    TEAM = "Team"
    PERSON = "Person"
    TENANT = "Tenant"  # Locataire (peut être une organisation)

    # --- Domaine Contractuel ---
    CONTRACT = "Contract"
    PROVIDER = "Provider"  # Fournisseur (énergie, maintenance)
    LEASE = "Lease"  # Bail
    WORK_ORDER = "WorkOrder"  # Ordre de travail maintenance

    # --- Domaine Exploitation (Tickets/Workflow) ---
    TICKET = "Ticket"  # Incident, demande, maintenance
    WORKFLOW = "Workflow"  # Processus métier
    WORKFLOW_STEP = "WorkflowStep"  # Étape d'un workflow
    EVENT = "Event"  # Événement historique
    NOTE = "Note"  # Note/commentaire sur un nœud

    # --- Domaine Groupement/Nomenclature ---
    CONTEXT = "Context"  # Partition logique du graphe
    CATEGORY = "Category"  # Catégorie de groupement
    GROUP = "Group"  # Groupe d'éléments
    NOMENCLATURE = "Nomenclature"  # Profil/template de points

    # --- Points de contrôle (distinction mesure/commande) ---
    CONTROL_ENDPOINT = "ControlEndpoint"  # Point de commande (setpoint, mode)
    ENDPOINT = "Endpoint"  # Point de mesure (capteur)

    # --- Data nodes (données attachées aux objets) ---
    FILE = "File"  # Fichiers documentaires (PDF, JPEG, DOCX, DWG)
    TIMESERIES_ARCHIVE = "TimeSeriesArchive"  # Historique de valeurs avec archivage
    CHANGELOG = "Changelog"  # Journal de changements (audit trail)
    BIM_OBJECT = "BimObject"  # Objet BIM avec géométrie (lien maquette numérique)
    ATTRIBUTE_CATEGORY = "AttributeCategory"  # Catégorie d'attributs structurés


# =============================================================================
# Types de relations - Complexité maximale (~20 types)
# =============================================================================

class RelationType(str, Enum):
    """Types de relations couvrant toutes les interactions du modèle."""

    # --- Relations Spatiales ---
    CONTAINS = "CONTAINS"  # Hiérarchie spatiale
    LOCATED_IN = "LOCATED_IN"  # Localisation d'équipement
    ADJACENT_TO = "ADJACENT_TO"  # Proximité spatiale

    # --- Relations Fonctionnelles ---
    HAS_PART = "HAS_PART"  # Composition d'équipement
    HAS_POINT = "HAS_POINT"  # Points de mesure/commande
    SERVES = "SERVES"  # Service fonctionnel (CVC → Zone)
    CONTROLS = "CONTROLS"  # Relation de contrôle
    MONITORS = "MONITORS"  # Supervision
    CONNECTS_TO = "CONNECTS_TO"  # Connexion physique/logique

    # --- Relations Énergétiques ---
    FEEDS = "FEEDS"  # Distribution électrique/fluide
    METERS = "METERS"  # Mesure de consommation

    # --- Relations IT/Réseau ---
    HOSTS = "HOSTS"  # Hébergement (rack → serveur)
    NETWORK_LINK = "NETWORK_LINK"  # Lien réseau
    STORES_DATA = "STORES_DATA"  # Stockage de données

    # --- Relations Organisationnelles ---
    BELONGS_TO = "BELONGS_TO"  # Appartenance organisationnelle
    MANAGES = "MANAGES"  # Gestion/responsabilité
    OCCUPIES = "OCCUPIES"  # Occupation d'espace
    WORKS_IN = "WORKS_IN"  # Affectation de personne

    # --- Relations Contractuelles ---
    COVERED_BY = "COVERED_BY"  # Couverture contractuelle
    PROVIDED_BY = "PROVIDED_BY"  # Fourniture de service
    LEASED_TO = "LEASED_TO"  # Location

    # --- Relations Sécurité ---
    SECURES = "SECURES"  # Protection de zone
    GRANTS_ACCESS = "GRANTS_ACCESS"  # Droit d'accès

    # --- Relations Parking ---
    PARKED_AT = "PARKED_AT"  # Stationnement
    RESERVED_BY = "RESERVED_BY"  # Réservation

    # --- Relations Temporelles (implicites via propriétés) ---
    HAS_SYSTEM = "HAS_SYSTEM"  # Système technique associé
    MEASURES = "MEASURES"  # Ce que mesure un point

    # --- Relations Exploitation (Tickets/Workflow) ---
    HAS_TICKET = "HAS_TICKET"  # Ticket lié à un nœud
    HAS_EVENT = "HAS_EVENT"  # Événement sur un nœud
    HAS_NOTE = "HAS_NOTE"  # Note sur un nœud
    FOLLOWS_WORKFLOW = "FOLLOWS_WORKFLOW"  # Ticket suit un workflow
    HAS_STEP = "HAS_STEP"  # Workflow contient des étapes
    NEXT_STEP = "NEXT_STEP"  # Ordre des étapes

    # --- Relations Groupement ---
    BELONGS_TO_CONTEXT = "BELONGS_TO_CONTEXT"  # Appartenance multi-contexte
    HAS_CATEGORY = "HAS_CATEGORY"  # Context contient catégories
    HAS_GROUP = "HAS_GROUP"  # Category contient groupes
    MEMBER_OF = "MEMBER_OF"  # Élément membre d'un groupe
    HAS_NOMENCLATURE = "HAS_NOMENCLATURE"  # Profil/template de points

    # --- Relations Points de contrôle ---
    HAS_CONTROL_ENDPOINT = "HAS_CONTROL_ENDPOINT"  # Point de commande
    HAS_ENDPOINT = "HAS_ENDPOINT"  # Point de mesure
    COMMANDS = "COMMANDS"  # ControlEndpoint commande un équipement

    # --- Relations Attributs ---
    HAS_ATTRIBUTE = "HAS_ATTRIBUTE"  # Attribut structuré sur un nœud

    # --- Relations Data (données attachées) ---
    HAS_FILE = "HAS_FILE"  # Fichier documentaire lié
    HAS_TIMESERIES_ARCHIVE = "HAS_TIMESERIES_ARCHIVE"  # Historique archivé
    HAS_CHANGELOG = "HAS_CHANGELOG"  # Journal d'audit
    HAS_BIM_OBJECT = "HAS_BIM_OBJECT"  # Lien avec objet BIM
    HAS_ATTRIBUTE_CATEGORY = "HAS_ATTRIBUTE_CATEGORY"  # Catégorie d'attributs


# =============================================================================
# Quantités mesurables - Étendu pour tous les domaines
# =============================================================================

POINT_QUANTITIES = [
    # --- Environnement ---
    "temperature",
    "humidity",
    "co2",
    "pressure",
    "air_quality",
    "illuminance",
    "noise_level",

    # --- Énergie électrique ---
    "power",
    "voltage",
    "current",
    "energy",
    "power_factor",
    "frequency",

    # --- Fluides ---
    "flow",
    "water_consumption",
    "gas_consumption",
    "thermal_energy",

    # --- États/Commandes ---
    "status",
    "command",
    "setpoint",
    "mode",
    "alarm_state",

    # --- Occupation ---
    "occupancy",
    "people_count",
    "presence",
    "workspace_status",
    "space_reservation_status",

    # --- IT ---
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "network_throughput",
    "network_latency",

    # --- Sécurité ---
    "access_event",
    "intrusion_status",
    "camera_status",
    "ssi_status",

    # --- Parking ---
    "spot_status",
    "charging_power",
    "battery_level",

    # --- AV ---
    "av_status",
    "display_status",
    "audio_level",

    # --- Maintenance ---
    "asset_status",
    "runtime_hours",
    "maintenance_due",
]

# Quantités qui génèrent des timeseries continues (vs événements discrets)
TIMESERIES_QUANTITIES = {
    "temperature", "humidity", "co2", "pressure", "air_quality", "illuminance",
    "power", "voltage", "current", "energy", "power_factor",
    "flow", "water_consumption", "gas_consumption", "thermal_energy",
    "people_count", "cpu_usage", "memory_usage", "disk_usage",
    "network_throughput", "charging_power", "noise_level",
}

# Quantités qui sont des événements discrets (pas de timeseries continues)
EVENT_QUANTITIES = {
    "status", "command", "setpoint", "mode", "alarm_state",
    "occupancy", "presence", "workspace_status", "space_reservation_status",
    "access_event", "intrusion_status", "camera_status", "ssi_status",
    "spot_status", "av_status", "display_status", "asset_status",
    "maintenance_due", "battery_level", "runtime_hours", "audio_level",
}


# =============================================================================
# Dataclasses
# =============================================================================

@dataclass
class Node:
    """Nœud du graphe avec support multi-contexte.

    Patterns BOS:
    - context_ids: appartenance à plusieurs contextes simultanément
    - static_id: UUID persistant (vs dynamic_id runtime)
    - modification tracking: direct/indirect modification dates
    """
    id: str
    type: NodeType
    name: str
    properties: Dict[str, Any] = None
    context_ids: Set[str] = field(default_factory=set)  # Multi-context support
    static_id: Optional[str] = None  # UUID persistant
    created_at: Optional[int] = None  # Timestamp création
    modified_at: Optional[int] = None  # Timestamp dernière modification

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.static_id is None:
            self.static_id = self.id  # Par défaut, même que l'id

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le noeud en dictionnaire pour export.

        Le building_id est extrait des properties pour l'export,
        permettant le filtrage par scale (small=building 1, medium=1-5, large=tous).
        """
        return {
            "node_id": self.id,
            "static_id": self.static_id,
            "node_type": self.type.value,
            "name": self.name,
            "building_id": self.properties.get("building_id", 0),
            "context_ids": list(self.context_ids),
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "properties": self.properties,
        }


@dataclass
class Attribute:
    """Attribut structuré avec métadonnées.

    Pattern BOS: attributs groupés par catégories avec unités et dates.
    """
    label: str
    value: Any  # string | number | boolean
    unit: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None  # Type de donnée
    date: Optional[int] = None  # Timestamp de la valeur

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "value": self.value,
            "unit": self.unit,
            "category": self.category,
            "type": self.type,
            "date": self.date,
        }


@dataclass
class ControlEndpoint:
    """Point de commande (setpoint, mode, etc.).

    Distinction avec Endpoint (mesure):
    - ControlEndpoint: valeur qu'on peut écrire (setpoint température, mode CVC)
    - Endpoint: valeur lue (mesure capteur)
    """
    id: str
    name: str
    category: str  # Profil/type de point
    value: Any  # Valeur actuelle
    profile_name: Optional[str] = None
    writable: bool = True
    unit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "value": self.value,
            "profile_name": self.profile_name,
            "writable": self.writable,
            "unit": self.unit,
        }


@dataclass
class Endpoint:
    """Point de mesure (capteur, valeur lue).

    Distinction avec ControlEndpoint (commande):
    - Endpoint: valeur lue depuis un capteur
    - current_value: dernière valeur connue
    - has_timeseries: indique si ce point génère des timeseries
    """
    id: str
    name: str
    category: str  # Profil/type de point
    current_value: Any  # Dernière valeur
    unit: Optional[str] = None
    writable: bool = False
    has_timeseries: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "current_value": self.current_value,
            "unit": self.unit,
            "writable": self.writable,
            "has_timeseries": self.has_timeseries,
        }


@dataclass
class Ticket:
    """Ticket de maintenance/incident.

    Pattern BOS: tickets liés à des équipements/espaces avec workflow.
    """
    id: str
    title: str
    status: str  # open, in_progress, resolved, closed
    priority: str  # low, medium, high, critical
    entity_id: str  # Nœud lié (équipement, espace)
    created_at: int
    updated_at: Optional[int] = None
    assigned_to: Optional[str] = None
    workflow_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "entity_id": self.entity_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "assigned_to": self.assigned_to,
            "workflow_id": self.workflow_id,
        }


@dataclass
class Event:
    """Événement historique sur un nœud.

    Pattern BOS: traçabilité des actions et changements.
    """
    id: str
    date: int  # Timestamp
    type: str  # Type d'événement
    message: str
    linked_entity_id: str  # Nœud concerné
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "type": self.type,
            "message": self.message,
            "linked_entity_id": self.linked_entity_id,
            "user_id": self.user_id,
        }


@dataclass
class Note:
    """Note/commentaire sur un nœud.

    Pattern BOS: annotations manuelles par les utilisateurs.
    """
    id: str
    date: int  # Timestamp
    type: str  # Type de note
    message: str
    user_name: str
    linked_entity_id: str  # Nœud concerné

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "type": self.type,
            "message": self.message,
            "user_name": self.user_name,
            "linked_entity_id": self.linked_entity_id,
        }


@dataclass
class File:
    """Fichier lié à un nœud (documentation, plans, manuels).

    Inspiré du pattern Path/File des systèmes de graphe.
    """
    id: str
    name: str
    file_type: str  # pdf, jpeg, docx, dwg, ifc, etc.
    file_path: Optional[str] = None
    size_bytes: Optional[int] = None
    state: Optional[str] = None  # initial, uploading, completed, failed
    created_at: Optional[int] = None
    linked_entity_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "file_type": self.file_type,
            "file_path": self.file_path,
            "size_bytes": self.size_bytes,
            "state": self.state,
            "created_at": self.created_at,
            "linked_entity_id": self.linked_entity_id,
        }


@dataclass
class LogEntry:
    """Entrée de journal de changements.

    Pattern BOS: traçabilité des modifications sur les objets.
    """
    id: str
    timestamp: int
    action: str  # create, update, delete, access, command
    message: str
    entity_id: str
    user_id: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "action": self.action,
            "message": self.message,
            "entity_id": self.entity_id,
            "user_id": self.user_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }


@dataclass
class BimObject:
    """Objet BIM avec lien vers la maquette numérique.

    Inspiré du pattern ForgeFile avec URN, états et dérivés.
    """
    id: str
    name: str
    bim_file_id: str  # Référence au fichier BIM (IFC, RVT)
    external_id: str  # ID dans le viewer (Forge URN, etc.)
    dbid: Optional[str] = None  # Database ID du viewer
    state: Optional[str] = None  # initial, translating, completed, failed
    urn: Optional[str] = None  # URN pour accès viewer
    transform: Optional[Dict[str, float]] = None  # Position/rotation/scale

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "bim_file_id": self.bim_file_id,
            "external_id": self.external_id,
            "dbid": self.dbid,
            "state": self.state,
            "urn": self.urn,
            "transform": self.transform,
        }


@dataclass
class TimeSeriesArchive:
    """Archive de séries temporelles avec gestion de l'archivage.

    Inspiré du pattern TimeSeries avec archiveTime et frequency.
    """
    id: str
    name: str
    archive_time_hours: int = 24  # Durée avant archivage
    frequency_seconds: int = 300  # Fréquence d'échantillonnage (5min)
    point_id: str = ""  # Point source
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    sample_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "archive_time_hours": self.archive_time_hours,
            "frequency_seconds": self.frequency_seconds,
            "point_id": self.point_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "sample_count": self.sample_count,
        }


@dataclass
class Edge:
    src: str
    dst: str
    rel: RelationType

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'edge en dictionnaire pour export."""
        return {
            "src": self.src,
            "dst": self.dst,
            "rel": self.rel.value,
        }


@dataclass
class MeasuresEdge:
    src: str
    quantity: str


@dataclass
class TimeseriesPoint:
    point_id: str
    timestamp: int  # Unix timestamp
    value: float


@dataclass
class TimeseriesChunk:
    point_id: str
    start_time: int
    end_time: int
    frequency_seconds: int
    values: List[float]


# =============================================================================
# Règles de relations valides
# =============================================================================

def relation_targets() -> Dict[RelationType, List[Tuple[NodeType, NodeType]]]:
    """Couples source/destination autorisés pour les relations orientées.

    Cette fonction définit la grammaire du graphe : quelles relations
    sont valides entre quels types de nœuds.
    """
    return {
        # --- Relations Spatiales ---
        RelationType.CONTAINS: [
            # Hiérarchie spatiale principale
            (NodeType.SITE, NodeType.BUILDING),
            (NodeType.BUILDING, NodeType.FLOOR),
            (NodeType.FLOOR, NodeType.SPACE),
            (NodeType.SPACE, NodeType.ZONE),
            # Systèmes techniques
            (NodeType.SYSTEM, NodeType.EQUIPMENT),
            # Parking
            (NodeType.PARKING_ZONE, NodeType.PARKING_LEVEL),
            (NodeType.PARKING_LEVEL, NodeType.PARKING_SPOT),
            # IT
            (NodeType.DATACENTER, NodeType.RACK),
            # Sécurité
            (NodeType.SECURITY_ZONE, NodeType.ACCESS_POINT),
            (NodeType.SECURITY_ZONE, NodeType.CAMERA),
            # Organisation
            (NodeType.ORGANIZATION, NodeType.DEPARTMENT),
            (NodeType.DEPARTMENT, NodeType.TEAM),
        ],

        RelationType.LOCATED_IN: [
            # Équipements dans espaces
            (NodeType.EQUIPMENT, NodeType.SPACE),
            (NodeType.SENSOR, NodeType.SPACE),
            (NodeType.ACTUATOR, NodeType.SPACE),
            (NodeType.CONTROLLER, NodeType.SPACE),
            # IT dans datacenter
            (NodeType.RACK, NodeType.SPACE),
            (NodeType.SERVER, NodeType.RACK),
            (NodeType.NETWORK_DEVICE, NodeType.RACK),
            (NodeType.STORAGE, NodeType.RACK),
            # AV dans espaces
            (NodeType.AV_SYSTEM, NodeType.SPACE),
            (NodeType.DISPLAY, NodeType.SPACE),
            (NodeType.PROJECTOR, NodeType.SPACE),
            # Sécurité
            (NodeType.ACCESS_POINT, NodeType.SPACE),
            (NodeType.CAMERA, NodeType.SPACE),
            (NodeType.ALARM, NodeType.SPACE),
            # Parking
            (NodeType.CHARGING_STATION, NodeType.PARKING_LEVEL),
        ],

        RelationType.ADJACENT_TO: [
            (NodeType.SPACE, NodeType.SPACE),
            (NodeType.ZONE, NodeType.ZONE),
            (NodeType.FLOOR, NodeType.FLOOR),
        ],

        # --- Relations Fonctionnelles ---
        RelationType.HAS_PART: [
            (NodeType.EQUIPMENT, NodeType.EQUIPMENT),
            (NodeType.SYSTEM, NodeType.EQUIPMENT),
            (NodeType.AV_SYSTEM, NodeType.DISPLAY),
            (NodeType.AV_SYSTEM, NodeType.PROJECTOR),
            (NodeType.AV_SYSTEM, NodeType.SPEAKER),
            (NodeType.AV_SYSTEM, NodeType.CONFERENCE_UNIT),
        ],

        RelationType.HAS_POINT: [
            (NodeType.EQUIPMENT, NodeType.POINT),
            (NodeType.SENSOR, NodeType.POINT),
            (NodeType.ACTUATOR, NodeType.POINT),
            (NodeType.METER, NodeType.POINT),
            (NodeType.SERVER, NodeType.POINT),
            (NodeType.NETWORK_DEVICE, NodeType.POINT),
            (NodeType.CHARGING_STATION, NodeType.POINT),
        ],

        RelationType.SERVES: [
            (NodeType.EQUIPMENT, NodeType.SPACE),
            (NodeType.EQUIPMENT, NodeType.ZONE),
            (NodeType.SYSTEM, NodeType.BUILDING),
            (NodeType.SYSTEM, NodeType.FLOOR),
            (NodeType.AV_SYSTEM, NodeType.SPACE),
        ],

        RelationType.CONTROLS: [
            (NodeType.POINT, NodeType.EQUIPMENT),
            (NodeType.CONTROLLER, NodeType.ACTUATOR),
            (NodeType.CONTROLLER, NodeType.EQUIPMENT),
        ],

        RelationType.MONITORS: [
            (NodeType.SENSOR, NodeType.SPACE),
            (NodeType.SENSOR, NodeType.EQUIPMENT),
            (NodeType.CAMERA, NodeType.SPACE),
            (NodeType.CAMERA, NodeType.SECURITY_ZONE),
        ],

        RelationType.CONNECTS_TO: [
            (NodeType.EQUIPMENT, NodeType.EQUIPMENT),
            (NodeType.CONTROLLER, NodeType.SENSOR),
            (NodeType.NETWORK_DEVICE, NodeType.NETWORK_DEVICE),
            (NodeType.NETWORK_DEVICE, NodeType.SERVER),
            (NodeType.SERVER, NodeType.STORAGE),
        ],

        # --- Relations Énergétiques ---
        RelationType.FEEDS: [
            (NodeType.METER, NodeType.EQUIPMENT),
            (NodeType.METER, NodeType.METER),  # Arbre de distribution
            (NodeType.EQUIPMENT, NodeType.EQUIPMENT),
            (NodeType.ENERGY_ZONE, NodeType.METER),
            (NodeType.CHARGING_STATION, NodeType.VEHICLE),
        ],

        RelationType.METERS: [
            (NodeType.METER, NodeType.SPACE),
            (NodeType.METER, NodeType.ZONE),
            (NodeType.METER, NodeType.EQUIPMENT),
        ],

        # --- Relations IT/Réseau ---
        RelationType.HOSTS: [
            (NodeType.RACK, NodeType.SERVER),
            (NodeType.RACK, NodeType.NETWORK_DEVICE),
            (NodeType.RACK, NodeType.STORAGE),
            (NodeType.SERVER, NodeType.SYSTEM),  # Services hébergés
        ],

        RelationType.NETWORK_LINK: [
            (NodeType.NETWORK_DEVICE, NodeType.NETWORK_DEVICE),
            (NodeType.NETWORK_DEVICE, NodeType.SERVER),
            (NodeType.NETWORK_DEVICE, NodeType.STORAGE),
            (NodeType.NETWORK_DEVICE, NodeType.CONTROLLER),
        ],

        RelationType.STORES_DATA: [
            (NodeType.STORAGE, NodeType.SYSTEM),
            (NodeType.SERVER, NodeType.SYSTEM),
        ],

        # --- Relations Organisationnelles ---
        RelationType.BELONGS_TO: [
            (NodeType.PERSON, NodeType.TEAM),
            (NodeType.TEAM, NodeType.DEPARTMENT),
            (NodeType.DEPARTMENT, NodeType.ORGANIZATION),
            (NodeType.TENANT, NodeType.ORGANIZATION),
        ],

        RelationType.MANAGES: [
            (NodeType.PERSON, NodeType.TEAM),
            (NodeType.PERSON, NodeType.DEPARTMENT),
            (NodeType.PERSON, NodeType.EQUIPMENT),
            (NodeType.PERSON, NodeType.SPACE),
        ],

        RelationType.OCCUPIES: [
            (NodeType.TENANT, NodeType.SPACE),
            (NodeType.TENANT, NodeType.FLOOR),
            (NodeType.DEPARTMENT, NodeType.SPACE),
            (NodeType.TEAM, NodeType.SPACE),
        ],

        RelationType.WORKS_IN: [
            (NodeType.PERSON, NodeType.SPACE),
            (NodeType.PERSON, NodeType.BUILDING),
        ],

        # --- Relations Contractuelles ---
        RelationType.COVERED_BY: [
            (NodeType.EQUIPMENT, NodeType.CONTRACT),
            (NodeType.SYSTEM, NodeType.CONTRACT),
            (NodeType.BUILDING, NodeType.CONTRACT),
            (NodeType.SPACE, NodeType.LEASE),
        ],

        RelationType.PROVIDED_BY: [
            (NodeType.CONTRACT, NodeType.PROVIDER),
            (NodeType.LEASE, NodeType.PROVIDER),
            (NodeType.METER, NodeType.PROVIDER),  # Fournisseur d'énergie
        ],

        RelationType.LEASED_TO: [
            (NodeType.SPACE, NodeType.TENANT),
            (NodeType.FLOOR, NodeType.TENANT),
            (NodeType.PARKING_SPOT, NodeType.TENANT),
        ],

        # --- Relations Sécurité ---
        RelationType.SECURES: [
            (NodeType.ACCESS_POINT, NodeType.SPACE),
            (NodeType.ACCESS_POINT, NodeType.SECURITY_ZONE),
            (NodeType.CAMERA, NodeType.SECURITY_ZONE),
            (NodeType.ALARM, NodeType.SECURITY_ZONE),
            (NodeType.INTRUSION_DETECTOR, NodeType.SPACE),
        ],

        RelationType.GRANTS_ACCESS: [
            (NodeType.ACCESS_POINT, NodeType.PERSON),
            (NodeType.ACCESS_POINT, NodeType.TEAM),
            (NodeType.SECURITY_ZONE, NodeType.DEPARTMENT),
        ],

        # --- Relations Parking ---
        RelationType.PARKED_AT: [
            (NodeType.VEHICLE, NodeType.PARKING_SPOT),
        ],

        RelationType.RESERVED_BY: [
            (NodeType.PARKING_SPOT, NodeType.PERSON),
            (NodeType.PARKING_SPOT, NodeType.TENANT),
            (NodeType.SPACE, NodeType.PERSON),  # Réservation de salle
        ],

        # --- Relations Système ---
        RelationType.HAS_SYSTEM: [
            (NodeType.BUILDING, NodeType.SYSTEM),
            (NodeType.SPACE, NodeType.SYSTEM),
            (NodeType.FLOOR, NodeType.SYSTEM),
        ],

        RelationType.MEASURES: [
            (NodeType.POINT, NodeType.SENSOR),
            (NodeType.POINT, NodeType.METER),
        ],

        # --- Relations Exploitation (Tickets/Workflow) ---
        RelationType.HAS_TICKET: [
            (NodeType.EQUIPMENT, NodeType.TICKET),
            (NodeType.SPACE, NodeType.TICKET),
            (NodeType.SYSTEM, NodeType.TICKET),
            (NodeType.METER, NodeType.TICKET),
        ],

        RelationType.HAS_EVENT: [
            (NodeType.EQUIPMENT, NodeType.EVENT),
            (NodeType.SPACE, NodeType.EVENT),
            (NodeType.TICKET, NodeType.EVENT),
            (NodeType.POINT, NodeType.EVENT),
        ],

        RelationType.HAS_NOTE: [
            (NodeType.EQUIPMENT, NodeType.NOTE),
            (NodeType.SPACE, NodeType.NOTE),
            (NodeType.TICKET, NodeType.NOTE),
            (NodeType.PERSON, NodeType.NOTE),
        ],

        RelationType.FOLLOWS_WORKFLOW: [
            (NodeType.TICKET, NodeType.WORKFLOW),
            (NodeType.WORK_ORDER, NodeType.WORKFLOW),
        ],

        RelationType.HAS_STEP: [
            (NodeType.WORKFLOW, NodeType.WORKFLOW_STEP),
        ],

        RelationType.NEXT_STEP: [
            (NodeType.WORKFLOW_STEP, NodeType.WORKFLOW_STEP),
        ],

        # --- Relations Groupement ---
        RelationType.BELONGS_TO_CONTEXT: [
            # Tout nœud peut appartenir à un contexte
            (NodeType.EQUIPMENT, NodeType.CONTEXT),
            (NodeType.SPACE, NodeType.CONTEXT),
            (NodeType.POINT, NodeType.CONTEXT),
            (NodeType.SYSTEM, NodeType.CONTEXT),
            (NodeType.METER, NodeType.CONTEXT),
        ],

        RelationType.HAS_CATEGORY: [
            (NodeType.CONTEXT, NodeType.CATEGORY),
        ],

        RelationType.HAS_GROUP: [
            (NodeType.CATEGORY, NodeType.GROUP),
        ],

        RelationType.MEMBER_OF: [
            (NodeType.EQUIPMENT, NodeType.GROUP),
            (NodeType.SPACE, NodeType.GROUP),
            (NodeType.POINT, NodeType.GROUP),
            (NodeType.ENDPOINT, NodeType.GROUP),
            (NodeType.CONTROL_ENDPOINT, NodeType.GROUP),
        ],

        RelationType.HAS_NOMENCLATURE: [
            (NodeType.EQUIPMENT, NodeType.NOMENCLATURE),
            (NodeType.POINT, NodeType.NOMENCLATURE),
            (NodeType.ENDPOINT, NodeType.NOMENCLATURE),
        ],

        # --- Relations Points de contrôle ---
        RelationType.HAS_CONTROL_ENDPOINT: [
            (NodeType.EQUIPMENT, NodeType.CONTROL_ENDPOINT),
            (NodeType.SYSTEM, NodeType.CONTROL_ENDPOINT),
            (NodeType.SPACE, NodeType.CONTROL_ENDPOINT),
        ],

        RelationType.HAS_ENDPOINT: [
            (NodeType.EQUIPMENT, NodeType.ENDPOINT),
            (NodeType.SYSTEM, NodeType.ENDPOINT),
            (NodeType.SENSOR, NodeType.ENDPOINT),
            (NodeType.METER, NodeType.ENDPOINT),
        ],

        RelationType.COMMANDS: [
            (NodeType.CONTROL_ENDPOINT, NodeType.EQUIPMENT),
            (NodeType.CONTROL_ENDPOINT, NodeType.ACTUATOR),
        ],

        # --- Relations Attributs ---
        # Note: HAS_ATTRIBUTE n'est pas dans relation_targets car
        # les attributs sont gérés comme propriétés structurées, pas comme nœuds

        # --- Relations Data (données attachées) ---
        RelationType.HAS_FILE: [
            (NodeType.EQUIPMENT, NodeType.FILE),
            (NodeType.SPACE, NodeType.FILE),
            (NodeType.BUILDING, NodeType.FILE),
            (NodeType.CONTRACT, NodeType.FILE),
            (NodeType.TICKET, NodeType.FILE),
        ],

        RelationType.HAS_TIMESERIES_ARCHIVE: [
            (NodeType.POINT, NodeType.TIMESERIES_ARCHIVE),
            (NodeType.ENDPOINT, NodeType.TIMESERIES_ARCHIVE),
            (NodeType.METER, NodeType.TIMESERIES_ARCHIVE),
            (NodeType.SENSOR, NodeType.TIMESERIES_ARCHIVE),
        ],

        RelationType.HAS_CHANGELOG: [
            (NodeType.EQUIPMENT, NodeType.CHANGELOG),
            (NodeType.SPACE, NodeType.CHANGELOG),
            (NodeType.POINT, NodeType.CHANGELOG),
            (NodeType.TICKET, NodeType.CHANGELOG),
            (NodeType.PERSON, NodeType.CHANGELOG),
        ],

        RelationType.HAS_BIM_OBJECT: [
            (NodeType.EQUIPMENT, NodeType.BIM_OBJECT),
            (NodeType.SPACE, NodeType.BIM_OBJECT),
            (NodeType.BUILDING, NodeType.BIM_OBJECT),
            (NodeType.FLOOR, NodeType.BIM_OBJECT),
        ],

        RelationType.HAS_ATTRIBUTE_CATEGORY: [
            (NodeType.EQUIPMENT, NodeType.ATTRIBUTE_CATEGORY),
            (NodeType.SPACE, NodeType.ATTRIBUTE_CATEGORY),
            (NodeType.POINT, NodeType.ATTRIBUTE_CATEGORY),
            (NodeType.BUILDING, NodeType.ATTRIBUTE_CATEGORY),
        ],
    }


# =============================================================================
# Métriques de complexité du modèle
# =============================================================================

def get_model_complexity() -> Dict[str, Any]:
    """Retourne les métriques de complexité du modèle.

    Utilisé pour documenter la complexité dans l'article académique.
    """
    targets = relation_targets()
    return {
        "node_types_count": len(NodeType),
        "relation_types_count": len(RelationType),
        "point_quantities_count": len(POINT_QUANTITIES),
        "timeseries_quantities_count": len(TIMESERIES_QUANTITIES),
        "event_quantities_count": len(EVENT_QUANTITIES),
        "valid_relation_pairs": sum(len(pairs) for pairs in targets.values()),
        "node_types": [t.value for t in NodeType],
        "relation_types": [r.value for r in RelationType],
        "domains": [
            "Spatial", "Equipment", "Energy", "IT/Datacenter",
            "Audiovisual", "Parking", "Security", "Organization", "Contractual",
            "Exploitation", "Groupement"
        ],
        "patterns": [
            "Multi-context",
            "Structured Attributes",
            "ControlEndpoint vs Endpoint",
            "Category/Group Hierarchy",
            "Tickets/Workflow",
            "Notes/Events",
        ],
    }


# =============================================================================
# Types de contextes prédéfinis (multi-context pattern)
# =============================================================================

class ContextType(str, Enum):
    """Types de contextes pour le pattern multi-context.

    Un nœud peut appartenir à plusieurs contextes simultanément.
    Exemple: un équipement HVAC appartient à:
    - GEOGRAPHIC (localisation spatiale)
    - EQUIPMENT (inventaire technique)
    - ENERGY (distribution énergétique)
    - MAINTENANCE (suivi maintenance)
    """
    GEOGRAPHIC = "Geographic"  # Hiérarchie spatiale
    EQUIPMENT = "Equipment"  # Inventaire équipements
    IOT_NETWORK = "IoTNetwork"  # Réseau capteurs/actionneurs
    ENERGY = "Energy"  # Distribution énergétique
    MAINTENANCE = "Maintenance"  # Suivi maintenance
    SECURITY = "Security"  # Zones de sécurité
    ORGANIZATION = "Organization"  # Structure organisationnelle
    ROOMS_GROUP = "RoomsGroup"  # Groupement d'espaces
    EQUIPMENTS_GROUP = "EquipmentsGroup"  # Groupement d'équipements
    ENDPOINTS_GROUP = "EndpointsGroup"  # Groupement de points
    NOMENCLATURE_GROUP = "NomenclatureGroup"  # Profils/templates


# =============================================================================
# Profils de points (nomenclatures)
# =============================================================================

POINT_PROFILES = {
    # HVAC
    "temperature_sensor": {"quantity": "temperature", "unit": "°C", "writable": False},
    "temperature_setpoint": {"quantity": "setpoint", "unit": "°C", "writable": True},
    "humidity_sensor": {"quantity": "humidity", "unit": "%RH", "writable": False},
    "co2_sensor": {"quantity": "co2", "unit": "ppm", "writable": False},
    "hvac_mode": {"quantity": "mode", "unit": None, "writable": True},
    "hvac_status": {"quantity": "status", "unit": None, "writable": False},

    # Énergie
    "power_meter": {"quantity": "power", "unit": "kW", "writable": False},
    "energy_meter": {"quantity": "energy", "unit": "kWh", "writable": False},
    "voltage_meter": {"quantity": "voltage", "unit": "V", "writable": False},
    "current_meter": {"quantity": "current", "unit": "A", "writable": False},

    # Éclairage
    "light_level": {"quantity": "illuminance", "unit": "lux", "writable": False},
    "light_command": {"quantity": "command", "unit": "%", "writable": True},
    "light_status": {"quantity": "status", "unit": None, "writable": False},

    # Occupation
    "occupancy_sensor": {"quantity": "occupancy", "unit": None, "writable": False},
    "people_counter": {"quantity": "people_count", "unit": "count", "writable": False},

    # Sécurité
    "access_reader": {"quantity": "access_event", "unit": None, "writable": False},
    "alarm_status": {"quantity": "alarm_state", "unit": None, "writable": False},

    # IT
    "cpu_monitor": {"quantity": "cpu_usage", "unit": "%", "writable": False},
    "memory_monitor": {"quantity": "memory_usage", "unit": "%", "writable": False},
    "network_monitor": {"quantity": "network_throughput", "unit": "Mbps", "writable": False},
}
