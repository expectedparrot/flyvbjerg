from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from flyvbjerg.analysis import add_metric, cluster_sensitivity, create_analysis, derive_metric
from flyvbjerg.cli import app
from flyvbjerg.domain import add_case, add_decision, add_record
from flyvbjerg.processing import approve_plan, build_plan, create_plan
from flyvbjerg.workspace import atomic_write, collection_root, initialize, versioned_write


runner = CliRunner()


def invoke(args: list[str]) -> dict:
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    envelope = json.loads(result.stdout)
    assert envelope["schema_version"] == "1.0"
    assert envelope["status"] == "ok"
    return envelope


def test_agent_cli_orientation_and_target_gaps(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    invoke(["init"])
    target_file = tmp_path / "target.json"
    target_file.write_text(json.dumps({"unknown": ["city", "launch_year"]}), encoding="utf-8")
    created = invoke(["target", "create", "new-team", "--name", "New team", "--from", str(target_file)])
    assert created["data"]["version"] == 1
    gaps = invoke(["target", "gaps", "new-team"])
    assert gaps["data"]["gaps"] == ["city", "launch_year"]
    assert gaps["data"]["ready_for_analysis"] is False
    step = invoke(["next"])["next_steps"][0]
    assert step["requires_network"] is False


def seed_mlb(root: Path) -> str:
    collection = "mlb-expansion"
    base = collection_root(root, collection, require=False)
    atomic_write(base / "collection.json", {"collection_id": collection, "title": "MLB expansion", "status": "exploratory"})
    for directory in ("events", "groups", "observations", "coverage", "decisions", "metrics", "cases", "analysis-sets", "claims", "relationships", "intake/sources", "intake/items", "intake/resolutions"):
        (base / directory).mkdir(parents=True, exist_ok=True)
    source, _ = add_record(root, collection, "source", {"source_id": "src-mlb", "url": "https://example.test", "kind": "article"})
    for case_id, capacity in (("rockies", 50000), ("marlins", 45000), ("rays", None)):
        context = {"venue_capacity": capacity} if capacity else {}
        add_case(root, collection, {"case_id": case_id, "name": case_id.title(), "entity_type": "mlb_expansion_franchise", "context": context})
    for case_id, start, end in (("rockies", "1991-06-01", "1993-04-05"), ("marlins", "1991-06-01", "1993-04-05"), ("rays", "1995-03-09", "1998-03-31")):
        add_record(root, collection, "event", {"type": "franchise_awarded", "case_ids": [case_id], "date": start, "date_precision": "day", "source_id": source["source_id"]})
        add_record(root, collection, "event", {"type": "inaugural_regular_season_game", "case_ids": [case_id], "date": end, "date_precision": "day", "source_id": source["source_id"]})
    add_record(root, collection, "group", {"group_id": "expansion-1993", "kind": "expansion_program", "members": ["rockies", "marlins"], "dependence_reason": "shared expansion program"})
    add_record(root, collection, "group", {"group_id": "expansion-1998", "kind": "expansion_program", "members": ["rays"], "dependence_reason": "shared expansion program"})
    return collection


def test_event_derivation_context_and_clusters(tmp_path: Path) -> None:
    root, _ = initialize(tmp_path)
    versioned_write(root / "targets" / "new-team", {"target_id": "new-team", "name": "New team", "status": "underspecified", "unknown": ["city"]}, id_field="target_id")
    collection = seed_mlb(root)
    derived_definition = {
        "metric_id": "award-to-first-game-days",
        "kind": "numeric",
        "role": "duration",
        "unit": "days",
        "derivation": {"kind": "event_interval", "start_event_type": "franchise_awarded", "end_event_type": "inaugural_regular_season_game", "selection": "unique_per_case", "date_precision_required": "day"},
    }
    add_metric(root, collection, derived_definition)
    result = derive_metric(root, collection, "award-to-first-game-days")
    assert len(result["created"]) == 3
    assert all(len(item["input_event_ids"]) == 2 for item in result["created"])
    # A second plausible endpoint must produce a gap, not a guessed choice.
    add_record(root, collection, "event", {"type": "inaugural_regular_season_game", "case_ids": ["rays"], "date": "1998-04-01", "date_precision": "day", "source_id": "src-mlb"})
    ambiguous = derive_metric(root, collection, "award-to-first-game-days", subjects=["rays"], dry_run=True)
    assert ambiguous["created"] == []
    assert ambiguous["gaps"][0]["code"] == "AMBIGUOUS_OR_MISSING_ENDPOINT"

    attendance, _ = add_metric(root, collection, {"metric_id": "attendance", "kind": "numeric", "role": "outcome", "unit": "people", "required_context": ["venue_capacity"], "missing_context_policy": "warn"})
    for case_id, value in (("rockies", 4_483_350), ("marlins", 3_064_847), ("rays", 2_506_293)):
        observation, _ = add_record(root, collection, "observation", {"subject": {"kind": "case", "id": case_id}, "metric": {"id": "attendance", "version": attendance["version"]}, "value": value, "status": "candidate"})
        add_decision(root, collection, "observation", observation["observation_id"], "accepted", "verified")
        add_record(root, collection, "coverage", {"subject": {"kind": "case", "id": case_id}, "metric_id": "attendance", "state": "observed", "reason": "accepted observation"})
    analysis, warnings = create_analysis(root, collection, "First pass", "attendance", "new-team", clusters=["expansion-1993", "expansion-1998"])
    assert warnings and "rays" in warnings[0]
    assert analysis["n_subjects"] == 3
    assert analysis["n_clusters"] == 2
    assert analysis["target"]["version"] == 1
    sensitivity = cluster_sensitivity(root, analysis["analysis_id"])
    assert len(sensitivity["results"]) == 2


def test_error_is_a_single_json_envelope(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 1
    envelope = json.loads(result.stdout)
    assert envelope["status"] == "error"
    assert envelope["errors"][0]["code"] == "NOT_FOUND"


def test_bounded_edsl_build_uses_registered_capture_and_never_runs(tmp_path: Path) -> None:
    root, _ = initialize(tmp_path)
    collection = seed_mlb(root)
    capture_text = tmp_path / "evidence.txt"
    capture_text.write_text("The league awarded the franchise on the stated date.", encoding="utf-8")
    from flyvbjerg.domain import add_capture

    capture, _ = add_capture(root, collection, "src-mlb", capture_text)
    plan, _ = create_plan(root, collection, "Extract dates", "extract", [capture["capture_id"]])
    approve_plan(root, plan["run_id"])
    manifest, artifacts = build_plan(root, plan["run_id"])
    assert manifest["scenario_count"] == 1
    assert manifest["capture_ids"] == [capture["capture_id"]]
    assert manifest["executes_models"] is False
    assert Path(manifest["jobs_path"]).exists()
    assert any(item["role"] == "edsl_jobs" for item in artifacts)
