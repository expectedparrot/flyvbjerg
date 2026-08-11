from __future__ import annotations

from pathlib import Path
from typing import Any

from .domain import load_capture
from .edsl_bridge import audit_results, build_jobs, save_and_verify
from .errors import ValidationError
from .workspace import atomic_write, collection_root, new_id, now, read_json


def create_plan(root: Path, collection: str, name: str, mode: str, captures: list[str], task: str = "") -> tuple[dict[str, Any], dict[str, Any]]:
    if mode not in {"extract", "code", "verify"}:
        raise ValidationError("mode must be extract, code, or verify")
    if not captures:
        raise ValidationError("At least one registered capture id is required")
    for capture in captures:
        load_capture(root, collection, capture)
    run_id = new_id("run")
    record = {"run_id": run_id, "collection_id": collection, "name": name, "mode": mode, "capture_ids": captures, "task": task, "status": "planned", "approved": False, "created_at": now()}
    artifact = atomic_write(collection_root(root, collection) / "runs" / run_id / "plan.json", record)
    return record, artifact


def find_run(root: Path, run_id: str) -> tuple[Path, dict[str, Any]]:
    matches = list((root / "collections").glob(f"*/runs/{run_id}/plan.json"))
    if not matches:
        raise ValidationError(f"Run not found: {run_id}")
    return matches[0].parent, read_json(matches[0])


def approve_plan(root: Path, run_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    run_dir, plan = find_run(root, run_id)
    approval = {"run_id": run_id, "plan_sha256": None, "approved": True, "approved_at": now()}
    artifact = atomic_write(run_dir / "approval.json", approval)
    return approval, artifact


def build_plan(root: Path, run_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    run_dir, plan = find_run(root, run_id)
    if not (run_dir / "approval.json").is_file():
        raise ValidationError("Processing plan is not approved", f"Run `flyvbjerg process approve {run_id}` first.")
    collection = plan["collection_id"]
    collection_record = read_json(collection_root(root, collection) / "collection.json")
    scenarios = []
    for capture_id in plan["capture_ids"]:
        capture = load_capture(root, collection, capture_id)
        capture_path = collection_root(root, collection) / "intake" / "captures" / capture_id / capture["file"]
        try:
            text = capture_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"Capture is not UTF-8 text: {capture_id}") from exc
        scenarios.append({"collection_id": collection, "collection_title": collection_record["title"], "capture_id": capture_id, "capture_sha256": capture["sha256"], "capture_text": text, "task": plan.get("task", "")})
    jobs = build_jobs(plan["mode"], scenarios)
    jobs_artifact = save_and_verify(jobs, run_dir / "jobs.ep")
    manifest = {"run_id": run_id, "mode": plan["mode"], "capture_ids": plan["capture_ids"], "scenario_count": len(scenarios), "jobs_path": jobs_artifact["path"], "executes_models": False, "created_at": now()}
    manifest_artifact = atomic_write(run_dir / "manifest.json", manifest)
    return manifest, [jobs_artifact, manifest_artifact]


def register_results(root: Path, run_id: str, input_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    run_dir, _ = find_run(root, run_id)
    result_id = new_id("results")
    destination = run_dir / "results" / f"{result_id}.results.ep"
    destination.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(input_path, destination)
    record = {"result_set_id": result_id, "run_id": run_id, "path": str(destination), "registered_at": now()}
    artifact = atomic_write(run_dir / "results" / f"{result_id}.json", record)
    return record, artifact


def audit_run(root: Path, run_id: str, result_set_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    run_dir, _ = find_run(root, run_id)
    registration = read_json(run_dir / "results" / f"{result_set_id}.json")
    audit = {"run_id": run_id, "result_set_id": result_set_id, **audit_results(run_dir / "jobs.ep", Path(registration["path"])), "audited_at": now()}
    artifact = atomic_write(run_dir / f"{result_set_id}.audit.json", audit)
    return audit, artifact

