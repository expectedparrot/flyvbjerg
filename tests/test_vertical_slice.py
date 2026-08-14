from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from flyvbjerg.analysis import add_metric, cluster_sensitivity, create_analysis, derive_metric, locate_value, threshold_analysis
from flyvbjerg.cli import app
from flyvbjerg.comparison import create_comparison, load_comparison, threshold_comparison
from flyvbjerg.comparison_plotting import create_comparison_plot
from flyvbjerg.domain import add_case, add_decision, add_record
from flyvbjerg.processing import approve_plan, build_plan, create_plan
from flyvbjerg.plotting import create_plot
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


def test_evidence_guide_allows_best_available_sources(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    invoke(["init"])
    evidence = invoke(["guide", "--topic", "evidence"])["data"]
    assert "Wikipedia" in evidence["guidance"]
    assert "silence" in evidence["guidance"]
    assert "evidence" in evidence["available_topics"]


def test_metric_can_be_fully_defined_inline(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    invoke(["init"])
    invoke(["collection", "new", "films", "Films"])
    created = invoke([
        "metric", "add", "films", "gross_multiple", "--kind", "ratio", "--role", "outcome", "--unit", "x",
        "--subject-kind", "case", "--label", "Gross multiple", "--definition", "Gross divided by budget",
        "--zero-policy", "Missing inputs remain missing",
    ])["data"]
    assert created["subject_kinds"] == ["case"]
    assert created["label"] == "Gross multiple"
    assert created["definition"] == "Gross divided by budget"
    assert created["zero_policy"] == "Missing inputs remain missing"


def test_effective_intake_status_and_next(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    invoke(["init"])
    invoke(["target", "create", "decision", "--name", "Decision"])
    invoke(["collection", "new", "history", "History"])
    invoke(["source", "add", "history", "--url", "https://example.test", "--source-id", "source"])
    first = invoke(["intake", "add", "history", "source", "history", "First"])["data"]
    second = invoke(["intake", "add", "history", "source", "history", "Second"])["data"]
    invoke(["intake", "defer", "history", first["item_id"], "--reason", "Out of scope"])
    invoke(["intake", "resolve-case", "history", second["item_id"], "--new-case", "company", "--name", "Company"])
    items = invoke(["intake", "list", "history"])["data"]
    assert {item["status"] for item in items} == {"deferred", "resolved"}
    next_result = invoke(["next"])
    assert next_result["data"]["unresolved_intake_count"] == 0
    assert next_result["next_steps"][0]["id"] == "register_evidence"


def test_qualitative_claim_decision_and_sourced_case_update(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    invoke(["init"])
    invoke(["collection", "new", "history", "History"])
    invoke(["source", "add", "history", "--url", "https://en.wikipedia.org/wiki/Example", "--kind", "encyclopedia", "--source-id", "wiki"])
    invoke(["case", "add", "history", "--id", "company", "--name", "Company"])
    claim = invoke(["claim", "add", "history", "--scope-kind", "case", "--scope", "company", "--claim-kind", "qualitative_assessment", "--source", "wiki", "--value", '"Entered an adjacent market"'])["data"]
    decision = invoke(["claim", "decide", "history", claim["claim_id"], "--accept", "--reason", "Supported descriptive history"])["data"]
    assert decision["subject_kind"] == "claim"
    assert decision["decision"] == "accepted"
    shown = invoke(["claim", "show", "history", claim["claim_id"]])["data"]
    assert shown["effective_status"] == "accepted"
    assert invoke(["claim", "list", "history", "--status", "accepted"])["data"][0]["claim_id"] == claim["claim_id"]
    update = tmp_path / "case-update.json"
    update.write_text(json.dumps({"context": {"principal_line": "legacy product", "threat_anchor": "2000"}}), encoding="utf-8")
    changed = invoke(["case", "update", "history", "company", "--from", str(update), "--source", "wiki"])["data"]
    assert changed["context"]["principal_line"] == "legacy product"
    assert changed["source_ids"] == ["wiki"]


def test_intake_can_resolve_to_claim_and_relationship(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    invoke(["init"])
    invoke(["collection", "new", "history", "History"])
    invoke(["source", "add", "history", "--url", "https://example.test", "--source-id", "source"])
    invoke(["case", "add", "history", "--id", "old", "--name", "Old"])
    invoke(["case", "add", "history", "--id", "new", "--name", "New"])
    claim_item = invoke(["intake", "add", "history", "source", "action", "Entered market"])["data"]
    relationship_item = invoke(["intake", "add", "history", "source", "identity", "Old became New"])["data"]
    claim_resolution = invoke(["intake", "resolve-claim", "history", claim_item["item_id"], "--scope-kind", "case", "--scope", "old", "--claim-kind", "qualitative_assessment", "--value", '"Entered market"'])["data"]
    relationship_resolution = invoke(["intake", "resolve-relationship", "history", relationship_item["item_id"], "--from", "old", "--type", "became", "--to", "new"])["data"]
    assert claim_resolution["resolution_kind"] == "claim"
    assert relationship_resolution["resolution_kind"] == "relationship"
    assert invoke(["intake", "list", "history", "--status", "resolved"])["data"]


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
    assert analysis["dependence_status"] == "assessed_with_clusters"
    assert analysis["distribution"]["quantile_convention"] == "nearest_rank"
    assert analysis["distribution"]["quantiles"]["0.5"] == 3_064_847
    assert analysis["target"]["version"] == 1
    sensitivity = cluster_sensitivity(root, analysis["analysis_id"])
    assert len(sensitivity["results"]) == 2
    threshold = threshold_analysis(root, analysis["analysis_id"], "le", 3_100_000)
    assert threshold["count_matching"] == 2
    assert threshold["frequency"] == 2 / 3
    located = locate_value(root, analysis["analysis_id"], 3_100_000, "inside view")
    assert located["empirical_rank"] == 2 / 3
    assert located["label"] == "inside view"
    for kind in ("ecdf", "ordered"):
        output = tmp_path / f"attendance-{kind}.svg"
        receipt, artifacts = create_plot(root, analysis["analysis_id"], kind, output, target_value=3_100_000, threshold=3_100_000)
        assert receipt["kind"] == kind
        assert output.read_text(encoding="utf-8").startswith("<svg")
        assert output.with_suffix(".plot.json").exists()
        assert len(artifacts) == 2


def test_multi_terminal_event_derivation_and_unassessed_dependence(tmp_path: Path) -> None:
    root, _ = initialize(tmp_path)
    collection = seed_mlb(root)
    add_record(root, collection, "event", {"type": "cancelled", "case_ids": ["rays"], "date": "1996-01-01", "date_precision": "day", "source_id": "src-mlb"})
    definition, _ = add_metric(root, collection, {
        "metric_id": "award-to-terminal-days",
        "kind": "numeric",
        "role": "duration",
        "unit": "days",
        "derivation": {
            "kind": "event_interval",
            "start_event_type": "franchise_awarded",
            "end_event_types": ["inaugural_regular_season_game", "cancelled"],
            "selection": "first_terminal_event",
        },
    })
    derived = derive_metric(root, collection, definition["metric_id"], subjects=["rays"])
    assert derived["created"][0]["terminal_event_type"] == "cancelled"
    observation = derived["created"][0]
    add_decision(root, collection, "observation", observation["observation_id"], "accepted", "verified")
    add_record(root, collection, "coverage", {"subject": {"kind": "case", "id": "rays"}, "metric_id": definition["metric_id"], "state": "observed", "reason": "derived"})
    analysis, _ = create_analysis(root, collection, "Terminal", definition["metric_id"])
    assert analysis["dependence_status"] == "not_assessed"
    assert analysis["n_clusters"] is None


def test_analysis_uses_only_latest_metric_version(tmp_path: Path) -> None:
    root, _ = initialize(tmp_path)
    collection = seed_mlb(root)
    first, _ = add_metric(root, collection, {"metric_id": "score", "kind": "numeric", "role": "outcome"})
    old, _ = add_record(root, collection, "observation", {"subject": {"kind": "case", "id": "rockies"}, "metric": {"id": "score", "version": first["version"]}, "value": 1, "status": "candidate"})
    add_decision(root, collection, "observation", old["observation_id"], "accepted", "verified")
    second, _ = add_metric(root, collection, {"metric_id": "score", "kind": "numeric", "role": "outcome"})
    new, _ = add_record(root, collection, "observation", {"subject": {"kind": "case", "id": "rockies"}, "metric": {"id": "score", "version": second["version"]}, "value": 2, "status": "candidate"})
    add_decision(root, collection, "observation", new["observation_id"], "accepted", "verified")
    add_record(root, collection, "coverage", {"subject": {"kind": "case", "id": "rockies"}, "metric_id": "score", "state": "observed", "reason": "verified"})
    analysis, _ = create_analysis(root, collection, "Latest only", "score")
    assert analysis["metric"]["version"] == 2
    assert analysis["distribution"]["values"] == [2]


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


def test_frozen_analysis_comparison_thresholds_and_plot(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    root, _ = initialize(tmp_path)
    versioned_write(root / "targets" / "film", {"target_id": "film", "name": "Film", "status": "ready_for_analysis"}, id_field="target_id")
    collection = seed_mlb(root)
    for metric_id, values in (
        ("low", {"rockies": 0.8, "marlins": 1.8, "rays": 2.6}),
        ("high", {"rockies": 1.2, "marlins": 2.2, "rays": 2.9}),
    ):
        definition, _ = add_metric(root, collection, {"metric_id": metric_id, "kind": "ratio", "role": "outcome", "unit": "x"})
        for subject, value in values.items():
            observation, _ = add_record(root, collection, "observation", {"subject": {"kind": "case", "id": subject}, "metric": {"id": metric_id, "version": definition["version"]}, "value": value, "status": "candidate"})
            add_decision(root, collection, "observation", observation["observation_id"], "accepted", "verified")
            add_record(root, collection, "coverage", {"subject": {"kind": "case", "id": subject}, "metric_id": metric_id, "state": "observed", "reason": "verified"})

    low, _ = create_analysis(root, collection, "Conservative", "low")
    high, _ = create_analysis(root, collection, "Optimistic", "high")
    assert invoke(["next"])["next_steps"][0]["id"] == "compare_analyses"
    comparison, artifact = create_comparison(root, collection, "Budget bounds", [low["analysis_id"], high["analysis_id"]])
    assert Path(artifact["path"]).exists()
    assert comparison["subject_sets_equal"] is True
    assert comparison["metrics_equal"] is False
    assert comparison["common_subject_ids"] == ["marlins", "rays", "rockies"]
    assert comparison["distribution_deltas"][1]["median_from_baseline"] == pytest.approx(0.4)
    assert load_comparison(root, comparison["comparison_id"])["analysis_ids"] == [low["analysis_id"], high["analysis_id"]]

    sensitivity, threshold_artifact = threshold_comparison(root, comparison["comparison_id"], "ge", [1.0, 2.5])
    assert Path(threshold_artifact["path"]).exists()
    first, second = sensitivity["results"]
    assert first["conclusion"] == "assumption_sensitive"
    assert [item["subject_id"] for item in first["classification_switches"]] == ["rockies"]
    assert second["classification_invariant"] is True
    assert second["conclusion"] == "robust"

    output = tmp_path / "comparison.svg"
    receipt, artifacts = create_comparison_plot(root, comparison["comparison_id"], output)
    assert receipt["analysis_ids"] == [low["analysis_id"], high["analysis_id"]]
    assert output.read_text(encoding="utf-8").startswith("<svg")
    assert output.with_suffix(".comparison-plot.json").exists()
    assert len(artifacts) == 2

    incomplete_definition, _ = add_metric(root, collection, {"metric_id": "incomplete", "kind": "ratio", "role": "outcome", "unit": "x"})
    for subject, value in (("rockies", 0.8), ("marlins", "not_disclosed"), ("rays", 2.6)):
        observation, _ = add_record(root, collection, "observation", {"subject": {"kind": "case", "id": subject}, "metric": {"id": "incomplete", "version": incomplete_definition["version"]}, "value": value, "status": "candidate"})
        add_decision(root, collection, "observation", observation["observation_id"], "accepted", "verified")
        add_record(root, collection, "coverage", {"subject": {"kind": "case", "id": subject}, "metric_id": "incomplete", "state": "observed" if isinstance(value, float) else "not_disclosed", "reason": "test coverage"})
    incomplete, _ = create_analysis(root, collection, "Incomplete", "incomplete")
    missing_comparison, _ = create_comparison(root, collection, "Missingness", [low["analysis_id"], incomplete["analysis_id"]])
    missing_threshold, _ = threshold_comparison(root, missing_comparison["comparison_id"], "ge", [1.0])
    missing_result = missing_threshold["results"][0]
    assert missing_result["conclusion"] == "assumption_sensitive"
    assert missing_result["missingness_changes"] == [{
        "subject_id": "marlins",
        "baseline_analysis_id": low["analysis_id"],
        "comparison_analysis_id": incomplete["analysis_id"],
        "baseline_missing": False,
        "comparison_missing": True,
    }]


def test_comparison_cli_contract(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    invoke(["init"])
    invoke(["collection", "new", "history", "History"])
    # Command-level validation is structured and refuses a one-analysis comparison.
    result = runner.invoke(app, ["comparison", "create", "history", "--name", "Invalid", "--analysis", "missing"])
    assert result.exit_code == 1
    envelope = json.loads(result.stdout)
    assert envelope["status"] == "error"
    assert envelope["errors"][0]["code"] == "VALIDATION_ERROR"
    assert "at least two analyses" in envelope["errors"][0]["message"]
