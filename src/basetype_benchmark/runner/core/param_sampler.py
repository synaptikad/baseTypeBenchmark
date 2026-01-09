"""
Dynamic Parameter Sampler - Benchmark BaseType V3

Extrait des IDs et valeurs valides depuis le dataset chargé
pour remplacer les paramètres hardcodés de golden_answers.yaml.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import random


@dataclass
class SampledParams:
    """Paramètres échantillonnés depuis le dataset."""
    # Spatial
    building_id: Optional[str] = None
    floor_id: Optional[str] = None
    space_id: Optional[str] = None

    # Equipment
    equipment_id: Optional[str] = None
    meter_id: Optional[str] = None
    ups_id: Optional[str] = None

    # Tenant
    tenant_id: Optional[str] = None

    # Point
    point_id: Optional[str] = None

    # Types
    source_type: Optional[str] = None
    tag_pattern: Optional[str] = None
    capability: Optional[str] = None

    # Dates (from dataset or defaults)
    date_start: str = "2024-01-15T00:00:00Z"
    date_end: str = "2024-01-15T23:59:59Z"
    reference_date: str = "2024-06-01"

    # Numeric
    days_ahead: int = 90
    max_hops: int = 3
    co2_factor: float = 0.5
    device_id: int = 1234


class ParamSampler:
    """
    Échantillonne des paramètres valides depuis une DB.

    Fonctionne avec P1/P2 (Postgres) et M1/M2 (Memgraph).
    """

    def __init__(self, paradigm: str, runner, seed: int = 42):
        """
        Args:
            paradigm: P1, P2, M1, M2, O2
            runner: Runner instance avec connexion DB active
            seed: Seed pour reproductibilité
        """
        self.paradigm = paradigm
        self.runner = runner
        self.rng = random.Random(seed)
        self._cache: Dict[str, List[str]] = {}

    def sample(self) -> SampledParams:
        """Échantillonne un set complet de paramètres."""
        params = SampledParams()

        # Spatial hierarchy
        params.building_id = self._sample_id("building")
        params.floor_id = self._sample_id("floor")
        params.space_id = self._sample_id("space")

        # Equipment
        params.equipment_id = self._sample_id("equipment")
        params.meter_id = self._sample_equipment_by_type("MainMeter", "SubMeter", "Meter")
        params.ups_id = self._sample_equipment_by_type("UPS")

        # Tenant
        params.tenant_id = self._sample_id("tenant")

        # Point
        params.point_id = self._sample_id("point")

        # Source type for Q21
        params.source_type = "MainMeter"

        # Tag pattern for Q16
        params.tag_pattern = "^brick:"

        # Capability for Q17
        params.capability = self._sample_capability()

        return params

    def _sample_id(self, node_type: str) -> Optional[str]:
        """Échantillonne un ID d'un type de nœud."""
        cache_key = f"ids_{node_type}"

        if cache_key not in self._cache:
            self._cache[cache_key] = self._fetch_ids(node_type)

        ids = self._cache[cache_key]
        if not ids:
            return None
        return self.rng.choice(ids)

    def _sample_equipment_by_type(self, *types: str) -> Optional[str]:
        """Échantillonne un ID d'équipement par type."""
        cache_key = f"equip_{'_'.join(types)}"

        if cache_key not in self._cache:
            self._cache[cache_key] = self._fetch_equipment_by_type(types)

        ids = self._cache[cache_key]
        if not ids:
            return None
        return self.rng.choice(ids)

    def _sample_capability(self) -> str:
        """Retourne une capability commune."""
        # On peut aussi la chercher dans la DB
        return "humidity_control"

    def _fetch_ids(self, node_type: str) -> List[str]:
        """Récupère les IDs d'un type de nœud depuis la DB."""
        try:
            if self.paradigm in ("P1", "P2"):
                return self._fetch_ids_postgres(node_type)
            elif self.paradigm in ("M1", "M2"):
                return self._fetch_ids_memgraph(node_type)
            elif self.paradigm == "O2":
                return self._fetch_ids_oxigraph(node_type)
            else:
                return []
        except Exception:
            return []

    def _fetch_ids_postgres(self, node_type: str) -> List[str]:
        """Récupère les IDs depuis Postgres (P1 ou P2)."""
        # P2 uses a single 'nodes' table with node_type column
        if self.paradigm == "P2":
            type_map = {
                "building": "Building",
                "floor": "Floor",
                "space": "Space",
                "equipment": "Equipment",
                "tenant": "Tenant",
                "point": "Point",
            }
            node_type_val = type_map.get(node_type.lower())
            if not node_type_val:
                return []

            query = "SELECT id FROM nodes WHERE node_type = %s LIMIT 100"
            try:
                result = self.runner.execute(query, (node_type_val,), timeout_seconds=5.0)
                return [row.get("id") or row.get(0) for row in result.rows if row]
            except Exception:
                return []

        # P1 uses separate tables (buildings, equipment, points, etc.)
        table_map = {
            "building": "buildings",
            "floor": "floors",
            "space": "spaces",
            "equipment": "equipment",
            "tenant": "tenants",
            "point": "points",
        }

        table = table_map.get(node_type.lower())
        if not table:
            return []

        query = f"SELECT id FROM {table} LIMIT 100"

        try:
            result = self.runner.execute(query, (), timeout_seconds=5.0)
            return [row.get("id") or row.get(0) for row in result.rows if row]
        except Exception:
            return []

    def _fetch_ids_memgraph(self, node_type: str) -> List[str]:
        """Récupère les IDs depuis Memgraph."""
        label_map = {
            "building": "Building",
            "floor": "Floor",
            "space": "Space",
            "equipment": "Equipment",
            "tenant": "Tenant",
            "point": "Point",
        }

        label = label_map.get(node_type.lower())
        if not label:
            return []

        query = f"MATCH (n:{label}) RETURN n.id AS id LIMIT 100"

        try:
            result = self.runner.execute(query, {}, timeout_seconds=5.0)
            return [row.get("id") for row in result.rows if row and row.get("id")]
        except Exception:
            return []

    def _fetch_ids_oxigraph(self, node_type: str) -> List[str]:
        """Récupère les IDs depuis Oxigraph (SPARQL)."""
        type_map = {
            "building": "Building",
            "floor": "Floor",
            "space": "Space",
            "equipment": "Equipment",
            "tenant": "Tenant",
            "point": "Point",
        }

        rdf_type = type_map.get(node_type.lower())
        if not rdf_type:
            return []

        # SPARQL query to fetch IDs by type
        query = f"""PREFIX btb: <http://basetype.benchmark/ontology#>
SELECT ?id WHERE {{
    ?node a btb:{rdf_type} .
    ?node btb:id ?id .
}} LIMIT 100"""

        try:
            result = self.runner.execute(query, {}, timeout_seconds=5.0)
            return [row.get("id") for row in result.rows if row and row.get("id")]
        except Exception:
            return []

    def _fetch_equipment_by_type(self, types: tuple) -> List[str]:
        """Récupère les IDs d'équipement par type."""
        try:
            if self.paradigm in ("P1", "P2"):
                return self._fetch_equipment_by_type_postgres(types)
            elif self.paradigm in ("M1", "M2"):
                return self._fetch_equipment_by_type_memgraph(types)
            elif self.paradigm == "O2":
                return self._fetch_equipment_by_type_oxigraph(types)
            else:
                return []
        except Exception:
            return []

    def _fetch_equipment_by_type_postgres(self, types: tuple) -> List[str]:
        """Récupère les IDs d'équipement par type depuis Postgres (P1 ou P2)."""
        placeholders = ", ".join(["%s"] * len(types))

        # P2 uses nodes table with JSONB data column
        if self.paradigm == "P2":
            query = f"""
                SELECT id FROM nodes
                WHERE node_type = 'Equipment'
                  AND data->>'equipment_type' IN ({placeholders})
                LIMIT 50
            """
        else:
            # P1 uses equipment table
            query = f"SELECT id FROM equipment WHERE equipment_type IN ({placeholders}) LIMIT 50"

        try:
            result = self.runner.execute(query, types, timeout_seconds=5.0)
            return [row.get("id") or row.get(0) for row in result.rows if row]
        except Exception:
            return []

    def _fetch_equipment_by_type_memgraph(self, types: tuple) -> List[str]:
        """Récupère les IDs d'équipement par type depuis Memgraph."""
        types_list = list(types)
        query = """
        MATCH (eq:Equipment)
        WHERE eq.equipment_type IN $types
        RETURN eq.id AS id LIMIT 50
        """

        try:
            result = self.runner.execute(query, {"types": types_list}, timeout_seconds=5.0)
            return [row.get("id") for row in result.rows if row and row.get("id")]
        except Exception:
            return []

    def _fetch_equipment_by_type_oxigraph(self, types: tuple) -> List[str]:
        """Récupère les IDs d'équipement par type depuis Oxigraph (SPARQL)."""
        # Build VALUES clause for types filter
        types_values = " ".join(f'"{t}"' for t in types)

        query = f"""PREFIX btb: <http://basetype.benchmark/ontology#>
SELECT ?id WHERE {{
    VALUES ?equipType {{ {types_values} }}
    ?eq a btb:Equipment .
    ?eq btb:equipmentType ?equipType .
    ?eq btb:id ?id .
}} LIMIT 50"""

        try:
            result = self.runner.execute(query, {}, timeout_seconds=5.0)
            return [row.get("id") for row in result.rows if row and row.get("id")]
        except Exception:
            return []


def get_params_for_query(query_id: str, sampled: SampledParams) -> Dict[str, Any]:
    """
    Retourne les paramètres appropriés pour une query donnée.

    Args:
        query_id: ID de la query (Q1, Q2, etc.)
        sampled: Paramètres échantillonnés

    Returns:
        Dict des paramètres pour cette query
    """
    # Mapping query -> paramètres requis
    query_params = {
        "Q1": {"METER_ID": sampled.meter_id},
        "Q2": {"EQUIPMENT_ID": sampled.equipment_id},
        "Q3": {"SPACE_ID": sampled.space_id},
        "Q4": {"FLOOR_ID": sampled.floor_id},
        "Q5": {},  # Pas de paramètres
        "Q6": {
            "POINT_ID": sampled.point_id,
            "DATE_START": sampled.date_start,
            "DATE_END": sampled.date_end,
        },
        "Q7": {
            "BUILDING_ID": sampled.building_id,
            "DATE_START": sampled.date_start,
            "DATE_END": sampled.date_end,
        },
        "Q8": {
            "TENANT_ID": sampled.tenant_id,
            "DATE_START": sampled.date_start,
            "DATE_END": sampled.date_end,
        },
        "Q9": {
            "TENANT_ID": sampled.tenant_id,
            "DATE_START": sampled.date_start,
            "DATE_END": sampled.date_end,
            "CO2_FACTOR": sampled.co2_factor,
        },
        "Q10": {"BUILDING_ID": sampled.building_id},
        "Q11": {"UPS_ID": sampled.ups_id},
        "Q12": {
            "BUILDING_ID": sampled.building_id,
            "DATE_START": sampled.date_start,
            "DATE_END": sampled.date_end,
        },
        "Q13": {
            "BUILDING_ID": sampled.building_id,
            "DATE_START": sampled.date_start,
            "DATE_END": sampled.date_end,
        },
        "Q14": {"DEVICE_ID": sampled.device_id},
        "Q15": {
            "DAYS_AHEAD": sampled.days_ahead,
            "REFERENCE_DATE": sampled.reference_date,
        },
        "Q16": {"TAG_PATTERN": sampled.tag_pattern},
        "Q17": {"CAPABILITY": sampled.capability},
        "Q18": {
            "METER_ID": sampled.meter_id,
            "REFERENCE_DATE": sampled.reference_date,
        },
        "Q19": {"EQUIPMENT_ID": sampled.equipment_id},
        "Q20": {
            "EQUIPMENT_ID": sampled.equipment_id,
            "SPACE_ID": sampled.space_id,
        },
        "Q21": {
            "EQUIPMENT_ID": sampled.equipment_id,
            "SOURCE_TYPE": sampled.source_type,
        },
        "Q22": {"EQUIPMENT_ID": sampled.equipment_id},
        "Q23": {
            "SPACE_ID": sampled.space_id,
            "MAX_HOPS": sampled.max_hops,
        },
    }

    return query_params.get(query_id, {})
