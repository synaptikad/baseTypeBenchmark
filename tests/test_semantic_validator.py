"""Tests for semantic validation.

Tests the SemanticValidator and SemanticNormalizer classes.
"""
import pytest
from pathlib import Path

from basetype_benchmark.runner.core.semantic_validator import (
    SemanticValidator,
    SemanticNormalizer,
    SemanticAnswer,
    SemanticComparison,
    SemanticStatus,
    QueryDefinition,
)
from basetype_benchmark.runner.benchmark.results import QueryResult


# Test fixtures
@pytest.fixture
def sample_definitions():
    """Sample semantic definitions for testing."""
    return {
        "Q1": QueryDefinition(
            query_id="Q1",
            question="Downstream equipment from meter",
            answer_type="set",
            semantic_key="id",
            exclude_parameter=True,
            parameter_name="meter_id",
            info_columns=["depth", "type", "name"],
        ),
        "Q8": QueryDefinition(
            query_id="Q8",
            question="Tenant total energy",
            answer_type="value",
            semantic_key="total_energy_kwh",
            tolerance={"default": 0.01, "M1": 0.05},
        ),
        "Q10": QueryDefinition(
            query_id="Q10",
            question="Security equipment per space",
            answer_type="aggregate",
            semantic_key=["space_id", "equipment_type"],
            value_columns=["equipment_count"],
        ),
        "Q7": QueryDefinition(
            query_id="Q7",
            question="Top 20 drift sensors",
            answer_type="ordered_set",
            semantic_key="point_id",
            order_by="variance",
            order_direction="desc",
            limit=20,
            rank_tolerance=2,
        ),
    }


@pytest.fixture
def normalizer(sample_definitions):
    """Create a normalizer with sample definitions."""
    return SemanticNormalizer(sample_definitions)


@pytest.fixture
def validator():
    """Create a validator with the real definitions file."""
    definitions_path = Path(__file__).parent.parent / "config" / "semantic_definitions.yaml"
    if definitions_path.exists():
        return SemanticValidator(definitions_path)
    return SemanticValidator()


class TestSemanticNormalizer:
    """Tests for SemanticNormalizer."""

    def test_normalize_set_excludes_source(self, normalizer):
        """Q1: Source parameter should be excluded from results."""
        # P1 result with source included (bug in query)
        p1_result = QueryResult(
            query_id="Q1",
            row_count=3,
            sample_rows=[
                {"id": "meter_1", "depth": 1, "type": "Meter", "name": "Main Meter"},
                {"id": "equip_1", "depth": 2, "type": "AHU", "name": "AHU 1"},
                {"id": "equip_2", "depth": 3, "type": "VAV", "name": "VAV 1"},
            ],
        )

        # M1 result without source (correct)
        m1_result = QueryResult(
            query_id="Q1",
            row_count=2,
            sample_rows=[
                {"id": "equip_1", "depth": 1, "type": "AHU", "name": "AHU 1"},
                {"id": "equip_2", "depth": 2, "type": "VAV", "name": "VAV 1"},
            ],
        )

        # Normalize both with parameter
        parameters = {"meter_id": "meter_1"}

        p1_answer = normalizer.normalize("Q1", p1_result, "P1", parameters)
        m1_answer = normalizer.normalize("Q1", m1_result, "M1", parameters)

        # After normalization, both should have same set (excluding source)
        assert p1_answer.data == {"equip_1", "equip_2"}
        assert m1_answer.data == {"equip_1", "equip_2"}

        # Metadata should show what was excluded
        assert "meter_1" in p1_answer.metadata.get("excluded", [])

    def test_normalize_set_without_exclusion(self, normalizer):
        """Set normalization without parameter exclusion."""
        # Create a definition without exclusion
        normalizer.definitions["Q5"] = QueryDefinition(
            query_id="Q5",
            question="Orphaned equipment",
            answer_type="set",
            semantic_key="id",
            exclude_parameter=False,
        )

        result = QueryResult(
            query_id="Q5",
            row_count=2,
            sample_rows=[
                {"id": "orphan_1", "type": "Sensor"},
                {"id": "orphan_2", "type": "Meter"},
            ],
        )

        answer = normalizer.normalize("Q5", result, "P1", {})

        assert answer.data == {"orphan_1", "orphan_2"}
        assert answer.answer_type == "set"

    def test_normalize_value(self, normalizer):
        """Q8: Value normalization."""
        result = QueryResult(
            query_id="Q8",
            row_count=1,
            sample_rows=[
                {"tenant_id": "tenant_1", "total_energy_kwh": 12345.67, "meter_count": 3},
            ],
        )

        answer = normalizer.normalize("Q8", result, "P1", {})

        assert answer.answer_type == "value"
        assert answer.data == 12345.67

    def test_normalize_aggregate(self, normalizer):
        """Q10: Aggregate normalization."""
        result = QueryResult(
            query_id="Q10",
            row_count=3,
            sample_rows=[
                {"space_id": "space_1", "equipment_type": "Camera", "equipment_count": 2},
                {"space_id": "space_1", "equipment_type": "Badge", "equipment_count": 1},
                {"space_id": "space_2", "equipment_type": "Camera", "equipment_count": 3},
            ],
        )

        answer = normalizer.normalize("Q10", result, "P1", {})

        assert answer.answer_type == "aggregate"
        # Key is tuple (space_id, equipment_type)
        assert ("space_1", "Camera") in answer.data
        assert answer.data[("space_1", "Camera")] == {"equipment_count": 2}

    def test_normalize_ordered_set(self, normalizer):
        """Q7: Ordered set normalization (top-N)."""
        result = QueryResult(
            query_id="Q7",
            row_count=3,
            sample_rows=[
                {"point_id": "pt_1", "variance": 100.0},
                {"point_id": "pt_2", "variance": 80.0},
                {"point_id": "pt_3", "variance": 60.0},
            ],
        )

        answer = normalizer.normalize("Q7", result, "P1", {})

        assert answer.answer_type == "ordered_set"
        # Should be sorted by variance desc
        assert answer.data[0][0] == "pt_1"  # First item
        assert answer.data[1][0] == "pt_2"
        assert answer.data[2][0] == "pt_3"

    def test_normalize_no_data(self, normalizer):
        """Handle missing data."""
        result = QueryResult(
            query_id="Q1",
            row_count=0,
            sample_rows=[],
        )

        answer = normalizer.normalize("Q1", result, "P1", {})

        assert answer.data is None
        assert answer.metadata.get("status") == "NO_DATA"


class TestSemanticValidator:
    """Tests for SemanticValidator."""

    def test_compare_identical_sets(self, validator):
        """Sets with identical items should be EQUIVALENT."""
        ref_result = QueryResult(
            query_id="Q1",
            row_count=2,
            sample_rows=[
                {"id": "equip_1"},
                {"id": "equip_2"},
            ],
        )
        cmp_result = QueryResult(
            query_id="Q1",
            row_count=2,
            sample_rows=[
                {"id": "equip_2"},  # Different order
                {"id": "equip_1"},
            ],
        )

        comparison = validator.validate("Q1", ref_result, "P1", cmp_result, "M1", {})

        assert comparison.status == SemanticStatus.EQUIVALENT

    def test_compare_sets_with_source_exclusion(self, validator):
        """Q1: P1 with source vs M1 without source should be EQUIVALENT after exclusion."""
        # P1 includes the source meter (bug)
        p1_result = QueryResult(
            query_id="Q1",
            row_count=3,
            sample_rows=[
                {"id": "meter_main_1"},  # Source - should be excluded
                {"id": "equip_1"},
                {"id": "equip_2"},
            ],
        )

        # M1 correctly excludes source
        m1_result = QueryResult(
            query_id="Q1",
            row_count=2,
            sample_rows=[
                {"id": "equip_1"},
                {"id": "equip_2"},
            ],
        )

        comparison = validator.validate(
            "Q1", p1_result, "P1", m1_result, "M1",
            {"meter_id": "meter_main_1"}
        )

        assert comparison.status == SemanticStatus.EQUIVALENT
        assert "Identical sets" in comparison.reason

    def test_compare_different_sets(self, validator):
        """Sets with different items should be MISMATCH."""
        ref_result = QueryResult(
            query_id="Q1",
            row_count=2,
            sample_rows=[
                {"id": "equip_1"},
                {"id": "equip_2"},
            ],
        )
        cmp_result = QueryResult(
            query_id="Q1",
            row_count=2,
            sample_rows=[
                {"id": "equip_1"},
                {"id": "equip_3"},  # Different!
            ],
        )

        comparison = validator.validate("Q1", ref_result, "P1", cmp_result, "M1", {})

        assert comparison.status == SemanticStatus.MISMATCH
        assert "equip_2" in str(comparison.details.get("only_in_ref", []))
        assert "equip_3" in str(comparison.details.get("only_in_cmp", []))

    def test_compare_values_within_tolerance(self, validator):
        """Values within tolerance should be EQUIVALENT."""
        ref_result = QueryResult(
            query_id="Q8",
            row_count=1,
            sample_rows=[{"total_energy_kwh": 1000.0}],
        )
        cmp_result = QueryResult(
            query_id="Q8",
            row_count=1,
            sample_rows=[{"total_energy_kwh": 1005.0}],  # 0.5% difference
        )

        comparison = validator.validate("Q8", ref_result, "P1", cmp_result, "M1", {})

        assert comparison.status == SemanticStatus.EQUIVALENT

    def test_compare_values_outside_tolerance(self, validator):
        """Values outside tolerance should be MISMATCH."""
        ref_result = QueryResult(
            query_id="Q8",
            row_count=1,
            sample_rows=[{"total_energy_kwh": 1000.0}],
        )
        cmp_result = QueryResult(
            query_id="Q8",
            row_count=1,
            sample_rows=[{"total_energy_kwh": 1100.0}],  # 10% difference
        )

        comparison = validator.validate("Q8", ref_result, "P1", cmp_result, "P2", {})

        assert comparison.status == SemanticStatus.MISMATCH

    def test_impossible_query(self, validator):
        """IMPOSSIBLE queries should return IMPOSSIBLE status."""
        ref_result = QueryResult(query_id="Q14", row_count=0, sample_rows=[])
        cmp_result = QueryResult(query_id="Q14", row_count=5, sample_rows=[])

        comparison = validator.validate("Q14", ref_result, "P1", cmp_result, "M1", {})

        assert comparison.status == SemanticStatus.IMPOSSIBLE

    def test_no_data_both(self, validator):
        """No data in both paradigms."""
        comparison = validator.validate("Q1", None, "P1", None, "M1", {})

        assert comparison.status == SemanticStatus.NO_DATA


class TestIntegration:
    """Integration tests with real definitions."""

    def test_load_definitions_file(self):
        """Test loading the semantic_definitions.yaml file."""
        definitions_path = Path(__file__).parent.parent / "config" / "semantic_definitions.yaml"

        if not definitions_path.exists():
            pytest.skip("semantic_definitions.yaml not found")

        validator = SemanticValidator(definitions_path)

        # Check some definitions loaded
        assert "Q1" in validator.definitions
        assert "Q8" in validator.definitions
        assert validator.definitions["Q1"].answer_type == "set"
        assert validator.definitions["Q8"].answer_type == "value"

    def test_q1_real_scenario(self):
        """Test Q1 with realistic data."""
        definitions_path = Path(__file__).parent.parent / "config" / "semantic_definitions.yaml"

        if not definitions_path.exists():
            pytest.skip("semantic_definitions.yaml not found")

        validator = SemanticValidator(definitions_path)

        # Simulate P1 result (includes source at depth=1)
        p1_result = QueryResult(
            query_id="Q1",
            row_count=418,
            sample_rows=[
                {"id": "meter_main_1", "type": "MainMeter", "name": "Building Main", "depth": 1},
                {"id": "sub_meter_1", "type": "SubMeter", "name": "Floor 1", "depth": 2},
                {"id": "sub_meter_2", "type": "SubMeter", "name": "Floor 2", "depth": 2},
                {"id": "ahu_1", "type": "AHU", "name": "AHU Floor 1", "depth": 3},
            ],
        )

        # Simulate M1 result (excludes source)
        m1_result = QueryResult(
            query_id="Q1",
            row_count=417,
            sample_rows=[
                {"id": "sub_meter_1", "type": "SubMeter", "name": "Floor 1", "depth": 1},
                {"id": "sub_meter_2", "type": "SubMeter", "name": "Floor 2", "depth": 1},
                {"id": "ahu_1", "type": "AHU", "name": "AHU Floor 1", "depth": 2},
            ],
        )

        comparison = validator.validate(
            "Q1", p1_result, "P1", m1_result, "M1",
            {"meter_id": "meter_main_1"}
        )

        # Should be equivalent after excluding source
        assert comparison.status == SemanticStatus.EQUIVALENT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
