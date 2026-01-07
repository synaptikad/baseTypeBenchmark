"""Entry point for running the Benchmark Runner V3 CLI.

Usage:
    python -m src.basetype_benchmark.runner [command] [options]

Examples:
    python -m src.basetype_benchmark.runner dry-run --all
    python -m src.basetype_benchmark.runner dry-run -q Q1 -v
    python -m src.basetype_benchmark.runner info Q7
    python -m src.basetype_benchmark.runner profiles
"""
from .cli import app

if __name__ == "__main__":
    app()
