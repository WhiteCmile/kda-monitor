#!/usr/bin/env python3
"""Distribute baseline traces from baseline-results/ into workspace outputs/baseline.json.

Maps baseline-results/<group>/<problem>/traces.json → workspaces/<prefix>_<problem>/outputs/baseline.json
in the format bench.py expects.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

INFRA_DIR = Path(__file__).resolve().parent.parent
BASELINE_RESULTS_DIR = INFRA_DIR / "baseline-results"
WORKSPACES_DIR = INFRA_DIR / "workspaces"

GROUP_PREFIX = {
    "FlashInfer-Bench": "fi",
    "L1": "l1",
    "L2": "l2",
    "Quant": "q",
}


def extract_workload_results(raw_traces: list[dict]) -> list[dict]:
    """Extract per-workload results from raw traces (same logic as bench.py)."""
    results = []
    for i, trace in enumerate(raw_traces):
        ev = trace.get("evaluation", {})
        perf = ev.get("performance") or {}
        corr = ev.get("correctness") or {}
        results.append({
            "workload_index": i,
            "status": ev.get("status", "UNKNOWN"),
            "latency_ms": perf.get("latency_ms", 0.0),
            "reference_latency_ms": perf.get("reference_latency_ms", 0.0),
            "speedup": perf.get("speedup_factor", 0.0),
            "max_abs_err": corr.get("max_absolute_error", 0.0),
            "max_rel_err": corr.get("max_relative_error", 0.0),
            "passed": ev.get("status") == "PASSED",
        })
    return results


def main():
    distributed = 0
    skipped = 0
    missing_ws = 0

    for group_name, prefix in GROUP_PREFIX.items():
        group_dir = BASELINE_RESULTS_DIR / group_name
        if not group_dir.exists():
            continue

        for problem_dir in sorted(group_dir.iterdir()):
            if not problem_dir.is_dir():
                continue

            traces_file = problem_dir / "traces.json"
            if not traces_file.exists():
                skipped += 1
                continue

            # Map to workspace
            ws_name = f"{prefix}_{problem_dir.name}"
            ws_path = WORKSPACES_DIR / ws_name
            if not ws_path.exists():
                missing_ws += 1
                continue

            # Target file
            outputs_dir = ws_path / "outputs"
            outputs_dir.mkdir(parents=True, exist_ok=True)
            baseline_path = outputs_dir / "baseline.json"

            # Skip if already exists (don't overwrite)
            if baseline_path.exists():
                skipped += 1
                continue

            # Read traces and convert
            raw_traces = json.loads(traces_file.read_text())
            workload_results = extract_workload_results(raw_traces)

            baseline_data = {
                "task_id": ws_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "iterations": 50,
                "max_workloads": None,
                "raw_traces": raw_traces,
                "workload_results": workload_results,
            }

            baseline_path.write_text(json.dumps(baseline_data, indent=2))
            distributed += 1
            print(f"  ✓ {ws_name}")

    print(f"\nDone: {distributed} distributed, {skipped} skipped, {missing_ws} no matching workspace")


if __name__ == "__main__":
    main()
