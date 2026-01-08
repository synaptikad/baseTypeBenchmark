"""Predefined benchmark scenarios.

Provides ready-to-use configurations for common benchmark use cases:
- quick: Fast validation (~10 min)
- standard: Full comparison (~2h)
- ram_gradient: Fine-grained RAM testing (~30 min)
- publication: High precision for papers (~8h)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .benchmark.scenario import ScenarioConfig


# =============================================================================
# PREDEFINED SCENARIOS
# =============================================================================

SCENARIOS: dict[str, ScenarioConfig] = {
    "quick": ScenarioConfig(
        paradigms=["P1", "M1"],
        queries=["Q1", "Q6", "Q8"],  # Graph, TS, Hybrid
        data_profile="small",
        ram_levels_mb=[32768, 16384, 8192],  # 32, 16, 8 GB
        n_warmup=1,
        n_runs=3,
        n_variants=1,
        timeout_seconds=60.0,
    ),
    "standard": ScenarioConfig(
        paradigms=["P1", "P2", "M1", "M2", "O2"],
        queries=None,  # All queries
        data_profile="small",
        ram_levels_mb=[131072, 65536, 32768, 16384, 8192],  # 128, 64, 32, 16, 8 GB
        n_warmup=3,
        n_runs=10,
        n_variants=3,
        timeout_seconds=300.0,
    ),
    "ram_gradient": ScenarioConfig(
        paradigms=["M1"],  # Single paradigm, user can override
        queries=["Q1", "Q6", "Q8"],
        data_profile="small",
        ram_levels_mb=[65536, 49152, 32768, 24576, 16384, 12288, 8192, 4096],  # Fine-grained
        n_warmup=3,
        n_runs=10,
        n_variants=3,
        timeout_seconds=300.0,
    ),
    "publication": ScenarioConfig(
        paradigms=["P1", "P2", "M1", "M2", "O2"],
        queries=None,  # All queries
        data_profile="medium",
        ram_levels_mb=[131072, 98304, 65536, 49152, 32768, 24576, 16384, 12288, 8192, 4096],
        n_warmup=5,
        n_runs=30,
        n_variants=5,
        timeout_seconds=600.0,
    ),
    "ci": ScenarioConfig(
        paradigms=["P1"],
        queries=["Q1", "Q6"],
        data_profile="small",
        ram_levels_mb=[32768],  # Single level
        n_warmup=1,
        n_runs=2,
        n_variants=1,
        timeout_seconds=30.0,
    ),
}


# Scenario descriptions for display
SCENARIO_INFO: dict[str, dict[str, Any]] = {
    "quick": {
        "name": "Quick Test",
        "description": "Fast validation with minimal paradigms",
        "estimated_duration": "~10 minutes",
        "paradigms_count": 2,
        "ram_levels_count": 3,
    },
    "standard": {
        "name": "Standard Benchmark",
        "description": "Full comparison, all paradigms",
        "estimated_duration": "~2 hours",
        "paradigms_count": 5,
        "ram_levels_count": 5,
    },
    "ram_gradient": {
        "name": "RAM Gradient",
        "description": "Fine-grained RAM testing for single paradigm",
        "estimated_duration": "~30 minutes",
        "paradigms_count": 1,
        "ram_levels_count": 8,
    },
    "publication": {
        "name": "Publication Ready",
        "description": "High precision for academic papers",
        "estimated_duration": "~8 hours",
        "paradigms_count": 5,
        "ram_levels_count": 10,
    },
    "ci": {
        "name": "CI/CD Quick Check",
        "description": "Minimal test for continuous integration",
        "estimated_duration": "~2 minutes",
        "paradigms_count": 1,
        "ram_levels_count": 1,
    },
}


def get_scenario(name: str) -> ScenarioConfig:
    """Get predefined scenario by name.

    Args:
        name: Scenario name (quick, standard, ram_gradient, publication, ci)

    Returns:
        ScenarioConfig instance

    Raises:
        ValueError: If scenario name is unknown
    """
    if name not in SCENARIOS:
        available = ", ".join(SCENARIOS.keys())
        raise ValueError(f"Unknown scenario: {name}. Available: {available}")
    return SCENARIOS[name]


def get_scenario_info(name: str) -> dict[str, Any]:
    """Get scenario info for display.

    Args:
        name: Scenario name

    Returns:
        Dict with name, description, estimated_duration, etc.
    """
    return SCENARIO_INFO.get(name, {})


def list_scenarios() -> list[str]:
    """List all available scenario names."""
    return list(SCENARIOS.keys())


# =============================================================================
# YAML SCENARIO LOADING
# =============================================================================

def load_scenario_from_yaml(path: Path) -> ScenarioConfig:
    """Load scenario configuration from YAML file.

    YAML format:
    ```yaml
    name: My Scenario
    description: Custom benchmark configuration

    paradigms:
      - P1
      - M1

    queries:
      - Q1
      - Q6
      - Q8

    dataset:
      profile: small

    ram_gradient:
      levels_gb: [32, 16, 8]

    execution:
      warmup_runs: 3
      timed_runs: 10
      variants: 3
      timeout_seconds: 300

    options:
      cleanup_exports: true
    ```

    Args:
        path: Path to YAML file

    Returns:
        ScenarioConfig instance

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML format is invalid
    """
    if not path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid scenario file: expected dict, got {type(data)}")

    # Parse paradigms
    paradigms = data.get("paradigms", ["P1", "P2", "M1", "M2", "O2"])
    if isinstance(paradigms, str):
        paradigms = [p.strip() for p in paradigms.split(",")]

    # Parse queries
    queries = data.get("queries")
    if queries == "all":
        queries = None
    elif isinstance(queries, str):
        queries = [q.strip() for q in queries.split(",")]

    # Parse dataset
    dataset = data.get("dataset", {})
    data_profile = dataset.get("profile", "small") if isinstance(dataset, dict) else "small"

    # Parse RAM gradient
    ram_gradient = data.get("ram_gradient", {})
    if isinstance(ram_gradient, dict):
        levels_gb = ram_gradient.get("levels_gb", [128, 64, 32, 16, 8])
    else:
        levels_gb = [128, 64, 32, 16, 8]

    # Convert GB to MB
    ram_levels_mb = [int(gb * 1024) for gb in levels_gb]

    # Parse execution
    execution = data.get("execution", {})
    n_warmup = execution.get("warmup_runs", 3)
    n_runs = execution.get("timed_runs", 10)
    n_variants = execution.get("variants", 3)
    timeout_seconds = float(execution.get("timeout_seconds", 300))

    return ScenarioConfig(
        paradigms=paradigms,
        queries=queries,
        data_profile=data_profile,
        ram_levels_mb=ram_levels_mb,
        n_warmup=n_warmup,
        n_runs=n_runs,
        n_variants=n_variants,
        timeout_seconds=timeout_seconds,
    )


def save_scenario_to_yaml(config: ScenarioConfig, path: Path, name: str = "", description: str = "") -> None:
    """Save scenario configuration to YAML file.

    Args:
        config: ScenarioConfig instance
        path: Output path
        name: Optional scenario name
        description: Optional description
    """
    data = {
        "name": name or "Custom Scenario",
        "description": description or "Generated scenario configuration",
        "paradigms": config.paradigms,
        "queries": config.queries if config.queries else "all",
        "dataset": {
            "profile": config.data_profile,
        },
        "ram_gradient": {
            "levels_gb": [mb // 1024 for mb in config.ram_levels_mb],
        },
        "execution": {
            "warmup_runs": config.n_warmup,
            "timed_runs": config.n_runs,
            "variants": config.n_variants,
            "timeout_seconds": config.timeout_seconds,
        },
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


# =============================================================================
# SCENARIO BUILDER (for interactive customization)
# =============================================================================

@dataclass
class ScenarioBuilder:
    """Builder for creating custom scenarios interactively.

    Example:
        builder = ScenarioBuilder()
        builder.set_paradigms(["P1", "M1"])
        builder.set_ram_levels_gb([32, 16, 8])
        config = builder.build()
    """
    paradigms: list[str] = field(default_factory=lambda: ["P1", "P2", "M1", "M2", "O2"])
    queries: list[str] | None = None
    data_profile: str = "small"
    ram_levels_gb: list[int] = field(default_factory=lambda: [128, 64, 32, 16, 8])
    n_warmup: int = 3
    n_runs: int = 10
    n_variants: int = 3
    timeout_seconds: float = 300.0

    def set_paradigms(self, paradigms: list[str]) -> "ScenarioBuilder":
        """Set paradigms to test."""
        self.paradigms = [p.upper() for p in paradigms]
        return self

    def set_queries(self, queries: list[str] | None) -> "ScenarioBuilder":
        """Set queries to run (None = all)."""
        self.queries = [q.upper() for q in queries] if queries else None
        return self

    def set_profile(self, profile: str) -> "ScenarioBuilder":
        """Set data profile (small, medium, large)."""
        self.data_profile = profile
        return self

    def set_ram_levels_gb(self, levels: list[int]) -> "ScenarioBuilder":
        """Set RAM levels in GB."""
        self.ram_levels_gb = sorted(levels, reverse=True)
        return self

    def set_runs(self, n_runs: int) -> "ScenarioBuilder":
        """Set number of timed runs."""
        self.n_runs = n_runs
        return self

    def set_variants(self, n_variants: int) -> "ScenarioBuilder":
        """Set number of parameter variants."""
        self.n_variants = n_variants
        return self

    def set_timeout(self, seconds: float) -> "ScenarioBuilder":
        """Set query timeout in seconds."""
        self.timeout_seconds = seconds
        return self

    def from_preset(self, name: str) -> "ScenarioBuilder":
        """Load values from a preset scenario."""
        preset = get_scenario(name)
        self.paradigms = preset.paradigms
        self.queries = preset.queries
        self.data_profile = preset.data_profile
        self.ram_levels_gb = [mb // 1024 for mb in preset.ram_levels_mb]
        self.n_warmup = preset.n_warmup
        self.n_runs = preset.n_runs
        self.n_variants = preset.n_variants
        self.timeout_seconds = preset.timeout_seconds
        return self

    def build(self) -> ScenarioConfig:
        """Build ScenarioConfig from current settings."""
        return ScenarioConfig(
            paradigms=self.paradigms,
            queries=self.queries,
            data_profile=self.data_profile,
            ram_levels_mb=[gb * 1024 for gb in self.ram_levels_gb],
            n_warmup=self.n_warmup,
            n_runs=self.n_runs,
            n_variants=self.n_variants,
            timeout_seconds=self.timeout_seconds,
        )

    def estimated_duration_minutes(self) -> int:
        """Estimate benchmark duration in minutes.

        Rough estimate based on:
        - ~30s per paradigm for export/load
        - ~5s per query per run at each RAM level
        """
        n_paradigms = len(self.paradigms)
        n_queries = len(self.queries) if self.queries else 23
        n_levels = len(self.ram_levels_gb)
        total_runs = self.n_runs * self.n_variants

        # Time estimates (seconds)
        export_load_time = n_paradigms * 30
        warmup_time = n_paradigms * n_levels * n_queries * self.n_warmup * 0.5
        run_time = n_paradigms * n_levels * n_queries * total_runs * 0.3

        total_seconds = export_load_time + warmup_time + run_time
        return int(total_seconds / 60) + 1  # Round up
