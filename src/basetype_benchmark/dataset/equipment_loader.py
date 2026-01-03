"""Parser multi-format pour définitions d'équipements.

Charge depuis:
1. config/equipment/*.yaml (prioritaire, format validé)
2. docs/Exploration/domains/ (fallback, format markdown)
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml


# =============================================================================
# FRÉQUENCES SÉMANTIQUES → INTERVALLES (secondes)
# =============================================================================
FREQ_MAP = {
    "event": 0,       # Sur changement uniquement
    "fast": 60,       # 1 min - positions, vitesses
    "normal": 300,    # 5 min - températures, mesures courantes
    "slow": 900,      # 15 min - diagnostics, efficacité
    "energy": 900,    # 15 min - compteurs (réglementaire, pas de deadband)
    "daily": 86400,   # 24h - cumuls
}

# =============================================================================
# ALIAS : noms longs (distribution) → codes courts (YAML) ou noms Exploration
# =============================================================================
EQUIPMENT_ALIAS = {
    # HVAC
    "Thermostat": "TMP",
    "TemperatureSensor": "TMP",
    "CO2_Sensor": "CO2",
    "Occupancy_Sensor": "OCC",
    "DALI_Gateway": "DGW",
    "Dimmer": "DIM",
    "Emergency_Lighting": "EML",
    "ManualCallPoint": "MCP",
    "Lighting_Circuit": "LTC",
    "LED_Driver_DALI2": "LDD",
    # Electrical
    "EnergyMeter": "MTR",
    "SubMeter": "SMT",
    "ThermalMeter": "THM",
    "Transformer_HT_BT": "TRF",
    # Parking
    "ParkingSensorMagnetic": "PKS",
    "ParkingGuidanceController": "PKC",
    "EVChargerLevel2": "EVC",
    "BarrierGate": "BAR",
    "TicketDispenser": "TKD",
    "SpeedGate": "SPG",
    # Fire/Safety
    "FireExtinguisher": "FEX",
    "CO_Sensor": "AirQualitySensor",  # Proxy vers AirQualitySensor (HVAC)
    # AV - noms génériques vers Exploration
    "Microphone": "TableMicrophone",
    "Speaker": "CeilingSpeaker",
    "PeopleCounter": "Occupancy_Sensor",  # Proxy vers occupancy
}


@dataclass
class EquipmentDef:
    """Définition d'un type d'équipement."""
    code: str
    domain: str
    haystack_tag: str
    brick_class: str
    description: str
    characteristics: Dict[str, str]
    points: List[dict]


# Fallbacks pour les points par défaut
DEFAULT_POINTS = [
    {"name": "status", "unit": "-", "range_min": 0, "range_max": 1, "frequency": 0, "type": "etat"},
    {"name": "value", "unit": "-", "range_min": 0, "range_max": 100, "frequency": 300, "type": "mesure"},
]


# =============================================================================
# CHARGEMENT YAML (config/equipment/*.yaml)
# =============================================================================

def load_yaml_equipment(config_path: Path) -> Dict[str, EquipmentDef]:
    """Charge les définitions depuis config/equipment/*.yaml.

    Args:
        config_path: Chemin vers config/

    Returns:
        Dict code_équipement -> EquipmentDef
    """
    defs = {}
    equip_dir = config_path / "equipment"

    if not equip_dir.exists():
        return defs

    for yaml_file in equip_dir.glob("*.yaml"):
        eq_def = _parse_yaml_equipment(yaml_file)
        if eq_def:
            defs[eq_def.code] = eq_def

    return defs


def _parse_yaml_equipment(path: Path) -> Optional[EquipmentDef]:
    """Parse un fichier YAML d'équipement."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return None

    if not data or "equipment" not in data:
        return None

    eq = data["equipment"]
    points_raw = data.get("points", [])

    # Convertir les points au format interne
    points = [_convert_yaml_point(p) for p in points_raw]

    return EquipmentDef(
        code=eq.get("code", path.stem),
        domain=eq.get("domain", "Unknown"),
        haystack_tag=eq.get("haystack", ""),
        brick_class=eq.get("brick", ""),
        description=eq.get("desc", ""),
        characteristics={},
        points=points,
    )


def _convert_yaml_point(p: dict) -> dict:
    """Convertit un point YAML au format générateur."""
    freq_key = p.get("freq", "normal")
    frequency = FREQ_MAP.get(freq_key, 300)

    # Inférer range depuis quantity ou unit
    range_min, range_max = _infer_range(p)

    return {
        "name": p.get("id", "unknown"),
        "unit": p.get("unit", "-"),
        "range_min": range_min,
        "range_max": range_max,
        "frequency": frequency,
        "type": p.get("type", "mesure"),
        "freq_category": freq_key,  # Garder pour le simulateur
    }


def _infer_range(p: dict) -> tuple:
    """Infère les bornes min/max depuis quantity ou unit."""
    quantity = p.get("quantity", "").lower()
    unit = p.get("unit", "").lower()

    # Ranges par défaut selon quantity
    ranges = {
        "temperature": (10.0, 35.0),
        "humidity": (0.0, 100.0),
        "pressure": (0.0, 1000.0),
        "differential_pressure": (0.0, 500.0),
        "co2": (350.0, 2000.0),
        "speed": (0.0, 100.0),
        "position": (0.0, 100.0),
        "power": (0.0, 1000.0),
        "energy": (0.0, 100000.0),
        "flow": (0.0, 5000.0),
        "level": (0.0, 100.0),
        "voltage": (380.0, 420.0),
        "current": (0.0, 1000.0),
    }

    if quantity in ranges:
        return ranges[quantity]

    # Fallback par unit
    if "°c" in unit:
        return (10.0, 35.0)
    elif "%" in unit:
        return (0.0, 100.0)
    elif unit in ("pa", "mbar"):
        return (0.0, 1000.0)
    elif unit in ("ppm",):
        return (350.0, 2000.0)

    return (0.0, 100.0)

# Patterns de colonnes reconnus (français)
COLUMN_PATTERNS = {
    "haystack": ["point", "tag haystack", "unité", "plage typique", "fréquence"],
    "code": ["code", "nom", "quantité", "unité", "plage", "fréquence"],
    "extended": ["point", "description", "unité", "plage typique", "haystack tags", "brick class", "fréquence"],
}


def load_exploration(path: Path) -> Dict[str, EquipmentDef]:
    """Charge tous les équipements depuis docs/Exploration/domains/.

    Args:
        path: Chemin vers docs/Exploration/

    Returns:
        Dict clé = "Domain/EquipmentName" -> EquipmentDef
    """
    defs = {}
    domains_path = path / "domains"

    if not domains_path.exists():
        return defs

    for domain_dir in domains_path.iterdir():
        if not domain_dir.is_dir():
            continue
        domain_name = domain_dir.name  # HVAC, Electrical, etc.
        for equip_dir in domain_dir.iterdir():
            if not equip_dir.is_dir():
                continue
            key = f"{domain_name}/{equip_dir.name}"
            defs[key] = parse_equipment_dir(equip_dir, domain_name)

    return defs


def parse_equipment_dir(equip_dir: Path, domain: str) -> EquipmentDef:
    """Parse un dossier équipement.

    Args:
        equip_dir: Chemin vers le dossier de l'équipement
        domain: Nom du domaine (HVAC, Electrical, etc.)

    Returns:
        EquipmentDef avec les données parsées ou fallbacks
    """
    name = equip_dir.name
    code = name[:3].upper()
    haystack = f"{name.lower()}-equip"
    brick = ""
    description = ""
    characteristics = {}
    points = [p.copy() for p in DEFAULT_POINTS]

    # equipment.md
    equip_file = equip_dir / "equipment.md"
    if equip_file.exists():
        content = equip_file.read_text(encoding="utf-8", errors="ignore")
        code = extract(content, r'\*\*Code\*\*\s*:\s*(\w+)') or code
        haystack = extract(content, r'\*\*Haystack\*\*\s*:\s*`([^`]+)`') or haystack
        brick = extract(content, r'\*\*Brick\*\*\s*:\s*`([^`]+)`') or ""
        description = extract_section(content, "Description") or ""
        characteristics = parse_characteristics(content)

    # points.md (multi-format)
    points_file = equip_dir / "points.md"
    if points_file.exists():
        content = points_file.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_points_multiformat(content)
        if parsed:
            points = parsed

    return EquipmentDef(
        code=code, domain=domain, haystack_tag=haystack, brick_class=brick,
        description=description, characteristics=characteristics, points=points
    )


def detect_format(header_cells: List[str]) -> Optional[str]:
    """Détecte le format du tableau basé sur les colonnes.

    Args:
        header_cells: Liste des cellules d'en-tête

    Returns:
        Nom du format détecté ou None
    """
    header_lower = [c.lower().strip() for c in header_cells]

    # Chercher le pattern qui matche le mieux
    for pattern_name, pattern_cols in COLUMN_PATTERNS.items():
        matches = sum(1 for col in pattern_cols if any(col in h for h in header_lower))
        if matches >= 3:  # Au moins 3 colonnes qui matchent
            return pattern_name
    return None


def parse_points_multiformat(content: str) -> List[dict]:
    """Parse les tableaux de points (multi-tables, multi-formats).

    Args:
        content: Contenu du fichier points.md

    Returns:
        Liste de dictionnaires décrivant chaque point
    """
    points = []
    lines = content.split('\n')
    current_format = None
    current_section = "mesure"  # Par défaut
    col_indices = {}

    for i, line in enumerate(lines):
        line = line.strip()

        # Détecter les sections
        if line.startswith('## Points de Mesure') or line.startswith('### '):
            if 'mesure' in line.lower() or 'capteur' in line.lower():
                current_section = "mesure"
            elif 'commande' in line.lower() or 'actionneur' in line.lower():
                current_section = "commande"
            elif 'état' in line.lower() or 'status' in line.lower():
                current_section = "etat"
            elif 'alarme' in line.lower():
                current_section = "alarme"
            continue
        
        # Skip non-point sections (mappings, protocols, sources, etc.)
        if line.startswith('##') and ('mapping' in line.lower() or 'protocol' in line.lower() or 
                                       'source' in line.lower() or 'référence' in line.lower()):
            current_section = None  # Disable parsing until next valid section
            continue

        # Ignorer les lignes non-table ou si dans une section non-point
        if not line.startswith('|') or current_section is None:
            continue

        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) < 3:
            continue

        # Ligne séparateur (---)
        if '---' in line:
            continue

        # Détecter l'en-tête et le format
        if is_header_row(cells):
            current_format = detect_format(cells)
            col_indices = build_column_map(cells, current_format)
            continue

        # Parser la ligne selon le format détecté
        point = parse_point_row(cells, col_indices, current_section, current_format)
        if point:
            points.append(point)

    return points


def is_header_row(cells: List[str]) -> bool:
    """Détecte si c'est une ligne d'en-tête.

    Args:
        cells: Liste des cellules de la ligne

    Returns:
        True si c'est une ligne d'en-tête
    """
    if not cells:
        return False
    
    first_cell = cells[0].strip()
    # Exact matches for common header names
    exact_headers = ['Point', 'Code', 'Nom', 'Name']
    if first_cell in exact_headers:
        return True
    
    # Check if it looks like a header (short words, multiple columns with header-like names)
    # Exclude cells with numeric/measurement values (e.g., "0-120%", "1s")
    header_indicators = ['unité', 'unit', 'description', 'plage', 'range', 'tag', 'haystack', 'brick', 'fréquence']
    
    # Count header indicators, but only in cells without numeric values
    header_count = 0
    numeric_indicators = 0
    for cell in cells:
        cell_lower = cell.lower()
        # Skip cells with obvious data values (numbers, ranges, units)
        if any(c.isdigit() for c in cell) or cell in ('%', '-', 'kW', 'kWh', '°C', 'Pa', 'V', 'A'):
            numeric_indicators += 1
            continue
        if any(ind in cell_lower for ind in header_indicators):
            header_count += 1
    
    # If we have numeric/data values, it's probably not a header
    if numeric_indicators >= 2:
        return False
    
    # If multiple columns have header-like words, it's likely a header
    return header_count >= 2


def build_column_map(cells: List[str], fmt: Optional[str]) -> Dict[str, int]:
    """Construit un mapping nom_colonne → index.

    Args:
        cells: Liste des cellules d'en-tête
        fmt: Format détecté (haystack, code, extended)

    Returns:
        Dict nom_colonne -> index
    """
    mapping = {}
    name_column_priority = []  # Track candidates for name column
    
    for i, cell in enumerate(cells):
        cell_stripped = cell.strip()
        cell_lower = cell_stripped.lower()
        
        # Exact match for primary name columns (highest priority)
        if cell_stripped in ('Point', 'Code', 'Nom', 'Name'):
            name_column_priority.insert(0, i)  # Prepend (highest priority)
        # Partial match for name-like columns (lower priority)
        elif 'point' in cell_lower or 'code' in cell_lower or 'nom' in cell_lower:
            # Exclude tag columns (Haystack, Brick) from being used as name
            if 'haystack' not in cell_lower and 'brick' not in cell_lower and 'tag' not in cell_lower:
                name_column_priority.append(i)
        
        # Map other columns
        if 'unité' in cell_lower or 'unit' in cell_lower:
            mapping['unit'] = i
        elif 'plage' in cell_lower or 'range' in cell_lower:
            mapping['range'] = i
        elif 'fréquence' in cell_lower or 'freq' in cell_lower:
            mapping['frequency'] = i
        elif 'haystack' in cell_lower:
            mapping['haystack'] = i
        elif 'brick' in cell_lower:
            mapping['brick'] = i
        elif 'description' in cell_lower:
            mapping['description'] = i
    
    # Assign name column using priority list (first match = highest priority)
    if name_column_priority:
        mapping['name'] = name_column_priority[0]
    
    return mapping


def parse_point_row(cells: List[str], col_map: Dict[str, int], section: str, fmt: Optional[str]) -> Optional[dict]:
    """Parse une ligne de point.

    Args:
        cells: Liste des cellules de la ligne
        col_map: Mapping colonne -> index
        section: Type de section (mesure, commande, etat, alarme)
        fmt: Format détecté

    Returns:
        Dict décrivant le point ou None si invalide
    """
    if not cells or not col_map:
        return None

    name_idx = col_map.get('name', 0)
    name = cells[name_idx] if name_idx < len(cells) else None
    if not name or name.lower() in ('point', 'code', 'nom', '-'):
        return None

    # Unité
    unit_idx = col_map.get('unit')
    unit = cells[unit_idx] if unit_idx and unit_idx < len(cells) else "-"

    # Plage
    range_min, range_max = 0.0, 100.0
    range_idx = col_map.get('range')
    if range_idx and range_idx < len(cells):
        m = re.search(r'(-?[\d.]+)\s*[-–à]\s*(-?[\d.]+)', cells[range_idx])
        if m:
            try:
                range_min, range_max = float(m.group(1)), float(m.group(2))
            except ValueError:
                pass

    # Fréquence → secondes
    frequency = 60  # défaut
    freq_idx = col_map.get('frequency')
    if freq_idx and freq_idx < len(cells):
        frequency = parse_frequency(cells[freq_idx])

    return {
        "name": name,
        "unit": unit,
        "range_min": range_min,
        "range_max": range_max,
        "frequency": frequency,
        "type": section,
    }


def parse_frequency(freq_str: str) -> int:
    """Convertit une fréquence textuelle en secondes.

    Args:
        freq_str: Description de la fréquence (ex: "10s", "1 min", "COV")

    Returns:
        Fréquence en secondes (0 pour event-driven)
    """
    freq_str = freq_str.lower().strip()

    # Patterns communs
    if 'cov' in freq_str or 'event' in freq_str or 'on request' in freq_str:
        return 0  # Event-driven

    m = re.search(r'(\d+)\s*(s|sec|min|hour|h|m)', freq_str)
    if m:
        val, unit = int(m.group(1)), m.group(2)
        if unit in ('s', 'sec'):
            return val
        elif unit in ('min', 'm'):
            return val * 60
        elif unit in ('hour', 'h'):
            return val * 3600

    # Défaut si non parsable
    return 60


def extract_section(content: str, section: str) -> Optional[str]:
    """Extrait le contenu d'une section ## Section.

    Args:
        content: Contenu du fichier markdown
        section: Nom de la section à extraire

    Returns:
        Contenu de la section ou None
    """
    match = re.search(rf'## {section}\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    return match.group(1).strip() if match else None


def parse_characteristics(content: str) -> Dict[str, str]:
    """Parse la section Caractéristiques Techniques.

    Args:
        content: Contenu du fichier markdown

    Returns:
        Dict caractéristique -> valeur
    """
    chars = {}
    section = extract_section(content, "Caractéristiques Techniques Typiques")
    if section:
        for line in section.split('\n'):
            if ':' in line and line.strip().startswith('-'):
                key, val = line.split(':', 1)
                chars[key.strip('- ')] = val.strip()
    return chars


def extract(content: str, pattern: str) -> Optional[str]:
    """Extrait une valeur via regex.

    Args:
        content: Contenu à parser
        pattern: Pattern regex avec un groupe de capture

    Returns:
        Valeur capturée ou None
    """
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def resolve_equipment_type(equipment_type: str) -> str:
    """Résout un type d'équipement via alias si nécessaire.

    Args:
        equipment_type: Nom long ou code court

    Returns:
        Code court (ou le type original si pas d'alias)
    """
    return EQUIPMENT_ALIAS.get(equipment_type, equipment_type)


def get_equipment_by_type(defs: Dict[str, EquipmentDef], equipment_type: str) -> Optional[EquipmentDef]:
    """Trouve une définition d'équipement par type.

    Args:
        defs: Dict des définitions chargées
        equipment_type: Type d'équipement (ex: "FCU", "AHU", "DALI_Gateway")

    Returns:
        EquipmentDef correspondante ou None
    """
    # Résoudre alias si présent
    resolved = resolve_equipment_type(equipment_type)

    # Chercher par code résolu
    if resolved in defs:
        return defs[resolved]

    # Fallback: chercher par chemin (Domain/Name)
    for key, eq_def in defs.items():
        if eq_def.code == resolved or key.endswith(f"/{equipment_type}"):
            return eq_def
    return None


def get_equipment_for_domain(defs: Dict[str, EquipmentDef], domain: str) -> List[EquipmentDef]:
    """Liste tous les équipements d'un domaine.

    Args:
        defs: Dict des définitions chargées
        domain: Nom du domaine (HVAC, Electrical, etc.)

    Returns:
        Liste des EquipmentDef du domaine
    """
    return [eq_def for eq_def in defs.values() if eq_def.domain == domain]
