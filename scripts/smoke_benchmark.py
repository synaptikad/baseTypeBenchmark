"""Smoke benchmark runner (non-interactive).

Purpose
-------
Quickly validate that the end-to-end benchmark pipeline works on a *reduced*
cloud instance before running a full campaign.

This script intentionally runs:
- a small profile (default: small-2d)
- a reduced protocol (default: 1 warmup, 3 runs)
- a minimal query subset including one hybrid query (default: Q1, Q6, Q8)
- multiple engines (default: P1,P2,M1,M2,O1,O2)
- a small RAM palette (default: 8,16)

It reuses the existing implementation in run.py without modifying it.

Usage (Linux host):
  python scripts/smoke_benchmark.py --profile small-2d --ram-levels 8 16

Notes
-----
- Requires Docker + docker compose and the benchmark docker-compose project.
- For dataset generation, it uses DatasetManager (V2 exporter).
- You can set --dataset-source hf to attempt HuggingFace download first.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_run_module():
    # Ensure repo root is importable
    sys.path.insert(0, str(REPO_ROOT))
    import run  # type: ignore

    return run


def _ensure_parquet_pivot(run_mod, profile: str, seed: int, source: str) -> Path:
    """Ensure Parquet pivot exists (lazy export mode), return export_dir."""
    from basetype_benchmark.dataset.dataset_manager import DatasetManager

    mgr = DatasetManager(base_dir=Path("src/basetype_benchmark/dataset"))
    export_dir = mgr.get_export_path(profile, seed)
    parquet_dir = export_dir / "parquet"

    # If parquet already exists, we're good
    if (parquet_dir / "timeseries.parquet").exists():
        print(f"[i] Parquet pivot exists: {parquet_dir}")
        return export_dir

    # Try HuggingFace first
    if source in ("auto", "hf"):
        ok = False
        try:
            ok = bool(run_mod.download_from_huggingface(profile, seed=seed))
        except Exception:
            ok = False
        if ok and (parquet_dir / "timeseries.parquet").exists():
            return export_dir
        if source == "hf":
            raise RuntimeError("Dataset not found on HuggingFace (or download failed)")

    # Generate Parquet pivot only (no scenario exports yet)
    mgr.generate_parquet_only(profile_name=profile, seed=seed)

    if not (parquet_dir / "timeseries.parquet").exists():
        raise RuntimeError(f"Parquet generation failed: {parquet_dir}")

    return export_dir


def _export_scenario(profile: str, scenario: str, seed: int) -> Path:
    """Export a single scenario from Parquet pivot (lazy export)."""
    from basetype_benchmark.dataset.dataset_manager import DatasetManager

    mgr = DatasetManager(base_dir=Path("src/basetype_benchmark/dataset"))
    return mgr.export_scenario_only(profile, scenario, seed)


def _prune_scenario(profile: str, scenario: str, seed: int, keep_timeseries: bool = True) -> None:
    """Prune scenario files after run to free disk space."""
    from basetype_benchmark.dataset.dataset_manager import DatasetManager

    mgr = DatasetManager(base_dir=Path("src/basetype_benchmark/dataset"))
    mgr.prune_scenario(profile, scenario, seed, keep_shared_timeseries=keep_timeseries)


def _select_queries(run_mod, scenarios: List[str], query_ids: List[str]) -> Dict[str, List[str]]:
    # Build a per-scenario map using the intersection with existing queries
    selected: Dict[str, List[str]] = {}
    for scenario in scenarios:
        existing = run_mod.QUERIES_BY_SCENARIO.get(scenario, [])
        selected[scenario] = [q for q in query_ids if q in existing]
    return selected


def _run_one(run_mod, scenario: str, export_dir: Path, profile: str, n_warmup: int, n_runs: int) -> Dict:
    result = {"scenario": scenario, "profile": profile, "queries": {}}

    if scenario.startswith("P"):
        return run_mod._run_postgres_benchmark(
            scenario=scenario,
            export_dir=export_dir,
            result=result,
            n_warmup=n_warmup,
            n_runs=n_runs,
            profile=profile,
        )

    if scenario.startswith("M"):
        return run_mod._run_memgraph_benchmark(
            scenario=scenario,
            export_dir=export_dir,
            result=result,
            n_warmup=n_warmup,
            n_runs=n_runs,
            profile=profile,
        )

    if scenario.startswith("O"):
        return run_mod._run_oxigraph_benchmark(
            scenario=scenario,
            export_dir=export_dir,
            result=result,
            n_warmup=n_warmup,
            n_runs=n_runs,
            profile=profile,
        )

    raise ValueError(f"Unknown scenario: {scenario}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a reduced smoke benchmark (non-interactive).")
    p.add_argument("--profile", default="small-2d")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--scenarios",
        nargs="*",
        default=["P1", "P2", "M1", "M2", "O1", "O2"],
        help="Scenarios to run (default: all 6)",
    )
    p.add_argument(
        "--ram-levels",
        nargs="*",
        type=int,
        default=[8, 16],
        help="RAM palette in GB (docker compose MEMORY_LIMIT)",
    )
    p.add_argument("--n-warmup", type=int, default=1)
    p.add_argument("--n-runs", type=int, default=3)
    p.add_argument(
        "--queries",
        nargs="*",
        default=["Q1", "Q6", "Q8"],
        help="Query subset to validate pipeline (default: Q1 Q6 Q8)",
    )
    p.add_argument(
        "--dataset-source",
        choices=["auto", "hf", "generate"],
        default="auto",
        help="auto=use existing else hf else generate; hf=only hf; generate=only local generation",
    )
    p.add_argument(
        "--out-dir",
        default="",
        help="Output directory under benchmark_results (default: timestamped)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    run_mod = _load_run_module()

    scenarios = [s.upper() for s in args.scenarios]
    for s in scenarios:
        if s not in run_mod.SCENARIOS:
            raise SystemExit(f"Unknown scenario {s}. Valid: {list(run_mod.SCENARIOS.keys())}")

    # Patch query lists to reduce runtime
    selected_map = _select_queries(run_mod, scenarios, [q.upper() for q in args.queries])
    original_queries = dict(run_mod.QUERIES_BY_SCENARIO)

    # Scenarios that share TimescaleDB timeseries
    TIMESERIES_SCENARIOS = {"P1", "P2", "M2", "O2"}

    try:
        for s in scenarios:
            run_mod.QUERIES_BY_SCENARIO[s] = selected_map[s]

        # Phase 1: Ensure Parquet pivot exists (no scenario exports yet)
        export_dir = _ensure_parquet_pivot(run_mod, args.profile, args.seed, args.dataset_source)

        stamp = args.out_dir.strip() or f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_smoke_{args.profile}_seed{args.seed}"
        out_dir = Path("benchmark_results") / stamp
        out_dir.mkdir(parents=True, exist_ok=True)

        meta = {
            "profile": args.profile,
            "seed": args.seed,
            "scenarios": scenarios,
            "ram_levels_gb": args.ram_levels,
            "n_warmup": args.n_warmup,
            "n_runs": args.n_runs,
            "queries": {s: selected_map[s] for s in scenarios},
            "export_dir": str(export_dir),
            "workflow": "lazy_export_prune",
        }
        (out_dir / "smoke_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        all_results: Dict[str, Dict[int, Dict]] = {}

        # Track which timeseries-sharing scenarios have run
        ts_scenarios_done = set()

        for scenario in scenarios:
            all_results[scenario] = {}
            containers = run_mod.SCENARIOS[scenario]["containers"]

            # === LAZY EXPORT: export this scenario only ===
            print(f"\n[LAZY] Exporting {scenario}...")
            try:
                _export_scenario(args.profile, scenario, args.seed)
            except Exception as e:
                print(f"[ERROR] Export failed for {scenario}: {e}")
                all_results[scenario] = {ram: {"status": "error", "error": f"export_failed: {e}"} for ram in args.ram_levels}
                continue

            for ram_gb in args.ram_levels:
                print(f"\n=== SMOKE {scenario} @ {ram_gb}GB ===")

                # Start only required containers for this scenario with RAM limit
                ok = run_mod.start_containers_with_ram(containers, ram_gb)
                if not ok:
                    all_results[scenario][ram_gb] = {"status": "error", "error": "failed_to_start_containers"}
                    continue

                t0 = time.time()
                try:
                    res = _run_one(
                        run_mod,
                        scenario=scenario,
                        export_dir=export_dir,
                        profile=args.profile,
                        n_warmup=args.n_warmup,
                        n_runs=args.n_runs,
                    )
                    elapsed = time.time() - t0
                    res = res or {"status": "error", "error": "runner_returned_none"}
                    res["smoke_elapsed_s"] = elapsed
                    res["ram_gb"] = ram_gb
                    all_results[scenario][ram_gb] = res

                except Exception as e:
                    all_results[scenario][ram_gb] = {
                        "status": "error",
                        "error": repr(e),
                        "smoke_elapsed_s": time.time() - t0,
                        "ram_gb": ram_gb,
                    }

                finally:
                    run_mod.stop_all_containers()

                (out_dir / f"{scenario}_ram{ram_gb}.json").write_text(
                    json.dumps(all_results[scenario][ram_gb], indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

            # === PRUNE after all RAM levels for this scenario ===
            if scenario in TIMESERIES_SCENARIOS:
                ts_scenarios_done.add(scenario)
                # Check if all timeseries scenarios in our list are done
                ts_scenarios_in_run = set(scenarios) & TIMESERIES_SCENARIOS
                all_ts_done = ts_scenarios_done >= ts_scenarios_in_run

                # Keep timeseries if more TS scenarios to run
                keep_ts = not all_ts_done
                print(f"\n[PRUNE] {scenario} (keep_timeseries={keep_ts})")
                _prune_scenario(args.profile, scenario, args.seed, keep_timeseries=keep_ts)
            else:
                # M1/O1: no shared timeseries, prune everything
                print(f"\n[PRUNE] {scenario} (full prune)")
                _prune_scenario(args.profile, scenario, args.seed, keep_timeseries=False)

        (out_dir / "smoke_results.json").write_text(
            json.dumps(all_results, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(f"\nWrote smoke results to: {out_dir}")
        return 0

    finally:
        run_mod.QUERIES_BY_SCENARIO.clear()
        run_mod.QUERIES_BY_SCENARIO.update(original_queries)


if __name__ == "__main__":
    raise SystemExit(main())
