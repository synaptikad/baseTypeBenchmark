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
    payload = jsonld_path.read_bytes()
    t0 = time.perf_counter()
    response = requests.post(
        f"{endpoint}/store", headers={"Content-Type": "application/ld+json"}, data=payload, timeout=300
    )
    # Accept 200, 201, 204 as success (201 = Created is valid for POST)
    if response.status_code not in [200, 201, 204]:
        response.raise_for_status()
    elapsed = time.perf_counter() - t0
    print(f"Ingestion Oxigraph: {len(payload)} octets chargés en {elapsed:.2f}s")
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
