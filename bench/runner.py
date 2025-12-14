"""
Runner principal pour les benchmarks reproductibles.
Les étapes suivent le protocole académique : vérification des services, ingestion, warmup, mesures et export structuré.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import yaml

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from bench.config import (
    ACTIVE_QUERIES,
    N_RUNS,
    N_WARMUP,
    Profile,
    SCALE_MODE,
    SEED,
    TIMEOUT_S,
)
from bench.metrics import ResourceMonitor, export_csv, export_json, latency_stats, volume_disk_usage

RESULTS_DIR = Path("bench/results")
PROFILES_DIR = Path("bench/profiles")


class BenchmarkError(RuntimeError):
    pass


def load_profile(profile_name: str) -> Profile:
    path = PROFILES_DIR / f"{profile_name}.yaml"
    if not path.exists():
        raise BenchmarkError(f"Profil {profile_name} introuvable")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Profile.from_mapping(profile_name, data)


def wait_for_health(container: str | None, timeout: float = 60.0) -> None:
    if not container:
        return
    start = time.time()
    while time.time() - start < timeout:
        try:
            status = subprocess.check_output(
                [
                    "docker",
                    "inspect",
                    "-f",
                    "{{.State.Health.Status}}",
                    container,
                ],
                text=True,
            ).strip()
            if status == "healthy":
                return
        except subprocess.CalledProcessError:
            pass
        time.sleep(2)
    raise BenchmarkError(f"Le service {container} n'est pas healthy après {timeout}s")


def run_command(command: List[str], timeout: float) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise BenchmarkError(f"Commande expirée : {' '.join(command)}") from exc
    except subprocess.CalledProcessError as exc:
        raise BenchmarkError(
            f"Commande échouée ({exc.returncode}) : {' '.join(command)}\n{exc.stderr}"
        ) from exc


def format_command(template: List[str], context: Dict[str, str]) -> List[str]:
    import re
    full_context = {**os.environ, **context}
    
    def expand_var(match):
        var = match.group(1)
        if ':-' in var:
            var_name, default = var.split(':-', 1)
            return full_context.get(var_name, default)
        else:
            return full_context.get(var, '')
    
    result = []
    for part in template:
        # Replace ${VAR} or ${VAR:-default}
        part = re.sub(r'\$\{([^}]+)\}', expand_var, part)
        result.append(part)
    return result


def _count_lines(path: Path, has_header: bool = False) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        total = sum(1 for _ in handle)
        return max(total - 1, 0) if has_header else total


def _count_triples(jsonld_path: Path) -> int | None:
    if not jsonld_path.exists():
        return None
    try:
        data = yaml.safe_load(jsonld_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    graph = data.get("@graph") or []
    triples = 0
    for node in graph:
        for key, value in node.items():
            if key in {"id", "@id"}:
                continue
            if isinstance(value, list):
                triples += len(value)
            else:
                triples += 1
    return triples


def dataset_element_counts() -> Dict[str, int | None]:
    data_dir = Path("dataset_gen/out")
    counts: Dict[str, int | None] = {"nodes": None, "edges": None, "triples": None}
    nodes_csv = data_dir / "nodes.csv"
    edges_csv = data_dir / "edges.csv"
    nodes_json = data_dir / "nodes.json"
    edges_json = data_dir / "edges.json"
    jsonld_path = data_dir / "graph.jsonld"

    if nodes_csv.exists():
        counts["nodes"] = _count_lines(nodes_csv, has_header=True)
    elif nodes_json.exists():
        counts["nodes"] = _count_lines(nodes_json)

    if edges_csv.exists():
        counts["edges"] = _count_lines(edges_csv, has_header=True)
    elif edges_json.exists():
        counts["edges"] = _count_lines(edges_json)

    counts["triples"] = _count_triples(jsonld_path)
    return counts


def count_items(profile: Profile) -> Dict[str, int | None]:
    counts = dataset_element_counts()
    total_items = None
    if counts["nodes"] is not None and counts["edges"] is not None:
        total_items = counts["nodes"] + counts["edges"]
    if profile.type == "oxigraph" and counts.get("triples") is not None:
        return {"items": counts["triples"], "nodes": counts["nodes"], "edges": counts["edges"], "triples": counts["triples"]}
    return {"items": total_items, "nodes": counts["nodes"], "edges": counts["edges"], "triples": counts["triples"]}


def run_ingestion(profile: Profile) -> Dict[str, float | int | None]:
    if not profile.ingestion:
        return {"time_s": 0.0, "items": None, "nodes": None, "edges": None, "triples": None}
    command = format_command(profile.ingestion.get("command", []), {"endpoint": profile.endpoint})
    t0 = time.perf_counter()
    run_command(command, timeout=profile.ingestion.get("timeout_s", TIMEOUT_S))
    elapsed = time.perf_counter() - t0
    items = count_items(profile)
    return {"time_s": round(elapsed, 3), **items}


def _execute_query(command: List[str]) -> float:
    t0 = time.perf_counter()
    run_command(command, timeout=TIMEOUT_S)
    return round(time.perf_counter() - t0, 3)


def run_queries(profile: Profile, active_queries: List[str]) -> List[dict]:
    results = []
    for qname in active_queries:
        mapping = profile.queries.get(qname)
        if mapping is None:
            results.append(
                {
                    "query": qname,
                    "warmup_runs": [],
                    "measure_runs": [],
                    "stats": None,
                    "note": "N/A",
                }
            )
            continue
        if isinstance(mapping, dict) and "selection" in mapping and "aggregation" in mapping:
            selection_cmd = format_command(mapping["selection"], {"endpoint": profile.endpoint})
            aggregation_cmd = format_command(mapping["aggregation"], {"endpoint": profile.endpoint})
            for _ in range(N_WARMUP):
                _execute_query(selection_cmd)
                _execute_query(aggregation_cmd)
            measures = []
            for _ in range(N_RUNS):
                t_sel = _execute_query(selection_cmd)
                t_agg = _execute_query(aggregation_cmd)
                measures.append(t_sel + t_agg)
            stats = latency_stats(measures)
            results.append(
                {
                    "query": qname,
                    "warmup_runs": [],
                    "measure_runs": measures,
                    "stats": stats,
                    "note": "Sélection graphe/RDF + agrégation Timescale",
                }
            )
            continue
        command_template = mapping if isinstance(mapping, list) else mapping.get("command", [])
        command = format_command(command_template, {"endpoint": profile.endpoint})
        warmup_runs = [_execute_query(command) for _ in range(N_WARMUP)]
        measure_runs = [_execute_query(command) for _ in range(N_RUNS)]
        stats = latency_stats(measure_runs)
        results.append(
            {
                "query": qname,
                "warmup_runs": warmup_runs,
                "measure_runs": measure_runs,
                "stats": stats,
                "note": None,
            }
        )
    return results


def summarize(results: dict) -> str:
    lines = [
        f"Profil: {results['profile']} ({results['engine']})",
        f"Mode: {results['scale_mode']} - seed={results['seed']}",
    ]
    ingestion = results["ingestion"]
    ingest_line = f"Ingestion: {ingestion.get('time_s')}s"
    dataset_items = [ingestion.get("nodes"), ingestion.get("edges")]
    if all(v is not None for v in dataset_items):
        ingest_line += f" pour {ingestion.get('nodes')} nœuds + {ingestion.get('edges')} relations"
    if ingestion.get("items") is not None:
        ingest_line += f" (compteur principal={ingestion.get('items')})"
    if ingestion.get("triples") is not None:
        ingest_line += f" ; RDF≈{ingestion.get('triples')} triplets"
    lines.append(ingest_line)
    lines.append("Requêtes:")
    for q in results["queries"]:
        if q["stats"]:
            lines.append(
                f"  {q['query']} p50={q['stats']['p50']}s p95={q['stats']['p95']}s min={q['stats']['min']}s max={q['stats']['max']}s"
            )
        else:
            lines.append(f"  {q['query']} {q.get('note', '')}")
    res = results.get("resources", {})
    lines.append(
        f"Mémoire: steady={res.get('steady_state_mem_mb')} MiB peak={res.get('peak_mem_mb')} MiB CPU={res.get('avg_cpu_pct')}%"
    )
    lines.append(f"Volume: {res.get('volume_mb')} MiB")
    return "\n".join(lines)


def save_results(payload: dict, engine: str, profile: str) -> None:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    json_path = RESULTS_DIR / f"{engine}_{profile}_{ts}.json"
    csv_path = RESULTS_DIR / f"{engine}_{profile}_{ts}.csv"
    export_json(json_path, payload)
    rows = []
    for q in payload["queries"]:
        if not q["measure_runs"]:
            rows.append(
                {
                    "query": q["query"],
                    "run": None,
                    "latency_s": None,
                    "note": q.get("note"),
                }
            )
            continue
        for idx, latency in enumerate(q["measure_runs"], start=1):
            rows.append(
                {
                    "query": q["query"],
                    "run": idx,
                    "latency_s": latency,
                    "note": q.get("note"),
                }
            )
    export_csv(csv_path, rows, ["query", "run", "latency_s", "note"])
    print(f"Résultats écrits dans {json_path} et {csv_path}")


def run_profile(profile_name: str) -> dict:
    profile = load_profile(profile_name)
    dataset_counts = dataset_element_counts()
    print(
        f"[contexte] scénario={SCALE_MODE} seed={SEED} profil={profile.name} moteur={profile.engine}"
    )
    if dataset_counts["nodes"] is not None and dataset_counts["edges"] is not None:
        print(
            f"[cohérence] données attendues: {dataset_counts['nodes']} nœuds + {dataset_counts['edges']} relations"
        )
    if dataset_counts.get("triples") is not None:
        print(
            f"[cohérence] export RDF anticipé: ≈{dataset_counts['triples']} triplets (compte structurel conservé pour comparaison)"
        )
    wait_for_health(profile.container)
    monitor = ResourceMonitor(profile.container)
    monitor.start()
    ingestion_info = run_ingestion(profile)
    active = ACTIVE_QUERIES.get(profile.type, [])
    query_results = run_queries(profile, active)
    monitor.stop()
    resources = monitor.summarize()
    resources["volume_mb"] = volume_disk_usage(profile.volume)
    payload = {
        "engine": profile.engine,
        "profile": profile.name,
        "scale_mode": SCALE_MODE,
        "seed": SEED,
        "ingestion": ingestion_info,
        "queries": query_results,
        "resources": resources,
        "runs": N_RUNS,
        "warmup": N_WARMUP,
        "timeout_s": TIMEOUT_S,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    save_results(payload, profile.engine, profile.name)
    print(summarize(payload))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Runner académique pour benchmarks multi-moteurs")
    parser.add_argument(
        "profile",
        help="Nom du profil YAML dans bench/profiles (sans extension)",
    )
    args = parser.parse_args()
    run_profile(args.profile)


if __name__ == "__main__":
    main()
