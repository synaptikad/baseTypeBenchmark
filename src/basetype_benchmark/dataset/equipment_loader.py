"""Parser multi-format pour equipment.md et points.md.

Charge les définitions d'équipements depuis docs/Exploration/domains/
avec support des 3 formats de points détectés automatiquement.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EquipmentDef:
    """Définition d'un type d'équipement."""
    code: str
    domain: str  # Inféré du dossier parent
    haystack_tag: str
    brick_class: str
    description: str
    characteristics: Dict[str, str]
    points: List[dict]


# Fallbacks pour les points par défaut
DEFAULT_POINTS = [
    {"name": "status", "unit": "-", "range_min": 0, "range_max": 1, "frequency": 60, "type": "etat"},
    {"name": "value", "unit": "-", "range_min": 0, "range_max": 100, "frequency": 60, "type": "mesure"},
]

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

        # Ignorer les lignes non-table
        if not line.startswith('|'):
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
    header_words = ['point', 'code', 'nom', 'tag', 'unité', 'unit', 'description', 'plage', 'range']
    first_cell_lower = cells[0].lower() if cells else ""
    return any(w in first_cell_lower for w in header_words)


def build_column_map(cells: List[str], fmt: Optional[str]) -> Dict[str, int]:
    """Construit un mapping nom_colonne → index.

    Args:
        cells: Liste des cellules d'en-tête
        fmt: Format détecté (haystack, code, extended)

    Returns:
        Dict nom_colonne -> index
    """
    mapping = {}
    for i, cell in enumerate(cells):
        cell_lower = cell.lower().strip()
        if 'point' in cell_lower or 'code' in cell_lower:
            mapping['name'] = i
        elif 'unité' in cell_lower or 'unit' in cell_lower:
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


def get_equipment_by_type(defs: Dict[str, EquipmentDef], equipment_type: str) -> Optional[EquipmentDef]:
    """Trouve une définition d'équipement par type.

    Args:
        defs: Dict des définitions chargées
        equipment_type: Type d'équipement (ex: "FCU", "AHU")

    Returns:
        EquipmentDef correspondante ou None
    """
    for key, eq_def in defs.items():
        if eq_def.code == equipment_type or key.endswith(f"/{equipment_type}"):
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
