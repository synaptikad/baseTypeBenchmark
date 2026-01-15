"""
Dynamic Parameter Sampler - Benchmark BaseType V3

Extrait des IDs et valeurs valides depuis le dataset chargé
pour générer dynamiquement les paramètres de requêtes.
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
    tenant_id_alt: Optional[str] = None  # Second tenant for QW11/QW12

    # Point
    point_id: Optional[str] = None

    # Types
    source_type: Optional[str] = None
    tag_pattern: Optional[str] = None
    capability: Optional[str] = None

    # Special params for complex queries
    hvac_source_equipment_id: Optional[str] = None  # Q20
    hvac_target_space_id: Optional[str] = None      # Q20
    critical_equipment_id: Optional[str] = None     # Q21
    building_with_offices_id: Optional[str] = None  # Q13
    transformer_id: Optional[str] = None            # Q29
    evacuation_space_id: Optional[str] = None       # Q27
    domain: str = "HVAC"                            # Q26, Q32

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
            paradigm: P1, P2, M1, M2
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

        # Tenant (sample two different tenants for QW11/QW12)
        params.tenant_id = self._sample_id("tenant")
        params.tenant_id_alt = self._sample_different_id("tenant", params.tenant_id)

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

    def _sample_different_id(self, node_type: str, exclude_id: Optional[str]) -> Optional[str]:
        """Échantillonne un ID différent de exclude_id."""
        cache_key = f"ids_{node_type}"

        if cache_key not in self._cache:
            self._cache[cache_key] = self._fetch_ids(node_type)

        ids = self._cache[cache_key]
        if not ids:
            return None

        # Filter out the excluded ID
        remaining = [id for id in ids if id != exclude_id]
        if not remaining:
            return None
        return self.rng.choice(remaining)

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

    def _fetch_equipment_by_type(self, types: tuple) -> List[str]:
        """Récupère les IDs d'équipement par type."""
        try:
            if self.paradigm in ("P1", "P2"):
                return self._fetch_equipment_by_type_postgres(types)
            elif self.paradigm in ("M1", "M2"):
                return self._fetch_equipment_by_type_memgraph(types)
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


def get_params_for_query(
    query_id: str,
    sampled: SampledParams,
    file_params: Dict[str, Any] = None,
    paradigm: str = None
) -> Dict[str, Any]:
    """
    Retourne les paramètres appropriés pour une query donnée.

    Args:
        query_id: ID de la query (Q1, Q2, QW1, etc.)
        sampled: Paramètres échantillonnés (pour Q1-Q34)
        file_params: Paramètres bruts du YAML (pour QW queries avec données riches)
        paradigm: P1, P2, M1, M2 (pour adaptation paradigme-spécifique)

    Returns:
        Dict des paramètres pour cette query
    """
    file_params = file_params or {}

    # Pour les QW queries, utiliser directement les params riches du YAML
    if query_id.startswith("QW") and file_params:
        return _get_qw_params(query_id, file_params, paradigm, sampled)

    # Mapping query -> paramètres requis (Q1-Q34)
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
            "EQUIPMENT_ID": sampled.hvac_source_equipment_id or sampled.equipment_id,
            "SPACE_ID": sampled.hvac_target_space_id or sampled.space_id,
        },
        "Q21": {
            "EQUIPMENT_ID": sampled.critical_equipment_id or sampled.equipment_id,
            "SOURCE_TYPE": sampled.source_type,
        },
        "Q22": {"EQUIPMENT_ID": sampled.equipment_id},
        "Q23": {
            "EQUIPMENT_ID": sampled.equipment_id,
            "MAX_HOPS": sampled.max_hops,
        },
        # Q24-Q26: JSONB validation queries
        "Q24": {"EQUIPMENT_ID": sampled.equipment_id},
        "Q25": {"EQUIPMENT_ID": sampled.equipment_id},
        "Q26": {"DOMAIN": sampled.domain},
        # Q27-Q30: Graph-native extended
        "Q27": {"SPACE_ID": sampled.evacuation_space_id or sampled.space_id},
        "Q28": {"METER_ID": sampled.meter_id},
        "Q29": {"TRANSFORMER_ID": sampled.transformer_id or sampled.meter_id},
        "Q30": {"EQUIPMENT_ID": sampled.meter_id or sampled.equipment_id},  # Failure Impact Analysis
        # Q31-Q34: SQL-native
        "Q31": {
            "BUILDING_ID": sampled.building_id,
            "DATE_START": sampled.date_start,
            "DATE_END": sampled.date_end,
        },
        "Q32": {"DOMAIN": sampled.domain},
        "Q33": {"BUILDING_ID": sampled.building_id},
        "Q34": {
            "BUILDING_ID": sampled.building_id,
            "DATE_START": sampled.date_start,
            "DATE_END": sampled.date_end,
        },
        # Q35-Q38: Write validation queries (QW1-QW3, QW8)
        # Q35 is handled specially below based on paradigm
        "Q35": {},
        "Q36": {"NODE_ID": sampled.equipment_id},
        "Q37": {
            "SOURCE_ID": sampled.meter_id,
            "TARGET_ID": sampled.equipment_id,
        },
        "Q38": {
            "NODE_ID": sampled.equipment_id,
            "KEY_TO_REMOVE": "deprecated_protocol",
        },
        # Q39-Q41: Tenant validation queries
        "Q39": {"TENANT_ID": sampled.tenant_id},
        "Q40": {"TENANT_ID": sampled.tenant_id},
        "Q41": {"TENANT_ID": sampled.tenant_id},
    }

    # Special handling for Q35 based on paradigm
    # M2 uses timeseries validation (ts/Q35.sql), others use space reservation validation
    if query_id == "Q35":
        if paradigm == "M2":
            # M2 Q35: Timeseries validation - uses point_id and reference_date
            return {
                "POINT_ID": sampled.point_id,
                "REFERENCE_DATE": sampled.reference_date,
            }
        else:
            # P1, P2, M1 Q35: Space Reservation validation
            return {
                "QW1_SPACE_ID": file_params.get("qw1_space_id", sampled.space_id),
                "QW1_START_DATE": file_params.get("qw1_start_date", sampled.reference_date),
                "QW1_END_DATE": file_params.get("qw1_end_date", sampled.reference_date),
            }

    return query_params.get(query_id, {})


def _get_qw_params(
    query_id: str,
    file_params: Dict[str, Any],
    paradigm: str,
    sampled: SampledParams
) -> Dict[str, Any]:
    """
    Extrait les paramètres QW depuis file_params selon le paradigme.

    Le générateur produit des données riches (qw1_chunks, qw6_metadata_patch, etc.)
    Cette fonction les extrait dans le format attendu par chaque moteur.
    """
    # QW1: Space Reservation - creates OCCUPIES edge with dates
    if query_id == "QW1":
        return {
            "QW1_TENANT_ID": file_params.get("qw1_tenant_id", sampled.tenant_id),
            "QW1_SPACE_ID": file_params.get("qw1_space_id", sampled.space_id),
            "QW1_START_DATE": file_params.get("qw1_start_date", sampled.reference_date),
            "QW1_END_DATE": file_params.get("qw1_end_date", sampled.reference_date),
        }

    # QW2: Metadata Update (tag)
    if query_id == "QW2":
        return {
            "NODE_ID": file_params.get("qw2_node_id", sampled.equipment_id),
            "TAG_KEY": file_params.get("qw2_tag_key", "calibration_status"),
            "TAG_VALUE": file_params.get("qw2_tag_value", "verified"),
        }

    # QW3: Relation Mutation
    if query_id == "QW3":
        return {
            "SOURCE_ID": file_params.get("qw3_source_id", sampled.meter_id),
            "TARGET_ID": file_params.get("qw3_target_id", sampled.equipment_id),
            "REL_TYPE": file_params.get("qw3_rel_type", "FEEDS"),
        }

    # QW4: Maintenance Event Append
    if query_id == "QW4":
        return {
            "EQUIPMENT_ID": file_params.get("qw4_equipment_id", sampled.equipment_id),
            "EVENT": file_params.get("qw4_event", {
                "date": sampled.reference_date,
                "type": "preventive",
                "technician": "Tech_A"
            }),
        }

    # QW5: Deep Calibration Update
    if query_id == "QW5":
        return {
            "POINT_ID": file_params.get("qw5_point_id", sampled.point_id),
            "CALIBRATION_DATE": file_params.get("qw5_calibration_date", sampled.reference_date),
            "NEXT_DATE": file_params.get("qw5_next_date", "2025-06-01"),
            "TECHNICIAN": file_params.get("qw5_technician", "Calibration_Co"),
        }

    # QW6: Metadata Merge
    if query_id == "QW6":
        if paradigm in ("M1", "M2"):
            # Cypher SET direct - besoin equipment_id + reference_date
            return {
                "EQUIPMENT_ID": file_params.get("qw6_equipment_id", sampled.equipment_id),
                "REFERENCE_DATE": file_params.get("reference_date", sampled.reference_date),
            }
        else:
            # SQL jsonb_set - besoin equipment_id + metadata_patch
            return {
                "EQUIPMENT_ID": file_params.get("qw6_equipment_id", sampled.equipment_id),
                "METADATA_PATCH": file_params.get("qw6_metadata_patch", {
                    "firmware_version": "3.2.1",
                    "last_update": sampled.reference_date
                }),
            }

    # QW7: Add Capability
    if query_id == "QW7":
        return {
            "EQUIPMENT_ID": file_params.get("qw7_equipment_id", sampled.equipment_id),
            "NEW_CAPABILITY": file_params.get("qw7_new_capability", "demand_control_ventilation"),
        }

    # QW8: Remove Metadata Key
    if query_id == "QW8":
        return {
            "NODE_ID": file_params.get("qw8_node_id", sampled.equipment_id),
            "KEY_TO_REMOVE": file_params.get("qw8_key_to_remove", "deprecated_protocol"),
        }

    # QW9: Tenant Move-In
    if query_id == "QW9":
        return {
            "TENANT_ID": file_params.get("tenant_id", sampled.tenant_id),
            "SPACE_ID": file_params.get("space_id", sampled.space_id),
            "METER_ID": file_params.get("meter_id", sampled.meter_id),
        }

    # QW10: Tenant Move-Out
    if query_id == "QW10":
        return {
            "TENANT_ID": file_params.get("tenant_id", sampled.tenant_id),
            "SPACE_ID": file_params.get("space_id", sampled.space_id),
        }

    # QW11: Space Reassignment
    if query_id == "QW11":
        return {
            "SPACE_ID": file_params.get("space_id", sampled.space_id),
            "OLD_TENANT_ID": file_params.get("old_tenant_id", sampled.tenant_id),
            "NEW_TENANT_ID": file_params.get("new_tenant_id", sampled.tenant_id_alt),
        }

    # QW12: Tenant Merge
    if query_id == "QW12":
        return {
            "SOURCE_TENANT_ID": file_params.get("source_tenant_id", sampled.tenant_id),
            "TARGET_TENANT_ID": file_params.get("target_tenant_id", sampled.tenant_id_alt),
        }

    # Fallback: pas de params
    return {}
