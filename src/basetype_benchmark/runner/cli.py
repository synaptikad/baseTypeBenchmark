"""CLI entry point for benchmark runner.

Usage:
    python -m basetype_benchmark.runner P1 --ram 8 --profile small-2d
    python -m basetype_benchmark.runner  # Interactive mode
"""

import argparse
import sys
from pathlib import Path

from .scenario import run_scenario


SCENARIOS = ["P1", "P2", "M1", "M2", "O1", "O2"]
PROFILES = ["small-2d", "small-7d", "medium-2d", "medium-7d", "large-2d", "large-7d"]


def interactive_mode() -> dict:
    """Prompt user for benchmark parameters."""
    print("\n=== BaseType Benchmark Runner ===\n")

    # Scenario selection
    print("Available scenarios:")
    for i, s in enumerate(SCENARIOS, 1):
        print(f"  {i}. {s}")
    while True:
        try:
            choice = input("\nSelect scenario (1-6): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(SCENARIOS):
                scenario = SCENARIOS[idx]
                break
        except ValueError:
            pass
        print("Invalid choice, try again.")

    # Profile selection
    print("\nAvailable profiles:")
    for i, p in enumerate(PROFILES, 1):
        print(f"  {i}. {p}")
    while True:
        try:
            choice = input("\nSelect profile (1-6): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(PROFILES):
                profile = PROFILES[idx]
                break
        except ValueError:
            pass
        print("Invalid choice, try again.")

    # RAM limit
    while True:
        try:
            ram = int(input("\nRAM limit in GB (e.g., 8): ").strip())
            if ram > 0:
                break
        except ValueError:
            pass
        print("Invalid value, try again.")

    # Export directory
    default_export = Path("exports") / profile
    export_input = input(f"\nExport directory [{default_export}]: ").strip()
    export_dir = Path(export_input) if export_input else default_export

    return {
        "scenario": scenario,
        "profile": profile,
        "ram_gb": ram,
        "export_dir": export_dir,
    }


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run BaseType benchmark scenarios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s P1 --ram 8 --profile small-2d
  %(prog)s M1 --ram 16 --profile medium-7d --export ./my_export
  %(prog)s  # Interactive mode
        """,
    )

    parser.add_argument(
        "scenario",
        nargs="?",
        choices=SCENARIOS,
        help="Scenario to run (P1, P2, M1, M2, O1, O2)",
    )
    parser.add_argument(
        "--ram",
        type=int,
        default=8,
        help="RAM limit in GB (default: 8)",
    )
    parser.add_argument(
        "--profile",
        choices=PROFILES,
        default="small-2d",
        help="Dataset profile (default: small-2d)",
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Export directory (default: exports/<profile>)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmark_results"),
        help="Output directory for results (default: benchmark_results)",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Interactive mode if no scenario provided
    if args.scenario is None:
        params = interactive_mode()
        scenario = params["scenario"]
        profile = params["profile"]
        ram_gb = params["ram_gb"]
        export_dir = params["export_dir"]
        output_dir = Path("benchmark_results")
    else:
        scenario = args.scenario
        profile = args.profile
        ram_gb = args.ram
        export_dir = args.export or (Path("exports") / profile)
        output_dir = args.output

    # Validate export directory
    if not export_dir.exists():
        print(f"ERROR: Export directory not found: {export_dir}")
        print(f"Run dataset generation first: python -m basetype_benchmark.dataset generate --profile {profile}")
        sys.exit(1)

    # Run benchmark
    result = run_scenario(
        scenario=scenario,
        export_dir=export_dir,
        profile=profile,
        ram_gb=ram_gb,
        output_dir=output_dir,
    )

    # Exit code based on result
    sys.exit(0 if result.status == "completed" else 1)


if __name__ == "__main__":
    main()
