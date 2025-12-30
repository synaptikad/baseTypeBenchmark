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


def discover_datasets(base_dir: Path = None) -> list:
    """Discover available datasets on disk.

    Looks for directories containing parquet files in:
    - src/basetype_benchmark/dataset/exports/
    - exports/
    - datasets/

    Returns:
        List of (profile_name, export_path) tuples
    """
    if base_dir is None:
        base_dir = Path.cwd()

    datasets = []

    # Search paths (in order of priority)
    search_paths = [
        base_dir / "src" / "basetype_benchmark" / "dataset" / "exports",
        base_dir / "exports",
        base_dir / "datasets",
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        for item in search_path.iterdir():
            if not item.is_dir():
                continue

            # Check for parquet files in root or in parquet/ subdirectory
            parquet_dir = None
            if (item / "nodes.parquet").exists() or (item / "timeseries.parquet").exists():
                parquet_dir = item
            elif (item / "parquet" / "nodes.parquet").exists() or (item / "parquet" / "timeseries.parquet").exists():
                parquet_dir = item / "parquet"

            if parquet_dir:
                # Extract profile name (remove _seed* suffix if present)
                profile = item.name
                if "_seed" in profile:
                    profile = profile.split("_seed")[0]

                # Get size info
                try:
                    size_mb = sum(f.stat().st_size for f in parquet_dir.rglob("*.parquet")) / (1024 * 1024)
                except:
                    size_mb = 0

                datasets.append({
                    "profile": profile,
                    "path": parquet_dir,  # Point to actual parquet directory
                    "size_mb": size_mb,
                    "full_name": item.name,
                })

    return datasets


def interactive_mode() -> dict:
    """Prompt user for benchmark parameters."""
    print("\n=== BaseType Benchmark Runner ===\n")

    # Discover datasets
    datasets = discover_datasets()

    if not datasets:
        print("ERROR: No datasets found!")
        print("Generate a dataset first with the old run.py or manually.")
        print("\nSearched in:")
        print("  - src/basetype_benchmark/dataset/exports/")
        print("  - exports/")
        print("  - datasets/")
        sys.exit(1)

    # Dataset selection
    print("Available datasets:")
    for i, ds in enumerate(datasets, 1):
        size_str = f"{ds['size_mb']:.0f} MB" if ds['size_mb'] > 0 else "unknown size"
        print(f"  {i}. {ds['full_name']} ({size_str})")

    while True:
        try:
            choice = input(f"\nSelect dataset (1-{len(datasets)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(datasets):
                selected_ds = datasets[idx]
                break
        except ValueError:
            pass
        print("Invalid choice, try again.")

    # Scenario selection
    print("\nAvailable scenarios:")
    for i, s in enumerate(SCENARIOS, 1):
        print(f"  {i}. {s}")
    print(f"  A. ALL (run all 6 scenarios)")

    while True:
        choice = input(f"\nSelect scenario (1-6 or A for all): ").strip().upper()
        if choice == "A":
            scenarios = SCENARIOS.copy()
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(SCENARIOS):
                scenarios = [SCENARIOS[idx]]
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

    return {
        "scenarios": scenarios,
        "profile": selected_ds["profile"],
        "ram_gb": ram,
        "export_dir": selected_ds["path"],
    }


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run BaseType benchmark scenarios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s P1 --ram 8 --export ./exports/small-1m_seed42
  %(prog)s ALL --ram 16 --export ./exports/medium-7d_seed42
  %(prog)s  # Interactive mode (auto-discovers datasets)
        """,
    )

    parser.add_argument(
        "scenario",
        nargs="?",
        choices=SCENARIOS + ["ALL"],
        help="Scenario to run (P1, P2, M1, M2, O1, O2, or ALL)",
    )
    parser.add_argument(
        "--ram",
        type=int,
        default=8,
        help="RAM limit in GB (default: 8)",
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Export directory containing parquet files",
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
        scenarios = params["scenarios"]
        profile = params["profile"]
        ram_gb = params["ram_gb"]
        export_dir = params["export_dir"]
        output_dir = Path("benchmark_results")
    else:
        # CLI mode
        if args.scenario == "ALL":
            scenarios = SCENARIOS.copy()
        else:
            scenarios = [args.scenario]

        ram_gb = args.ram
        output_dir = args.output

        # Find export directory
        if args.export:
            export_dir = args.export
        else:
            # Auto-discover
            datasets = discover_datasets()
            if not datasets:
                print("ERROR: No datasets found. Use --export to specify path.")
                sys.exit(1)
            if len(datasets) == 1:
                export_dir = datasets[0]["path"]
                print(f"Auto-selected dataset: {datasets[0]['full_name']}")
            else:
                print("Multiple datasets found. Use --export to specify:")
                for ds in datasets:
                    print(f"  --export {ds['path']}")
                sys.exit(1)

        # Extract profile from directory name
        profile = export_dir.name
        if "_seed" in profile:
            profile = profile.split("_seed")[0]

    # Validate export directory
    if not export_dir.exists():
        print(f"ERROR: Export directory not found: {export_dir}")
        sys.exit(1)

    # Run benchmarks
    results = []
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"  Running {scenario}")
        print(f"{'='*60}")

        result = run_scenario(
            scenario=scenario,
            export_dir=export_dir,
            profile=profile,
            ram_gb=ram_gb,
            output_dir=output_dir,
        )
        results.append(result)

    # Summary
    if len(results) > 1:
        print(f"\n{'='*60}")
        print("  SUMMARY")
        print(f"{'='*60}")
        for r in results:
            status = "✓" if r.status == "completed" else "✗"
            print(f"  {status} {r.scenario}: {r.status}")

    # Exit code: 0 if all completed, 1 otherwise
    all_ok = all(r.status == "completed" for r in results)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
