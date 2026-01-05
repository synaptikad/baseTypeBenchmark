"""Base class for paradigm-specific parameter generators.

This module defines the abstract interface that all paradigm-specific
parameter generators must implement. The Strategy Pattern allows each
database paradigm (SQL, Cypher, SPARQL) to use its idiomatic syntax
for pattern matching, date formatting, etc.

Academic rationale:
- Reproducibility: Each paradigm's parameter generation is documented separately
- Extensibility: Adding a new paradigm (e.g., Gremlin) = one new file
- Comparability: Differences between paradigms are explicit, not hidden in conditionals
- Validation: Unit tests can verify each paradigm independently
"""

import random
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from ..params_core import (
    extract_params_from_query,
    get_query_params,
    extract_dataset_info,
    extract_dataset_info_from_parquet,
    extract_timeseries_range,
    extract_timeseries_range_from_parquet,
)


class ParamGenerator(ABC):
    """Abstract base class for paradigm-specific parameter generation.

    Each paradigm (SQL, Cypher, SPARQL) implements this interface to provide
    idiomatic parameter values that leverage each database's native capabilities.

    Attributes:
        paradigm: Name of the paradigm (sql, cypher, sparql)
        scenarios: List of scenario codes using this paradigm
    """

    paradigm: str = "base"
    scenarios: List[str] = []

    # Base space type prefixes (without paradigm-specific wildcards)
    BASE_SPACE_TYPE_PREFIXES = ["office_", "meeting_"]
    BASE_SPACE_TYPE_EXACT = ["conference"]

    @abstractmethod
    def transform_space_type(self, prefix: str, is_exact: bool = False) -> str:
        """Transform a space type prefix to paradigm-specific syntax.

        Args:
            prefix: Base prefix (e.g., "office_")
            is_exact: If True, match exactly (no wildcard)

        Returns:
            Paradigm-specific pattern string

        Examples:
            SQL: "office_" -> "office_%" (LIKE wildcard)
            Cypher: "office_" -> "office_" (STARTS WITH, no wildcard needed)
            SPARQL: "office_" -> "office_" (STRSTARTS, no wildcard needed)
        """
        pass

    @abstractmethod
    def format_date(self, timestamp: int) -> str:
        """Format a Unix timestamp for this paradigm.

        Args:
            timestamp: Unix timestamp (seconds since epoch)

        Returns:
            Paradigm-specific date string

        Examples:
            SQL: 1704067200 -> "2024-01-01T00:00:00+00:00" (ISO 8601)
            Cypher: 1704067200 -> "1704067200" (Unix timestamp as string)
            SPARQL: 1704067200 -> "2024-01-01" (xsd:date format)
        """
        pass

    def get_space_type_values(self, rng: random.Random) -> str:
        """Generate a space type pattern value for this paradigm.

        Uses the paradigm-specific transform_space_type method.

        Args:
            rng: Random number generator for reproducibility

        Returns:
            Space type pattern appropriate for this paradigm
        """
        # Combine prefixes and exact matches
        all_options = [
            (prefix, False) for prefix in self.BASE_SPACE_TYPE_PREFIXES
        ] + [
            (exact, True) for exact in self.BASE_SPACE_TYPE_EXACT
        ]

        prefix, is_exact = rng.choice(all_options)
        return self.transform_space_type(prefix, is_exact)

    def generate_variant(
        self,
        params: List[str],
        dataset_info: Dict,
        rng: random.Random,
        ts_start: int,
        ts_end: int,
        query_id: str,
        variant_index: int,
        n_variants: int,
    ) -> Dict:
        """Generate a single parameter variant.

        This method handles common parameter generation logic,
        delegating paradigm-specific transforms to subclass methods.

        Args:
            params: List of parameter names to generate
            dataset_info: Dataset information (IDs by type)
            rng: Seeded random generator
            ts_start: Dataset start timestamp
            ts_end: Dataset end timestamp
            query_id: Query identifier (Q1, Q2, etc.)
            variant_index: Index of this variant (0 to n_variants-1)
            n_variants: Total number of variants

        Returns:
            Dict mapping parameter names to values
        """
        variant = {}

        for param in params:
            if param == "meter_id":
                meters = dataset_info.get("meters", [])
                variant[param] = rng.choice(meters) if meters else "meter_default"

            elif param == "equipment_id":
                equipment = dataset_info.get("equipment", [])
                variant[param] = rng.choice(equipment) if equipment else "eq_default"

            elif param == "space_id":
                spaces = dataset_info.get("spaces", [])
                variant[param] = rng.choice(spaces) if spaces else "space_default"

            elif param == "floor_id":
                floors = dataset_info.get("floors", [])
                variant[param] = rng.choice(floors) if floors else "floor_default"

            elif param == "building_id":
                buildings = dataset_info.get("buildings", [])
                variant[param] = rng.choice(buildings) if buildings else "bldg_default"

            elif param == "tenant_id":
                tenants = dataset_info.get("tenants", [])
                variant[param] = rng.choice(tenants) if tenants else "tenant_default"

            elif param == "zone_id":
                zones = dataset_info.get("zones", [])
                variant[param] = rng.choice(zones) if zones else "zone_default"

            elif param == "point_id":
                points = dataset_info.get("points", [])
                variant[param] = rng.choice(points) if points else "point_default"

            elif param == "space_type":
                variant[param] = self.get_space_type_values(rng)

            elif param == "date_start":
                ts = self._compute_date_start(
                    ts_start, ts_end, query_id, variant_index, n_variants
                )
                variant[param] = self.format_date(ts)

            elif param == "date_end":
                ts = self._compute_date_end(
                    ts_start, ts_end, query_id, variant_index, n_variants
                )
                variant[param] = self.format_date(ts)

        return variant

    def _compute_date_start(
        self,
        ts_start: int,
        ts_end: int,
        query_id: str,
        variant_index: int,
        n_variants: int,
    ) -> int:
        """Compute date_start timestamp for a variant."""
        data_duration_days = (ts_end - ts_start) / 86400 if ts_end > ts_start else 2

        # Adapt window to query type and available data
        if query_id == "Q7":
            ideal_window_hours = 12 if data_duration_days <= 2 else 24 * 7
            ideal_window = ideal_window_hours / 24
        elif query_id in ["Q6", "Q12", "Q13"]:
            ideal_window_hours = 6 if data_duration_days <= 2 else 24
            ideal_window = ideal_window_hours / 24
        else:
            ideal_window = 30

        window_days = min(ideal_window, max(0.25, data_duration_days - 0.1))

        # Sliding offset: divide available range by n_variants
        max_offset = max(0, data_duration_days - window_days)
        offset_days = (max_offset / max(1, n_variants - 1)) * variant_index if n_variants > 1 else 0

        return int(ts_start + offset_days * 86400)

    def _compute_date_end(
        self,
        ts_start: int,
        ts_end: int,
        query_id: str,
        variant_index: int,
        n_variants: int,
    ) -> int:
        """Compute date_end timestamp for a variant."""
        data_duration_days = (ts_end - ts_start) / 86400 if ts_end > ts_start else 2

        ideal_window = 7 if query_id == "Q7" else 1 if query_id in ["Q6", "Q12"] else 30
        window_days = min(ideal_window, max(1, data_duration_days - 0.5))

        max_offset = max(0, data_duration_days - window_days)
        offset_days = (max_offset / max(1, n_variants - 1)) * variant_index if n_variants > 1 else 0

        return int(ts_start + (offset_days + window_days) * 86400)

    def generate_variants(
        self,
        query_id: str,
        profile: str,
        dataset_info: Dict,
        seed: int = 42,
        n_variants: int = None,
        queries_dir: Path = None,
        scenario: str = None,
    ) -> List[Dict]:
        """Generate parameter variants for a query.

        Args:
            query_id: Query identifier (Q1, Q2, etc.)
            profile: Dataset profile (small-2d, medium-1w, etc.)
            dataset_info: Dataset information from extract_dataset_info()
            seed: Random seed for reproducibility
            n_variants: Number of variants (None = infer from profile)
            queries_dir: Path to queries/ directory
            scenario: Scenario code (uses first from self.scenarios if None)

        Returns:
            List of parameter dicts, one per variant
        """
        if scenario is None:
            scenario = self.scenarios[0] if self.scenarios else "P1"

        if queries_dir is None:
            queries_dir = Path("queries")

        params = get_query_params(query_id, queries_dir, scenario)
        if not params:
            return [{}]

        # Determine n_variants from profile if not specified
        if n_variants is None:
            scale = profile.split("-")[0] if "-" in profile else profile
            n_variants = {"small": 3, "medium": 5, "large": 10}.get(scale, 3)

        # Get timestamp range
        ts_start = dataset_info.get("ts_start", 0)
        ts_end = dataset_info.get("ts_end", 0)

        if ts_end == 0:
            ts_end = int(datetime.now(timezone.utc).timestamp())
        if ts_start == 0:
            ts_start = ts_end - 7 * 86400

        rng = random.Random(seed)
        variants = []

        for i in range(n_variants):
            variant = self.generate_variant(
                params, dataset_info, rng,
                ts_start, ts_end, query_id, i, n_variants
            )
            variants.append(variant)

        return variants
