#!/usr/bin/env python3
"""Rebuild the musical reference class through Flyvbjerg's public CLI.

The checked-in cohort fixture is the only research input. This script performs
no network access and no EDSL execution.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
COLLECTION = "theatrical_musicals"
METRICS = {
    "budget_low_musd": ("metric-budget-low.json", "numeric", "input", "million_usd"),
    "budget_high_musd": ("metric-budget-high.json", "numeric", "input", "million_usd"),
    "worldwide_gross_musd": ("metric-gross.json", "numeric", "outcome", "million_usd"),
    "gross_multiple_low": ("metric-multiple-low.json", "ratio", "outcome", "x"),
    "gross_multiple_high": ("metric-multiple-high.json", "ratio", "outcome", "x"),
}


class Workflow:
    def __init__(self, workspace: Path, *, verbose: bool) -> None:
        self.workspace = workspace
        self.verbose = verbose
        self.env = os.environ.copy()
        source_root = HERE.parents[1] / "src"
        existing = self.env.get("PYTHONPATH")
        self.env["PYTHONPATH"] = str(source_root) if not existing else f"{source_root}{os.pathsep}{existing}"

    def run(self, *args: str) -> dict[str, Any]:
        command = [sys.executable, "-m", "flyvbjerg", *map(str, args)]
        if self.verbose:
            print("$", " ".join(map(str, args if args else command)))
        result = subprocess.run(command, cwd=self.workspace, env=self.env, text=True, capture_output=True, check=False)
        if result.returncode:
            raise RuntimeError(f"command failed: {' '.join(command)}\n{result.stdout}\n{result.stderr}")
        envelope = json.loads(result.stdout)
        if envelope.get("status") != "ok":
            raise RuntimeError(result.stdout)
        return envelope

    def next(self, stage: str) -> None:
        result = self.run("next")
        if self.verbose:
            next_ids = [item["id"] for item in result.get("next_steps", [])]
            print(f"  next after {stage}: {', '.join(next_ids) or 'complete'}")


def rebuild(workspace: Path, *, verbose: bool = True) -> dict[str, Any]:
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    if (workspace / ".flyvbjerg").exists():
        raise RuntimeError(f"refusing to overwrite existing workspace: {workspace}")

    data = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    candidates = data["candidates"]
    included = [item for item in candidates if item["included"]]
    excluded = [item for item in candidates if not item["included"]]
    cli = Workflow(workspace, verbose=verbose)

    cli.run("init")
    cli.run("target", "create", "theatrical_musical", "--name", "Theatrical musical adaptation economics", "--from", str(HERE / "target.json"))
    cli.run("collection", "new", COLLECTION, "US theatrical stage-musical film adaptations, 2006–2025 seed cohort")
    cli.next("definition")

    for item in candidates:
        source_id = f"wiki_{item['id']}"
        cli.run("source", "add", COLLECTION, "--url", item["url"], "--title", f"{item['name']} — Wikipedia", "--kind", "encyclopedia", "--source-id", source_id)
        intake = cli.run("intake", "add", COLLECTION, source_id, "membership_candidate", item["membership_evidence"], "--proposed-name", item["name"])["data"]
        if item["included"]:
            cli.run("intake", "resolve-case", COLLECTION, intake["item_id"], "--new-case", item["id"], "--name", item["name"])
            update = workspace / f"{item['id']}-membership.json"
            update.write_text(json.dumps({"entity_type":"theatrical_film","context":{"release_year":item["year"],"membership_status":"included","membership_basis":item["membership_evidence"]}}), encoding="utf-8")
            cli.run("case", "update", COLLECTION, item["id"], "--from", str(update), "--source", source_id)
            update.unlink()
        else:
            cli.run("intake", "defer", COLLECTION, intake["item_id"], "--reason", item["exclusion_reason"])
    cli.next("outcome-independent enumeration")

    for metric_id, (filename, kind, role, unit) in METRICS.items():
        cli.run("metric", "add", COLLECTION, metric_id, "--kind", kind, "--role", role, "--unit", unit, "--from", str(HERE / filename))
    cli.next("metric definition")

    for item in included:
        values = {
            "budget_low_musd": item["budget_low"],
            "budget_high_musd": item["budget_high"],
            "worldwide_gross_musd": item["worldwide_gross"],
            "gross_multiple_low": round(item["worldwide_gross"] / item["budget_high"], 4),
            "gross_multiple_high": round(item["worldwide_gross"] / item["budget_low"], 4),
        }
        for metric_id, value in values.items():
            method = "calculated" if metric_id.startswith("gross_multiple") else "reported"
            observation = cli.run("observation", "add", COLLECTION, "--subject-kind", "case", "--subject", item["id"], "--metric", metric_id, "--value", str(value), "--source", f"wiki_{item['id']}", "--period", str(item["year"]), "--method", method)["data"]
            cli.run("observation", "decide", COLLECTION, observation["observation_id"], "--accept", "--reason", "Reported field or inspected calculation supported by the registered source; bounds preserved separately.")
            cli.run("coverage", "set", COLLECTION, "--subject-kind", "case", "--subject", item["id"], "--metric", metric_id, "--state", "observed", "--reason", "Accepted observation with complete inputs.")
    cli.next("measurement and evidence decisions")

    conservative = cli.run("analysis", "create", COLLECTION, "--name", "Conservative worldwide gross multiple", "--metric", "gross_multiple_low", "--target", "theatrical_musical", "--target-version", "1")["data"]
    optimistic = cli.run("analysis", "create", COLLECTION, "--name", "Optimistic worldwide gross multiple", "--metric", "gross_multiple_high", "--target", "theatrical_musical", "--target-version", "1")["data"]
    cli.next("frozen analyses")
    comparison = cli.run("comparison", "create", COLLECTION, "--name", "Production-budget bound sensitivity", "--analysis", conservative["analysis_id"], "--analysis", optimistic["analysis_id"])["data"]
    thresholds = cli.run("comparison", "threshold", comparison["comparison_id"], "--operator", "ge", "--value", "2.0", "--value", "2.5")["data"]
    cli.run("comparison", "plot", comparison["comparison_id"], "--output", str(workspace / "plots" / "budget-bound-comparison.svg"))
    cli.next("comparison sensitivity")
    validation = cli.run("validate")["data"]
    return {
        "workspace": str(workspace),
        "candidate_count": len(candidates),
        "included_count": len(included),
        "excluded_count": len(excluded),
        "observation_count": len(included) * len(METRICS),
        "analysis_ids": [conservative["analysis_id"], optimistic["analysis_id"]],
        "comparison_id": comparison["comparison_id"],
        "threshold_conclusions": {str(item["threshold"]["value"]): item["conclusion"] for item in thresholds["results"]},
        "distribution": conservative["distribution"],
        "validation": validation,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path, help="empty directory in which to build the workspace")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    print(json.dumps(rebuild(args.workspace, verbose=not args.quiet), indent=2))


if __name__ == "__main__":
    main()
