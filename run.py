#!/usr/bin/env python3
"""BaseType Benchmark - Entry Point

Unified entry point for dataset generation and benchmark execution.

Usage:
    # Dataset generation
    python run.py generate small-2d         # Generate small-2d dataset
    python run.py generate medium-1w --seed 123

    # Benchmark execution  
    python run.py                           # Interactive mode
    python run.py P1 --ram 8                # Run P1 scenario
    python run.py ALL --ram 16              # Run all scenarios
    python run.py P1 --export ./exports/small-2d_seed42

Alternative:
    python -m basetype_benchmark.runner     # Same as run.py (benchmark only)
"""

import os
import sys

# Ensure src/ is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def cmd_generate(args):
    """Generate a dataset."""
    from basetype_benchmark.dataset.dataset_manager import DatasetManager
    
    if len(args) < 1:
        print("Usage: python run.py generate <profile> [--seed SEED]")
        print("\nProfiles: small-2d, small-1w, small-1m, medium-2d, medium-1w, etc.")
        print("Format: <scale>-<duration>")
        print("  Scales: small, medium, large")
        print("  Durations: 2d, 1w, 1m, 6m, 1y")
        sys.exit(1)
    
    profile = args[0]
    seed = 42  # Default seed
    
    # Parse --seed argument
    for i, arg in enumerate(args):
        if arg == "--seed" and i + 1 < len(args):
            seed = int(args[i + 1])
    
    print(f"\n{'='*60}")
    print(f"  DATASET GENERATION")
    print(f"{'='*60}")
    print(f"  Profile: {profile}")
    print(f"  Seed: {seed}")
    print(f"{'='*60}\n")
    
    manager = DatasetManager()
    parquet_dir, fingerprint = manager.generate_parquet_only(profile, seed)
    
    print(f"\n{'='*60}")
    print(f"  GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Output: {parquet_dir}")
    nodes_count = fingerprint.get('nodes_count', 'N/A')
    edges_count = fingerprint.get('edges_count', 'N/A')
    ts_count = fingerprint.get('timeseries_count', 'N/A')
    print(f"  Nodes: {nodes_count:,}" if isinstance(nodes_count, int) else f"  Nodes: {nodes_count}")
    print(f"  Edges: {edges_count:,}" if isinstance(edges_count, int) else f"  Edges: {edges_count}")
    print(f"  Timeseries rows: {ts_count:,}" if isinstance(ts_count, int) else f"  Timeseries rows: {ts_count}")
    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    # Check for generate subcommand
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        cmd_generate(sys.argv[2:])
        return
    
    # Otherwise, delegate to benchmark runner
    from basetype_benchmark.runner.cli import main as runner_main
    runner_main()


if __name__ == "__main__":
    main()
