"""Oxigraph engine for O1 (standalone) and O2 (hybrid) scenarios."""

import time
from pathlib import Path
from typing import Callable, Tuple

import requests


class OxigraphEngine:
    """Oxigraph engine for O1/O2 benchmarks."""

    def __init__(self, scenario: str = "O1"):
        """Initialize engine.

        Args:
            scenario: O1 (standalone) or O2 (hybrid with TimescaleDB)
        """
        self.scenario = scenario.upper()
        self.base_url = "http://localhost:7878"

    def connect(self) -> None:
        """Verify Oxigraph is reachable."""
        max_retries = 30
        for attempt in range(max_retries):
            try:
                resp = requests.get(f"{self.base_url}/query", timeout=5)
                if resp.status_code in (200, 400):  # 400 = no query provided, but server is up
                    return
            except requests.RequestException:
                pass
            print(f"  [WAIT] Oxigraph not ready ({attempt + 1}/{max_retries})...")
            time.sleep(2)
        raise ConnectionError("Could not connect to Oxigraph")

    def close(self) -> None:
        """No persistent connection to close."""
        pass

    def clear(self) -> None:
        """Clear all data."""
        requests.post(
            f"{self.base_url}/update",
            data="DROP ALL",
            headers={"Content-Type": "application/sparql-update"}
        )

    def load_ntriples(self, nt_file: Path) -> int:
        """Load N-Triples file into Oxigraph."""
        t0 = time.time()
        total_bytes = nt_file.stat().st_size

        with open(nt_file, "rb") as f:
            resp = requests.post(
                f"{self.base_url}/store?default",  # Use default graph
                data=f,
                headers={"Content-Type": "application/n-triples"}
            )

        if resp.status_code not in (200, 201, 204):
            raise RuntimeError(f"Failed to load N-Triples: HTTP {resp.status_code} - {resp.text}")

        elapsed = time.time() - t0
        mb = total_bytes / (1024 * 1024)
        print(f"  [LOAD] N-Triples: {mb:.0f} MB in {elapsed:.1f}s")

        # Count triples
        count_query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        resp = requests.get(
            f"{self.base_url}/query",
            params={"query": count_query},
            headers={"Accept": "application/sparql-results+json"}
        )
        if resp.status_code == 200:
            data = resp.json()
            count = int(data["results"]["bindings"][0]["count"]["value"])
            return count

        return 0

    def execute_query(self, query: str) -> Tuple[int, float]:
        """Execute a SPARQL query and return (row_count, latency_ms)."""
        t0 = time.perf_counter()
        resp = requests.get(
            f"{self.base_url}/query",
            params={"query": query},
            headers={"Accept": "application/sparql-results+json"}
        )
        latency_ms = (time.perf_counter() - t0) * 1000

        if resp.status_code == 200:
            data = resp.json()
            rows = data.get("results", {}).get("bindings", [])
            return len(rows), latency_ms

        return 0, latency_ms

    def get_executor(self) -> Callable[[str], Tuple[int, float]]:
        """Return query executor function."""
        return self.execute_query
