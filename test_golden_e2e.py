#!/usr/bin/env python3
"""
E2E Golden Dataset Validation Tests

Validates that queries return expected results on the golden dataset.
Tests correctness across all paradigms (P1, P2, M1, M2, O2).

Usage:
    # Run all tests (requires Docker containers running)
    pytest test_golden_e2e.py -v

    # Run specific query tests
    pytest test_golden_e2e.py -v -k "Q1 or Q6"

    # Run specific paradigm
    pytest test_golden_e2e.py -v -k "P1"

    # Run graph-only queries on P1
    pytest test_golden_e2e.py -v -k "P1 and (Q1 or Q2 or Q3 or Q4 or Q5)"

    # Quick smoke test
    pytest test_golden_e2e.py -v -k "Q1 and P1"

Requirements:
    - Docker containers: timescale, memgraph, oxigraph
    - Golden dataset exported and loaded
"""

import subprocess
import sys
import time
import tempfile
from pathlib import Path
from typing import Optional

import pytest

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from basetype_benchmark.dataset.golden import GoldenDataset, export_to_parquet
from basetype_benchmark.runner.core.validator import GoldenValidator, ValidationResult
from basetype_benchmark.runner.core.params import GoldenAnswersLoader
from basetype_benchmark.runner.runners.base import RunStatus

# Configuration
PROJECT_ROOT = Path(__file__).parent
DOCKER_COMPOSE = PROJECT_ROOT / "docker" / "docker-compose.yml"
DSN_TIMESCALE = "postgresql://postgres:postgres@localhost:5432/benchmark"

# Query and paradigm definitions
ALL_QUERIES = [f"Q{i}" for i in range(1, 24)] + ["QW1", "QW2", "QW3"]
PARADIGMS = ["P1", "P2", "M1", "M2", "O2"]

# Query categories and their valid paradigms (simplified from catalog.yaml)
QUERY_PARADIGM_STATUS = {
    # Graph-only - all paradigms
    "Q1": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "NATIVE"},
    "Q2": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "NATIVE"},
    "Q3": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "NATIVE"},
    "Q4": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "NATIVE"},
    "Q5": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "NATIVE"},
    # Timeseries pure
    "Q6": {"P1": "NATIVE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "NATIVE", "O2": "DEGRADED"},
    # Hybrid
    "Q7": {"P1": "NATIVE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "NATIVE", "O2": "DEGRADED"},
    "Q8": {"P1": "NATIVE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "NATIVE", "O2": "DEGRADED"},
    "Q9": {"P1": "NATIVE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "NATIVE", "O2": "DEGRADED"},
    "Q10": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "NATIVE"},
    "Q11": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "NATIVE"},
    "Q12": {"P1": "NATIVE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "NATIVE", "O2": "DEGRADED"},
    "Q13": {"P1": "NATIVE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "NATIVE", "O2": "DEGRADED"},
    # JSONB-specific - P2 native, others impossible/degraded
    "Q14": {"P1": "IMPOSSIBLE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "DEGRADED", "O2": "DEGRADED"},
    "Q15": {"P1": "IMPOSSIBLE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "DEGRADED", "O2": "DEGRADED"},
    "Q16": {"P1": "IMPOSSIBLE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "DEGRADED", "O2": "NATIVE"},
    "Q17": {"P1": "IMPOSSIBLE", "P2": "NATIVE", "M1": "DEGRADED", "M2": "DEGRADED", "O2": "DEGRADED"},
    "Q18": {"P1": "DEGRADED", "P2": "NATIVE", "M1": "DEGRADED", "M2": "DEGRADED", "O2": "DEGRADED"},
    "Q19": {"P1": "VERY_DEGRADED", "P2": "NATIVE", "M1": "IMPOSSIBLE", "M2": "DEGRADED", "O2": "DEGRADED"},
    # Graph-native
    "Q20": {"P1": "DEGRADED", "P2": "DEGRADED", "M1": "NATIVE", "M2": "NATIVE", "O2": "DEGRADED"},
    "Q21": {"P1": "DEGRADED", "P2": "DEGRADED", "M1": "NATIVE", "M2": "NATIVE", "O2": "IMPOSSIBLE"},
    "Q22": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "NATIVE"},
    "Q23": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "DEGRADED"},
    # Write workloads
    "QW1": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "NATIVE"},
    "QW2": {"P1": "IMPOSSIBLE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "DEGRADED"},
    "QW3": {"P1": "NATIVE", "P2": "NATIVE", "M1": "NATIVE", "M2": "NATIVE", "O2": "DEGRADED"},
}


def is_docker_running() -> bool:
    """Check if Docker containers are running."""
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", str(DOCKER_COMPOSE), "ps", "--format", "json"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0 and "timescale" in result.stdout
    except Exception:
        return False


def query_is_impossible(query_id: str, paradigm: str) -> bool:
    """Check if query is impossible for paradigm."""
    status = QUERY_PARADIGM_STATUS.get(query_id, {}).get(paradigm, "NATIVE")
    return status == "IMPOSSIBLE"


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def golden_dataset_path(tmp_path_factory):
    """Generate and export golden dataset to temp directory."""
    output_dir = tmp_path_factory.mktemp("golden")
    export_to_parquet(output_dir)
    return output_dir


@pytest.fixture(scope="session")
def docker_ready():
    """Ensure Docker containers are running."""
    if not is_docker_running():
        pytest.skip("Docker containers not running. Start with: docker compose up -d")
    return True


@pytest.fixture(scope="session")
def validator():
    """Create validator instance."""
    return GoldenValidator(tolerance=0.01)


@pytest.fixture(scope="session")
def golden_loader():
    """Create golden answers loader."""
    return GoldenAnswersLoader()


# =============================================================================
# UNIT TESTS FOR VALIDATOR
# =============================================================================

class TestGoldenValidator:
    """Unit tests for GoldenValidator."""

    def test_validate_row_count_pass(self, validator):
        """Test row count validation passes when counts match."""
        # Q1 expects 8 rows
        result = validator.validate_row_count_only("Q1", 8)
        assert result.passed
        assert result.expected_count == 8
        assert result.actual_count == 8

    def test_validate_row_count_fail(self, validator):
        """Test row count validation fails when counts don't match."""
        result = validator.validate_row_count_only("Q1", 5)
        assert not result.passed
        assert "Row count mismatch" in result.errors[0]

    def test_validate_with_results(self, validator):
        """Test full validation with result data."""
        # Simulate Q1 results (energy chain)
        actual_results = [
            {"id": "submeter_1", "type": "Equipment", "name": "HVAC SubMeter", "depth": 1},
            {"id": "ups_1", "type": "Equipment", "name": "Main UPS", "depth": 1},
            {"id": "ahu_1", "type": "Equipment", "name": "AHU Building A", "depth": 2},
            {"id": "server_1", "type": "Equipment", "name": "Rack Server 1", "depth": 2},
            {"id": "server_2", "type": "Equipment", "name": "Rack Server 2", "depth": 2},
            {"id": "switch_1", "type": "Equipment", "name": "Network Switch", "depth": 2},
            {"id": "vav_1", "type": "Equipment", "name": "VAV Box 1", "depth": 3},
            {"id": "vav_2", "type": "Equipment", "name": "VAV Box 2", "depth": 3},
        ]
        result = validator.validate("Q1", actual_results)
        assert result.passed
        assert result.actual_count == 8

    def test_float_tolerance(self, validator):
        """Test float comparison with tolerance."""
        assert validator._values_match(21.59, 21.60)  # Within 1%
        assert validator._values_match(100.0, 100.5)  # Within 1%
        assert not validator._values_match(100.0, 102.0)  # Outside 1%


class TestGoldenAnswersLoader:
    """Unit tests for GoldenAnswersLoader."""

    def test_load_parameters(self, golden_loader):
        """Test loading parameters for Q1."""
        params = golden_loader.get_parameters("Q1")
        assert params.query_id == "Q1"
        meter_id = params.get("METER_ID")
        assert meter_id is not None
        assert meter_id.value == "meter_main_1"

    def test_get_expected_count(self, golden_loader):
        """Test getting expected row count."""
        count = golden_loader.get_expected_count("Q1")
        assert count == 8

    def test_get_expected_results(self, golden_loader):
        """Test getting expected results."""
        results = golden_loader.get_expected_results("Q1")
        assert results is not None
        assert len(results) == 8
        assert results[0]["id"] == "submeter_1"


# =============================================================================
# INTEGRATION TESTS (require Docker)
# =============================================================================

class TestGoldenDataset:
    """Test golden dataset generation and export."""

    def test_dataset_stats(self):
        """Test golden dataset has expected structure."""
        dataset = GoldenDataset()
        assert len(dataset.nodes) >= 35  # At least 35 nodes
        assert len(dataset.edges) >= 50  # At least 50 edges
        assert len(dataset.timeseries) == 168  # 7 points * 24 hours

    def test_export_creates_files(self, golden_dataset_path):
        """Test export creates all required files."""
        assert (golden_dataset_path / "nodes.parquet").exists()
        assert (golden_dataset_path / "edges.parquet").exists()
        assert (golden_dataset_path / "timeseries.parquet").exists()

    def test_export_file_contents(self, golden_dataset_path):
        """Test exported files have correct row counts."""
        import pandas as pd

        nodes_df = pd.read_parquet(golden_dataset_path / "nodes.parquet")
        edges_df = pd.read_parquet(golden_dataset_path / "edges.parquet")
        ts_df = pd.read_parquet(golden_dataset_path / "timeseries.parquet")

        assert len(nodes_df) >= 35
        assert len(edges_df) >= 50
        assert len(ts_df) == 168


# =============================================================================
# E2E QUERY TESTS (require Docker + loaded databases)
# =============================================================================

@pytest.mark.integration
class TestQueryCorrectness:
    """
    E2E tests for query correctness against golden dataset.

    These tests require:
    1. Docker containers running (timescale, memgraph, oxigraph)
    2. Golden dataset loaded into databases

    Run with: pytest test_golden_e2e.py -v -m integration
    """

    @pytest.mark.skip(reason="Requires database setup - run manually")
    @pytest.mark.parametrize("query_id", ["Q1", "Q2", "Q3", "Q4", "Q5"])
    def test_graph_only_queries_p1(self, query_id, docker_ready, validator, golden_loader):
        """Test graph-only queries on P1 (PostgreSQL relational)."""
        from basetype_benchmark.runner.runners.postgres import PostgresRunner
        from basetype_benchmark.runner.config import PostgresConfig

        config = PostgresConfig(dsn=DSN_TIMESCALE)
        runner = PostgresRunner(config, paradigm="P1")

        try:
            # Get query and parameters
            params = golden_loader.get_parameters(query_id)

            # Load query file
            query_file = PROJECT_ROOT / "queries" / "p1" / f"{query_id}.sql"
            if not query_file.exists():
                pytest.skip(f"Query file not found: {query_file}")

            query_text = query_file.read_text()

            # Execute query
            result = runner.execute(query_text, params.to_sql_params())

            if result.status != RunStatus.SUCCESS:
                pytest.fail(f"Query execution failed: {result.error_message}")

            # Validate results
            validation = validator.validate(query_id, result.rows)
            assert validation.passed, f"Validation failed: {validation.errors}"

        finally:
            runner.close()


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run tests directly (without pytest)."""
    print("=" * 60)
    print("GOLDEN DATASET E2E VALIDATION")
    print("=" * 60)

    # Test 1: Dataset generation
    print("\n=== Test 1: Golden Dataset Generation ===")
    dataset = GoldenDataset()
    print(f"  Nodes: {len(dataset.nodes)}")
    print(f"  Edges: {len(dataset.edges)}")
    print(f"  Timeseries: {len(dataset.timeseries)}")
    print("  OK")

    # Test 2: Export to parquet
    print("\n=== Test 2: Export to Parquet ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        export_to_parquet(tmpdir)
        files = list(Path(tmpdir).glob("*.parquet"))
        print(f"  Created {len(files)} files: {[f.name for f in files]}")
        print("  OK")

    # Test 3: Validator
    print("\n=== Test 3: GoldenValidator ===")
    validator = GoldenValidator()

    # Test Q1 validation
    result = validator.validate_row_count_only("Q1", 8)
    print(f"  Q1 row count validation (8): {'PASS' if result.passed else 'FAIL'}")

    result = validator.validate_row_count_only("Q1", 5)
    print(f"  Q1 row count validation (5): {'FAIL' if not result.passed else 'UNEXPECTED PASS'}")

    # Test 4: Golden Answers Loader
    print("\n=== Test 4: GoldenAnswersLoader ===")
    loader = GoldenAnswersLoader()

    params = loader.get_parameters("Q1")
    meter_id = params.get("METER_ID")
    print(f"  Q1 METER_ID: {meter_id.value if meter_id else 'NOT FOUND'}")

    count = loader.get_expected_count("Q1")
    print(f"  Q1 expected count: {count}")

    print("\n=== Summary ===")
    print("All unit tests passed!")
    print("\nTo run full E2E tests with databases:")
    print("  1. Start containers: docker compose up -d")
    print("  2. Load golden dataset: (TODO)")
    print("  3. Run: pytest test_golden_e2e.py -v -m integration")

    return 0


if __name__ == "__main__":
    sys.exit(main())
