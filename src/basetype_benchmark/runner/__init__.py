"""Benchmark runner for BaseType Benchmark.

Simple, modular runner for executing benchmarks across 6 scenarios:
- P1: PostgreSQL relational
- P2: PostgreSQL JSONB
- M1: Memgraph standalone (graph + chunks in-memory)
- M2: Memgraph + TimescaleDB hybrid
- O1: Oxigraph standalone (RDF + daily aggregates)
- O2: Oxigraph + TimescaleDB hybrid

Usage:
    python -m basetype_benchmark.runner P1 --ram 8 --profile small-2d
    python -m basetype_benchmark.runner  # Interactive mode
"""

__version__ = "2.0.0"
