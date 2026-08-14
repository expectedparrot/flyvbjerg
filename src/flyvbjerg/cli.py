from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

import typer
from typer.main import get_command
from typer._click.exceptions import Exit as ClickExit
from typer._click.exceptions import UsageError as ClickUsageError

from . import __version__
from .analysis import add_metric, cluster_sensitivity, create_analysis, derive_metric, load_analysis, locate_value, metric, threshold_analysis
from .comparison import create_comparison, load_comparison, threshold_comparison
from .comparison_plotting import create_comparison_plot
from .domain import add_capture, add_case, add_decision, add_record, get_case, get_record, list_records
from .envelope import Envelope
from .errors import FlyvbjergError, ValidationError
from .processing import approve_plan, audit_run, build_plan, create_plan, find_run, register_results
from .plotting import create_plot
from .workspace import atomic_write, collection_root, discover, initialize, json_value, load_version, now, read_input, read_json, records, versioned_write

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
target_app = typer.Typer(no_args_is_help=True)
collection_app = typer.Typer(no_args_is_help=True)
source_app = typer.Typer(no_args_is_help=True)
capture_app = typer.Typer(no_args_is_help=True)
intake_app = typer.Typer(no_args_is_help=True)
case_app = typer.Typer(no_args_is_help=True)
event_app = typer.Typer(no_args_is_help=True)
relationship_app = typer.Typer(no_args_is_help=True)
group_app = typer.Typer(no_args_is_help=True)
claim_app = typer.Typer(no_args_is_help=True)
metric_app = typer.Typer(no_args_is_help=True)
observation_app = typer.Typer(no_args_is_help=True)
coverage_app = typer.Typer(no_args_is_help=True)
analysis_app = typer.Typer(no_args_is_help=True)
comparison_app = typer.Typer(no_args_is_help=True)
sensitivity_app = typer.Typer(no_args_is_help=True)
process_app = typer.Typer(no_args_is_help=True)

for name, child in (("target", target_app), ("collection", collection_app), ("source", source_app), ("capture", capture_app), ("intake", intake_app), ("case", case_app), ("event", event_app), ("relationship", relationship_app), ("group", group_app), ("claim", claim_app), ("metric", metric_app), ("observation", observation_app), ("coverage", coverage_app), ("analysis", analysis_app), ("comparison", comparison_app), ("sensitivity", sensitivity_app), ("process", process_app)):
    app.add_typer(child, name=name)


def emit(command: str, action: Callable[[], Any]) -> None:
    try:
        result = action()
        if isinstance(result, Envelope):
            envelope = result
        else:
            envelope = Envelope(command=command, data=result)
    except FlyvbjergError as exc:
        envelope = Envelope(command=command, status="error", errors=[{"code": exc.code, "message": exc.message, "hint": exc.hint}])
        typer.echo(json.dumps(envelope.to_dict(), ensure_ascii=False))
        raise typer.Exit(exc.exit_code)
    typer.echo(json.dumps(envelope.to_dict(), ensure_ascii=False))


def artifact_envelope(command: str, record: dict[str, Any], artifact: dict[str, Any], *, warnings: list[str] | None = None) -> Envelope:
    return Envelope(command=command, data=record, artifacts=[artifact], warnings=warnings or [])


def payload(path: Path | None, inline: dict[str, Any]) -> dict[str, Any]:
    return {**(read_input(path) if path else {}), **{key: value for key, value in inline.items() if value is not None}}


@app.command()
def version() -> None:
    emit("flyvbjerg version", lambda: {"version": __version__})


@app.command("init")
def init_command(path: Path = Path(".")) -> None:
    def action() -> Envelope:
        root, artifact = initialize(path)
        return artifact_envelope("flyvbjerg init", {"workspace": str(root)}, artifact)
    emit("flyvbjerg init", action)


@app.command()
def guide(topic: str | None = None) -> None:
    stages = ["target", "collection", "intake", "triage", "metrics", "decisions", "analysis", "comparison", "optional_edsl", "forecast"]
    guidance = {
        "evidence": (
            "Use the best available evidence for the task. Wikipedia and similar tertiary sources are valid for company histories, "
            "identities, ownership, products, chronology, and reported actions. Prefer stronger sources when readily available or "
            "when a claim is disputed, causal, quantitative, determines cohort membership, or asserts an absence. Do not treat a "
            "source's silence as evidence that an event did not occur. Register every source used and preserve permitted captures."
        ),
        "missingness": (
            "Preserve missing, not applicable, censored, conflicted, not found, and invalid states. A failed retrieval, malformed "
            "result, or source omission is never a zero or negative finding."
        ),
        "claims": (
            "Extracted claims remain candidates until explicitly accepted or rejected. Qualitative claims may be accepted without "
            "inventing a metric; promotion to an observation remains a separate compatibility-checked action."
        ),
        "comparison": (
            "Compare two or more frozen analyses without mutating them. Preserve cohort, metric, target, quantile, missingness, "
            "and dependence differences. Threshold comparison receipts identify case-level classification switches and label a "
            "conclusion robust only when subject sets, missingness, classifications, and frequencies are invariant."
        ),
    }
    selected = topic or "lifecycle"
    emit("flyvbjerg guide", lambda: {
        "topic": selected,
        "boundary": "The agent researches; Flyvbjerg only organizes registered evidence.",
        "stages": stages,
        "guidance": guidance.get(selected),
        "available_topics": ["lifecycle", *guidance],
    })


def effective_intake(collection_base: Path) -> list[dict[str, Any]]:
    items = records(collection_base / "intake/items")
    resolutions = records(collection_base / "intake/resolutions")
    by_item: dict[str, list[dict[str, Any]]] = {}
    for resolution in resolutions:
        by_item.setdefault(resolution["item_id"], []).append(resolution)
    result = []
    for item in items:
        linked = by_item.get(item["item_id"], [])
        status = item.get("status", "untriaged")
        if linked:
            status = "deferred" if all(x.get("resolution_kind") == "deferred" for x in linked) else "resolved"
        result.append({**item, "status": status, "resolution_ids": [x["resolution_id"] for x in linked]})
    return result


def with_decisions(root: Path, collection: str, kind: str, record: dict[str, Any]) -> dict[str, Any]:
    record_id = record[f"{kind}_id"]
    decisions = [
        x for x in records(collection_root(root, collection) / "decisions")
        if x.get("subject_kind") == kind and x.get("subject_id") == record_id
    ]
    return {**record, "effective_status": decisions[-1]["decision"] if decisions else record.get("status"), "decisions": decisions}


def next_state(root: Path) -> Envelope:
    targets = list((root / "targets").glob("*/v*.json"))
    collections = records(root / "collections", "*/collection.json")
    unresolved = 0
    if not targets:
        step = {"id": "create_target", "purpose": "Describe the decision to inform", "command": "flyvbjerg target create TARGET --name NAME", "mutates_state": True, "requires_network": False, "requires_user_approval": False}
    elif not collections:
        step = {"id": "create_collection", "purpose": "Create an exploratory evidence corpus", "command": "flyvbjerg collection new COLLECTION TITLE", "mutates_state": True, "requires_network": False, "requires_user_approval": False}
    else:
        unresolved_by_collection = {
            c["collection_id"]: [x for x in effective_intake(root / "collections" / c["collection_id"]) if x["status"] == "untriaged"]
            for c in collections
        }
        unresolved = sum(len(items) for items in unresolved_by_collection.values())
        step = {"id": "review_intake", "purpose": "Resolve or defer registered intake", "command": f"flyvbjerg intake list {collections[0]['collection_id']}", "mutates_state": False, "requires_network": False, "requires_user_approval": False}
        if unresolved == 0:
            step = {"id": "register_evidence", "purpose": "Register evidence found by the agent", "command": f"flyvbjerg source add {collections[0]['collection_id']} --url URL", "mutates_state": True, "requires_network": False, "requires_user_approval": False}
            for candidate_collection in collections:
                candidate_base = root / "collections" / candidate_collection["collection_id"]
                analyses = list(candidate_base.glob("analysis-sets/*/analysis.json"))
                comparisons = list(candidate_base.glob("comparison-sets/*/comparison.json"))
                if len(analyses) >= 2 and not comparisons:
                    analysis_ids = [read_json(path)["analysis_id"] for path in analyses[:2]]
                    step = {"id": "compare_analyses", "purpose": "Test whether conclusions survive alternative frozen analyses", "command": f"flyvbjerg comparison create {candidate_collection['collection_id']} --name NAME --analysis {analysis_ids[0]} --analysis {analysis_ids[1]}", "mutates_state": True, "requires_network": False, "requires_user_approval": False}
                    break
    data = {"workspace": read_json(root / "workspace.json"), "target_count": len({p.parent.name for p in targets}), "collection_count": len(collections)}
    if collections:
        data["unresolved_intake_count"] = unresolved
        data["analysis_count"] = len(list((root / "collections").glob("*/analysis-sets/*/analysis.json")))
        data["comparison_count"] = len(list((root / "collections").glob("*/comparison-sets/*/comparison.json")))
    return Envelope(command="flyvbjerg next", data=data, next_steps=[step])


@app.command("next")
def next_command() -> None:
    emit("flyvbjerg next", lambda: next_state(discover()))


@app.command()
def status() -> None:
    def action() -> dict[str, Any]:
        root = discover()
        collections = records(root / "collections", "*/collection.json")
        return {"workspace": read_json(root / "workspace.json"), "targets": len({p.parent for p in (root / "targets").glob("*/v*.json")}), "collections": collections}
    emit("flyvbjerg status", action)


@target_app.command("create")
def target_create(target_id: str, name: str = typer.Option(...), from_file: Path | None = typer.Option(None, "--from")) -> None:
    def action() -> Envelope:
        root = discover()
        record, artifact = versioned_write(root / "targets" / target_id, payload(from_file, {"target_id": target_id, "name": name, "status": "underspecified"}), id_field="target_id")
        return artifact_envelope("flyvbjerg target create", record, artifact)
    emit("flyvbjerg target create", action)


@target_app.command("revise")
def target_revise(target_id: str, from_file: Path = typer.Option(..., "--from")) -> None:
    def action() -> Envelope:
        root = discover(); current = load_version(root / "targets" / target_id)
        record, artifact = versioned_write(root / "targets" / target_id, {**current, **read_input(from_file), "target_id": target_id}, id_field="target_id")
        return artifact_envelope("flyvbjerg target revise", record, artifact)
    emit("flyvbjerg target revise", action)


@target_app.command("show")
def target_show(target_id: str, version: int | None = None) -> None:
    emit("flyvbjerg target show", lambda: load_version(discover() / "targets" / target_id, version))


@target_app.command("list")
def target_list() -> None:
    emit("flyvbjerg target list", lambda: [load_version(path) for path in sorted((discover() / "targets").iterdir()) if path.is_dir()])


@target_app.command("gaps")
def target_gaps(target_id: str, version: int | None = None) -> None:
    def action() -> dict[str, Any]:
        item = load_version(discover() / "targets" / target_id, version)
        unknown = item.get("unknown", [])
        return {"target": {"id": target_id, "version": item["version"]}, "status": item.get("status"), "gaps": unknown, "ready_for_analysis": item.get("status") == "ready_for_analysis" and not unknown}
    emit("flyvbjerg target gaps", action)


@collection_app.command("new")
def collection_new(collection_id: str, title: str) -> None:
    def action() -> Envelope:
        root = discover(); base = collection_root(root, collection_id, require=False)
        record = {"collection_id": collection_id, "title": title, "status": "exploratory", "definition_version": 0, "created_at": now()}
        artifact = atomic_write(base / "collection.json", record)
        for directory in ("intake/sources", "intake/captures", "intake/items", "intake/resolutions", "claims", "cases", "groups", "events", "relationships", "metrics", "observations", "coverage", "decisions", "analysis-sets", "comparison-sets", "runs", "forecasts"):
            (base / directory).mkdir(parents=True, exist_ok=True)
        return artifact_envelope("flyvbjerg collection new", record, artifact)
    emit("flyvbjerg collection new", action)


@collection_app.command("list")
def collection_list() -> None:
    emit("flyvbjerg collection list", lambda: records(discover() / "collections", "*/collection.json"))


@collection_app.command("show")
def collection_show(collection_id: str) -> None:
    emit("flyvbjerg collection show", lambda: read_json(collection_root(discover(), collection_id) / "collection.json"))


@source_app.command("add")
def source_add(collection: str, url: str | None = None, file: Path | None = None, title: str | None = None, kind: str | None = None, source_id: str | None = None) -> None:
    def action() -> Envelope:
        if not url and not file: raise ValidationError("Provide --url or --file")
        root = discover(); record, artifact = add_record(root, collection, "source", {"source_id": source_id, "url": url, "title": title or (file.name if file else url), "kind": kind or "unknown", "retrieved": now()})
        artifacts = [artifact]
        if file:
            _, cap_artifact = add_capture(root, collection, record["source_id"], file); artifacts.append(cap_artifact)
        return Envelope(command="flyvbjerg source add", data=record, artifacts=artifacts)
    emit("flyvbjerg source add", action)


@source_app.command("list")
def source_list(collection: str) -> None:
    emit("flyvbjerg source list", lambda: list_records(discover(), collection, "source"))


@capture_app.command("add")
def capture_add(collection: str, source: str, file: Path, parent: str | None = None) -> None:
    emit("flyvbjerg capture add", lambda: (lambda x: artifact_envelope("flyvbjerg capture add", *x))(add_capture(discover(), collection, source, file, parent)))


@intake_app.command("add")
def intake_add(collection: str, source: str, kind: str, text: str, capture: str | None = None, locator: str | None = None, proposed_name: list[str] | None = typer.Option(None)) -> None:
    def action() -> Envelope:
        record, artifact = add_record(discover(), collection, "item", {"source_id": source, "capture_id": capture, "kind": kind, "text": text, "locator": json_value(locator), "proposed_names": proposed_name or [], "status": "untriaged"})
        return artifact_envelope("flyvbjerg intake add", record, artifact)
    emit("flyvbjerg intake add", action)


@intake_app.command("list")
def intake_list(collection: str, status: str | None = None, kind: str | None = None) -> None:
    def action() -> list[dict[str, Any]]:
        items = effective_intake(collection_root(discover(), collection))
        return [x for x in items if (not status or x.get("status") == status) and (not kind or x.get("kind") == kind)]
    emit("flyvbjerg intake list", action)


@intake_app.command("defer")
def intake_defer(collection: str, item: str, reason: str = typer.Option(...)) -> None:
    def action() -> Envelope:
        root = discover(); get_record(root, collection, "item", item)
        record, artifact = add_record(root, collection, "resolution", {"item_id": item, "resolution_kind": "deferred", "reason": reason})
        return artifact_envelope("flyvbjerg intake defer", record, artifact)
    emit("flyvbjerg intake defer", action)


@intake_app.command("resolve-case")
def intake_resolve_case(collection: str, item: str, case: str | None = None, new_case: str | None = None, name: str | None = None) -> None:
    def action() -> Envelope:
        root = discover(); get_record(root, collection, "item", item)
        case_id = case or new_case
        if not case_id or (case and new_case): raise ValidationError("Choose exactly one of --case or --new-case")
        if new_case:
            add_case(root, collection, {"case_id": new_case, "name": name or new_case})
        else:
            get_case(root, collection, case_id)
        record, artifact = add_record(root, collection, "resolution", {"item_id": item, "resolution_kind": "case", "case_id": case_id})
        return artifact_envelope("flyvbjerg intake resolve-case", record, artifact)
    emit("flyvbjerg intake resolve-case", action)


@intake_app.command("resolve-event")
def intake_resolve_event(collection: str, item: str, type: str = typer.Option(...), case: list[str] = typer.Option(...), date: str | None = None, date_precision: str | None = None) -> None:
    def action() -> Envelope:
        root = discover(); intake = get_record(root, collection, "item", item)
        event, _ = add_record(root, collection, "event", {"type": type, "case_ids": case, "date": date, "date_precision": date_precision, "source_id": intake["source_id"], "item_ids": [item]})
        record, artifact = add_record(root, collection, "resolution", {"item_id": item, "resolution_kind": "event", "event_id": event["event_id"]})
        return artifact_envelope("flyvbjerg intake resolve-event", record, artifact)
    emit("flyvbjerg intake resolve-event", action)


@intake_app.command("resolve-relationship")
def intake_resolve_relationship(collection: str, item: str, from_case: str = typer.Option(..., "--from"), type: str = typer.Option(...), to_case: str = typer.Option(..., "--to")) -> None:
    def action() -> Envelope:
        root = discover(); intake = get_record(root, collection, "item", item)
        get_case(root, collection, from_case); get_case(root, collection, to_case)
        relationship, relationship_artifact = add_record(root, collection, "relationship", {"from_case": from_case, "type": type, "to_case": to_case, "source_id": intake["source_id"], "item_id": item})
        record, resolution_artifact = add_record(root, collection, "resolution", {"item_id": item, "resolution_kind": "relationship", "relationship_id": relationship["relationship_id"]})
        return Envelope(command="flyvbjerg intake resolve-relationship", data=record, artifacts=[relationship_artifact, resolution_artifact])
    emit("flyvbjerg intake resolve-relationship", action)


@intake_app.command("resolve-claim")
def intake_resolve_claim(collection: str, item: str, scope_kind: str = typer.Option(...), scope: list[str] = typer.Option(...), claim_kind: str = typer.Option(...), value: str | None = None, unit: str | None = None, construct: str | None = None) -> None:
    def action() -> Envelope:
        root = discover(); intake = get_record(root, collection, "item", item)
        claim, claim_artifact = add_record(root, collection, "claim", {"scope_kind": scope_kind, "scope_ids": scope, "claim_kind": claim_kind, "source_id": intake["source_id"], "value": json_value(value), "unit": unit, "construct": construct, "status": "candidate", "item_ids": [item]})
        record, resolution_artifact = add_record(root, collection, "resolution", {"item_id": item, "resolution_kind": "claim", "claim_id": claim["claim_id"]})
        return Envelope(command="flyvbjerg intake resolve-claim", data=record, artifacts=[claim_artifact, resolution_artifact])
    emit("flyvbjerg intake resolve-claim", action)


@case_app.command("add")
def case_add(collection: str, case_id: str = typer.Option(..., "--id"), name: str = typer.Option(...), type: str | None = None, from_file: Path | None = typer.Option(None, "--from")) -> None:
    def action() -> Envelope:
        record, artifact = add_case(discover(), collection, payload(from_file, {"case_id": case_id, "name": name, "entity_type": type}))
        return artifact_envelope("flyvbjerg case add", record, artifact)
    emit("flyvbjerg case add", action)


@case_app.command("show")
def case_show(collection: str, case_id: str) -> None:
    emit("flyvbjerg case show", lambda: get_case(discover(), collection, case_id, compose=True))


@case_app.command("list")
def case_list(collection: str) -> None:
    emit("flyvbjerg case list", lambda: records(collection_root(discover(), collection) / "cases", "*/case.json"))


@case_app.command("update")
def case_update(collection: str, case_id: str, from_file: Path = typer.Option(..., "--from"), source: list[str] | None = typer.Option(None)) -> None:
    def action() -> Envelope:
        root = discover(); current = get_case(root, collection, case_id); changes = read_input(from_file)
        if changes.get("case_id", case_id) != case_id: raise ValidationError("An update cannot change case_id")
        source_ids = list(dict.fromkeys([*current.get("source_ids", []), *(source or [])]))
        for source_id in source or []: get_record(root, collection, "source", source_id)
        record = {**current, **changes, "case_id": case_id, "source_ids": source_ids, "updated_at": now()}
        artifact = atomic_write(collection_root(root, collection) / "cases" / case_id / "case.json", record, replace=True)
        return artifact_envelope("flyvbjerg case update", record, artifact)
    emit("flyvbjerg case update", action)


@event_app.command("add")
def event_add(collection: str, type: str = typer.Option(...), case: list[str] = typer.Option(...), source: str = typer.Option(...), date: str | None = None, date_precision: str | None = None, workstream: str | None = None, item: list[str] | None = typer.Option(None), change: str | None = None) -> None:
    def action() -> Envelope:
        record, artifact = add_record(discover(), collection, "event", {"type": type, "case_ids": case, "source_id": source, "date": date, "date_precision": date_precision, "workstream": workstream, "item_ids": item or [], "change": json_value(change)})
        return artifact_envelope("flyvbjerg event add", record, artifact)
    emit("flyvbjerg event add", action)


@event_app.command("list")
def event_list(collection: str, case: str | None = None, type: str | None = None, workstream: str | None = None) -> None:
    emit("flyvbjerg event list", lambda: [x for x in list_records(discover(), collection, "event") if (not case or case in x.get("case_ids", [])) and (not type or x.get("type") == type) and (not workstream or x.get("workstream") == workstream)])


@relationship_app.command("add")
def relationship_add(collection: str, from_case: str = typer.Option(..., "--from"), type: str = typer.Option(...), to_case: str = typer.Option(..., "--to"), source: str = typer.Option(...), item: str | None = None) -> None:
    def action() -> Envelope:
        record, artifact = add_record(discover(), collection, "relationship", {"from_case": from_case, "type": type, "to_case": to_case, "source_id": source, "item_id": item})
        return artifact_envelope("flyvbjerg relationship add", record, artifact)
    emit("flyvbjerg relationship add", action)


@group_app.command("create")
def group_create(collection: str, group_id: str, kind: str = typer.Option(...), name: str = typer.Option(...), member: list[str] | None = typer.Option(None), dependence_reason: str | None = None) -> None:
    def action() -> Envelope:
        record, artifact = add_record(discover(), collection, "group", {"group_id": group_id, "kind": kind, "name": name, "members": member or [], "dependence_reason": dependence_reason})
        return artifact_envelope("flyvbjerg group create", record, artifact)
    emit("flyvbjerg group create", action)


@claim_app.command("add")
def claim_add(collection: str, scope_kind: str = typer.Option(...), scope: list[str] = typer.Option(...), claim_kind: str = typer.Option(...), source: str = typer.Option(...), value: str | None = None, unit: str | None = None, construct: str | None = None, causal_strength: str | None = None) -> None:
    def action() -> Envelope:
        record, artifact = add_record(discover(), collection, "claim", {"scope_kind": scope_kind, "scope_ids": scope, "claim_kind": claim_kind, "source_id": source, "value": json_value(value), "unit": unit, "construct": construct, "causal_strength": causal_strength, "status": "candidate"})
        return artifact_envelope("flyvbjerg claim add", record, artifact)
    emit("flyvbjerg claim add", action)


@claim_app.command("decide")
def claim_decide(collection: str, claim_id: str, accept: bool = False, reject: bool = False, reason: str = typer.Option(...)) -> None:
    def action() -> Envelope:
        if accept == reject: raise ValidationError("Choose exactly one of --accept or --reject")
        root = discover(); get_record(root, collection, "claim", claim_id)
        record, artifact = add_decision(root, collection, "claim", claim_id, "accepted" if accept else "rejected", reason)
        return artifact_envelope("flyvbjerg claim decide", record, artifact)
    emit("flyvbjerg claim decide", action)


@claim_app.command("show")
def claim_show(collection: str, claim_id: str) -> None:
    def action() -> dict[str, Any]:
        root = discover()
        return with_decisions(root, collection, "claim", get_record(root, collection, "claim", claim_id))
    emit("flyvbjerg claim show", action)


@claim_app.command("list")
def claim_list(collection: str, status: str | None = None, claim_kind: str | None = None) -> None:
    def action() -> list[dict[str, Any]]:
        root = discover(); claims = [with_decisions(root, collection, "claim", x) for x in list_records(root, collection, "claim")]
        return [x for x in claims if (not status or x.get("effective_status") == status) and (not claim_kind or x.get("claim_kind") == claim_kind)]
    emit("flyvbjerg claim list", action)


@claim_app.command("promote")
def claim_promote(collection: str, claim_id: str, metric_id: str = typer.Option(..., "--metric"), metric_version: int | None = None) -> None:
    def action() -> Envelope:
        root = discover(); claim = get_record(root, collection, "claim", claim_id); definition = metric(root, collection, metric_id, metric_version)
        allowed = definition.get("subject_kinds", ["case"])
        scope_kind = claim.get("scope_kind")
        if scope_kind not in allowed: raise ValidationError(f"Claim scope {scope_kind} is incompatible with metric subject kinds {allowed}")
        if claim.get("claim_kind") == "management_attribution" and definition.get("role") == "causal_effect" and "management_attribution" not in definition.get("eligible_claim_kinds", []):
            raise ValidationError("Management attribution cannot promote to this causal-effect metric")
        if len(claim.get("scope_ids", [])) != 1: raise ValidationError("Promotion requires exactly one subject; preserve multi-subject claims as claims")
        if claim.get("value") is None: raise ValidationError("Claim has no promotable value")
        record, artifact = add_record(root, collection, "observation", {"subject": {"kind": scope_kind, "id": claim["scope_ids"][0]}, "metric": {"id": metric_id, "version": definition["version"]}, "value": claim["value"], "unit": claim.get("unit"), "method": "reported", "status": "candidate", "provenance": {"kind": "claim", "id": claim_id}})
        return artifact_envelope("flyvbjerg claim promote", record, artifact)
    emit("flyvbjerg claim promote", action)


@metric_app.command("add")
def metric_add(collection: str, metric_id: str, kind: str = typer.Option(...), role: str = typer.Option(...), unit: str | None = None, label: str | None = None, definition: str | None = None, zero_policy: str | None = None, subject_kind: list[str] | None = typer.Option(None, "--subject-kind"), from_file: Path | None = typer.Option(None, "--from")) -> None:
    def action() -> Envelope:
        record, artifact = add_metric(discover(), collection, payload(from_file, {"metric_id": metric_id, "kind": kind, "role": role, "unit": unit, "label": label, "definition": definition, "zero_policy": zero_policy, "subject_kinds": subject_kind}))
        return artifact_envelope("flyvbjerg metric add", record, artifact)
    emit("flyvbjerg metric add", action)


@metric_app.command("show")
def metric_show(collection: str, metric_id: str, version: int | None = None) -> None:
    emit("flyvbjerg metric show", lambda: metric(discover(), collection, metric_id, version))


@metric_app.command("derive")
def metric_derive(collection: str, metric_id: str, metric_version: int | None = None, subject: list[str] | None = typer.Option(None), dry_run: bool = False) -> None:
    emit("flyvbjerg metric derive", lambda: derive_metric(discover(), collection, metric_id, metric_version, subject, dry_run))


@observation_app.command("add")
def observation_add(collection: str, subject_kind: str = typer.Option(...), subject: str = typer.Option(...), metric_id: str = typer.Option(..., "--metric"), value: str = typer.Option(...), source: str | None = None, period: str | None = None, method: str = "reported") -> None:
    def action() -> Envelope:
        definition = metric(discover(), collection, metric_id)
        record, artifact = add_record(discover(), collection, "observation", {"subject": {"kind": subject_kind.lower(), "id": subject}, "metric": {"id": metric_id, "version": definition["version"]}, "value": json_value(value), "source_id": source, "period": period, "method": method, "status": "candidate"})
        return artifact_envelope("flyvbjerg observation add", record, artifact)
    emit("flyvbjerg observation add", action)


@observation_app.command("decide")
def observation_decide(collection: str, observation_id: str, accept: bool = False, reject: bool = False, reason: str = typer.Option(...)) -> None:
    def action() -> Envelope:
        if accept == reject: raise ValidationError("Choose exactly one of --accept or --reject")
        get_record(discover(), collection, "observation", observation_id)
        record, artifact = add_decision(discover(), collection, "observation", observation_id, "accepted" if accept else "rejected", reason)
        return artifact_envelope("flyvbjerg observation decide", record, artifact)
    emit("flyvbjerg observation decide", action)


@coverage_app.command("set")
def coverage_set(collection: str, subject_kind: str = typer.Option(...), subject: str = typer.Option(...), metric_id: str = typer.Option(..., "--metric"), state: str = typer.Option(...), reason: str = typer.Option(...)) -> None:
    def action() -> Envelope:
        record, artifact = add_record(discover(), collection, "coverage", {"subject": {"kind": subject_kind, "id": subject}, "metric_id": metric_id, "state": state, "reason": reason})
        return artifact_envelope("flyvbjerg coverage set", record, artifact)
    emit("flyvbjerg coverage set", action)


@analysis_app.command("create")
def analysis_create(collection: str, name: str = typer.Option(...), metric_id: str = typer.Option(..., "--metric"), target: str | None = None, target_version: int | None = None, cluster_group: list[str] | None = typer.Option(None)) -> None:
    def action() -> Envelope:
        record, warnings = create_analysis(discover(), collection, name, metric_id, target, target_version, cluster_group)
        return Envelope(command="flyvbjerg analysis create", data=record, warnings=warnings)
    emit("flyvbjerg analysis create", action)


@analysis_app.command("show")
def analysis_show(analysis_id: str) -> None:
    emit("flyvbjerg analysis show", lambda: load_analysis(discover(), analysis_id))


@comparison_app.command("create")
def comparison_create(collection: str, name: str = typer.Option(...), analysis_id: list[str] = typer.Option(..., "--analysis")) -> None:
    def action() -> Envelope:
        record, artifact = create_comparison(discover(), collection, name, analysis_id)
        return artifact_envelope("flyvbjerg comparison create", record, artifact)
    emit("flyvbjerg comparison create", action)


@comparison_app.command("show")
def comparison_show(comparison_id: str) -> None:
    emit("flyvbjerg comparison show", lambda: load_comparison(discover(), comparison_id))


@comparison_app.command("threshold")
def comparison_threshold(comparison_id: str, operator: str = typer.Option(...), value: list[float] = typer.Option(...)) -> None:
    def action() -> Envelope:
        record, artifact = threshold_comparison(discover(), comparison_id, operator, value)
        return artifact_envelope("flyvbjerg comparison threshold", record, artifact)
    emit("flyvbjerg comparison threshold", action)


@comparison_app.command("plot")
def comparison_plot(comparison_id: str, output: Path = typer.Option(...)) -> None:
    def action() -> Envelope:
        receipt, artifacts = create_comparison_plot(discover(), comparison_id, output)
        return Envelope(command="flyvbjerg comparison plot", data=receipt, artifacts=artifacts)
    emit("flyvbjerg comparison plot", action)


@app.command("rate")
def rate(analysis_id: str) -> None:
    emit("flyvbjerg rate", lambda: load_analysis(discover(), analysis_id)["distribution"])


@app.command("threshold")
def threshold(analysis_id: str, operator: str = typer.Option(...), value: float = typer.Option(...)) -> None:
    emit("flyvbjerg threshold", lambda: threshold_analysis(discover(), analysis_id, operator, value))


@app.command("locate")
def locate(analysis_id: str, value: float = typer.Option(...), label: str | None = None) -> None:
    emit("flyvbjerg locate", lambda: locate_value(discover(), analysis_id, value, label))


@app.command("plot")
def plot(analysis_id: str, kind: str = typer.Option(...), output: Path = typer.Option(...), target_value: float | None = None, threshold: float | None = None) -> None:
    def action() -> Envelope:
        receipt, artifacts = create_plot(discover(), analysis_id, kind, output, target_value, threshold)
        return Envelope(command="flyvbjerg plot", data=receipt, artifacts=artifacts)
    emit("flyvbjerg plot", action)


@sensitivity_app.command("cluster")
def sensitivity_cluster(analysis_id: str) -> None:
    emit("flyvbjerg sensitivity cluster", lambda: cluster_sensitivity(discover(), analysis_id))


@process_app.command("plan")
def process_plan(collection: str, name: str = typer.Option(...), mode: str = typer.Option(...), capture: list[str] = typer.Option(...), task: str = "") -> None:
    def action() -> Envelope:
        record, artifact = create_plan(discover(), collection, name, mode, capture, task)
        return artifact_envelope("flyvbjerg process plan", record, artifact)
    emit("flyvbjerg process plan", action)


@process_app.command("show")
def process_show(run_id: str) -> None:
    emit("flyvbjerg process show", lambda: find_run(discover(), run_id)[1])


@process_app.command("approve")
def process_approve(run_id: str) -> None:
    def action() -> Envelope:
        record, artifact = approve_plan(discover(), run_id)
        return artifact_envelope("flyvbjerg process approve", record, artifact)
    emit("flyvbjerg process approve", action)


@process_app.command("build")
def process_build(run_id: str) -> None:
    def action() -> Envelope:
        record, artifacts = build_plan(discover(), run_id)
        return Envelope(command="flyvbjerg process build", data=record, artifacts=artifacts, next_steps=[{"id": "inspect_jobs", "purpose": "Inspect the native Jobs package", "command": f"ep inspect {record['jobs_path']}", "mutates_state": False, "requires_network": False, "requires_user_approval": False}, {"id": "estimate_cost", "purpose": "Estimate model cost before requesting execution authority", "command": f"ep jobs cost {record['jobs_path']}", "mutates_state": False, "requires_network": False, "requires_user_approval": False}])
    emit("flyvbjerg process build", action)


@process_app.command("register-results")
def process_register_results(run_id: str, input: Path = typer.Option(...)) -> None:
    def action() -> Envelope:
        record, artifact = register_results(discover(), run_id, input)
        return artifact_envelope("flyvbjerg process register-results", record, artifact)
    emit("flyvbjerg process register-results", action)


@process_app.command("audit")
def process_audit(run_id: str, result_set: str = typer.Option(...)) -> None:
    def action() -> Envelope:
        record, artifact = audit_run(discover(), run_id, result_set)
        warnings = [] if record["complete"] else ["Results are incomplete or malformed and must not be treated as negative findings."]
        return artifact_envelope("flyvbjerg process audit", record, artifact, warnings=warnings)
    emit("flyvbjerg process audit", action)


@app.command("validate")
def validate() -> None:
    def action() -> dict[str, Any]:
        root = discover(); errors = []
        for path in root.rglob("*.json"):
            try: read_json(path)
            except FlyvbjergError as exc: errors.append({"path": str(path), "message": exc.message})
        if errors: raise ValidationError(f"Workspace has {len(errors)} invalid JSON records")
        return {"valid": True, "json_records": len(list(root.rglob("*.json")))}
    emit("flyvbjerg validate", action)


def main() -> None:
    """Run the CLI while preserving JSON envelopes for parser-level failures."""
    command = get_command(app)
    try:
        command.main(prog_name="flyvbjerg", standalone_mode=False)
    except ClickUsageError as exc:
        envelope = Envelope(command="flyvbjerg", status="error", errors=[{"code": "USAGE_ERROR", "message": exc.format_message(), "hint": "Run `flyvbjerg --help` or the command's `--help`."}])
        typer.echo(json.dumps(envelope.to_dict(), ensure_ascii=False))
        raise SystemExit(1) from None
    except ClickExit as exc:
        raise SystemExit(exc.exit_code) from None


if __name__ == "__main__":
    main()
