"""Charge un export JSON-LD du dataset dans Oxigraph via HTTP.

Le script applique un nettoyage optionnel du graphe par défaut, charge le
fichier JSON-LD généré par `dataset_gen`, mesure le temps d'ingestion et
vérifie le nombre total de triplets insérés. Aucune inférence n'est activée
et seules les relations explicites présentes dans le fichier sont chargées.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import requests


def wait_for_oxigraph(
    endpoint: str = "http://localhost:7878",
    max_retries: int = 10,
    retry_delay: float = 3.0
) -> bool:
    """Wait for Oxigraph to be ready with retry logic.

    Args:
        endpoint: Oxigraph HTTP endpoint
        max_retries: Maximum connection attempts
        retry_delay: Seconds to wait between retries

    Returns:
        True if connected, raises exception otherwise
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"{endpoint}/query",
                params={"query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1"},
                timeout=10
            )
            # 200 = OK with results, 204 = OK no content
            if response.status_code in [200, 204]:
                return True
        except requests.exceptions.RequestException:
            pass

        if attempt < max_retries - 1:
            print(f"[INFO] Oxigraph not ready (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
            time.sleep(retry_delay)
        else:
            print(f"[ERROR] Oxigraph connection failed after {max_retries} attempts")
            raise ConnectionError(f"Cannot connect to Oxigraph at {endpoint}")

    return False


def clear_store(endpoint: str) -> None:
    response = requests.delete(f"{endpoint}/store", timeout=30)
    # Accept both 200 and 204 as success
    if response.status_code not in [200, 204]:
        response.raise_for_status()


def load_jsonld(endpoint: str, jsonld_path: Path) -> float:
    """Load JSON-LD file into Oxigraph default graph."""
    payload = jsonld_path.read_bytes()
    t0 = time.perf_counter()
    response = requests.post(
        f"{endpoint}/store?default", headers={"Content-Type": "application/ld+json"}, data=payload, timeout=300
    )
    # Accept 200, 201, 204 as success (201 = Created is valid for POST)
    if response.status_code not in [200, 201, 204]:
        response.raise_for_status()
    elapsed = time.perf_counter() - t0
    print(f"Ingestion Oxigraph: {len(payload)} octets chargés en {elapsed:.2f}s")
    return elapsed


def load_ntriples(endpoint: str, nt_path: Path, timeout: int = 600) -> float:
    """Load N-Triples file into Oxigraph via HTTP POST to default graph.

    Args:
        endpoint: Oxigraph HTTP endpoint (e.g., http://localhost:7878)
        nt_path: Path to .nt file
        timeout: Request timeout in seconds (default 10 min for large files)

    Returns:
        Elapsed time in seconds

    Note:
        Uses /store?default to load into the default graph.
        Without ?default, POST creates a new named graph each time.
    """
    payload = nt_path.read_bytes()
    t0 = time.perf_counter()
    response = requests.post(
        f"{endpoint}/store?default",
        headers={"Content-Type": "application/n-triples"},
        data=payload,
        timeout=timeout
    )
    if response.status_code not in [200, 201, 204]:
        # Print response body for detailed error (e.g., parsing errors)
        print(f"[ERROR] Oxigraph returned {response.status_code}: {response.text[:500]}")
        response.raise_for_status()
    elapsed = time.perf_counter() - t0
    size_mb = len(payload) / (1024 * 1024)
    print(f"Ingestion Oxigraph: {size_mb:.1f} MB N-Triples chargés en {elapsed:.2f}s")
    return elapsed


def load_ntriples_streaming(endpoint: str, nt_path: Path, chunk_size: int = 10 * 1024 * 1024) -> float:
    """Load large N-Triples file in chunks for streaming.

    For very large files (>100MB), this prevents memory issues.

    Args:
        endpoint: Oxigraph HTTP endpoint
        nt_path: Path to .nt file
        chunk_size: Size of each chunk in bytes (default 10MB)

    Returns:
        Total elapsed time in seconds
    """
    t0 = time.perf_counter()
    total_bytes = 0

    with open(nt_path, 'rb') as f:
        buffer = b''
        chunk_num = 0

        while True:
            data = f.read(chunk_size)
            if not data:
                break

            buffer += data

            # Find last complete line
            last_newline = buffer.rfind(b'\n')
            if last_newline == -1:
                continue

            # Send complete lines
            to_send = buffer[:last_newline + 1]
            buffer = buffer[last_newline + 1:]

            response = requests.post(
                f"{endpoint}/store?default",
                headers={"Content-Type": "application/n-triples"},
                data=to_send,
                timeout=300
            )
            if response.status_code not in [200, 201, 204]:
                print(f"[ERROR] Oxigraph returned {response.status_code}: {response.text[:500]}")
                response.raise_for_status()

            total_bytes += len(to_send)
            chunk_num += 1
            if chunk_num % 10 == 0:
                print(f"      {total_bytes / (1024*1024):.1f} MB loaded...", flush=True)

        # Send remaining buffer
        if buffer:
            response = requests.post(
                f"{endpoint}/store?default",
                headers={"Content-Type": "application/n-triples"},
                data=buffer,
                timeout=300
            )
            if response.status_code not in [200, 201, 204]:
                print(f"[ERROR] Oxigraph returned {response.status_code}: {response.text[:500]}")
                response.raise_for_status()
            total_bytes += len(buffer)

    elapsed = time.perf_counter() - t0
    print(f"Ingestion Oxigraph: {total_bytes / (1024*1024):.1f} MB N-Triples chargés en {elapsed:.2f}s (streaming)")
    return elapsed


def count_triples(endpoint: str) -> int:
    """Count total triples in the store.

    Note: Oxigraph uses /query endpoint for SPARQL queries (not /sparql).
    """
    query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
    response = requests.get(
        f"{endpoint}/query",
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    binding = data["results"]["bindings"][0]["count"]
    count = int(binding["value"])
    print(f"Triples chargés: {count}")
    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loader Oxigraph pour Base Type Benchmark")
    parser.add_argument(
        "--endpoint",
        default="http://localhost:7878",
        help="URL de base du service Oxigraph (par défaut http://localhost:7878)",
    )
    parser.add_argument(
        "--jsonld-file",
        type=Path,
        default=Path("dataset_gen/out/graph.jsonld"),
        help="Chemin vers le fichier JSON-LD généré",
    )
    parser.add_argument(
        "--skip-clear",
        action="store_true",
        help="Ne pas vider le graphe par défaut avant le chargement",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.jsonld_file.exists():
        raise FileNotFoundError(f"Fichier JSON-LD introuvable: {args.jsonld_file}")

    # Wait for Oxigraph to be ready
    wait_for_oxigraph(args.endpoint)

    if not args.skip_clear:
        clear_store(args.endpoint)
        print("Graphe par défaut vidé avant chargement")

    elapsed = load_jsonld(args.endpoint, args.jsonld_file)
    triples = count_triples(args.endpoint)

    print(f"Résumé: {triples} triplets chargés en {elapsed:.2f}s sans inférence")


if __name__ == "__main__":
    main()
