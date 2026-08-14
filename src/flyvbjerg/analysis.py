from __future__ import annotations

import statistics
import math
from datetime import date
from pathlib import Path
from typing import Any

from .domain import add_record, list_records
from .errors import NotFound, ValidationError
from .workspace import atomic_write, collection_root, load_version, new_id, now, read_json, records


def metric(root: Path, collection: str, metric_id: str, version: int | None = None) -> dict[str, Any]:
    return load_version(collection_root(root, collection) / "metrics" / metric_id, version)


def add_metric(root: Path, collection: str, value: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    metric_id = value.get("metric_id")
    if not metric_id:
        raise ValidationError("metric_id is required")
    directory = collection_root(root, collection) / "metrics" / metric_id
    version = len(list(directory.glob("v*.json"))) + 1
    record = {**value, "metric_id": metric_id, "version": version, "created_at": now()}
    return record, atomic_write(directory / f"v{version}.json", record)


def _parse_day(value: str, event_id: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Event {event_id} lacks a day-precision ISO date") from exc


def derive_metric(root: Path, collection: str, metric_id: str, version: int | None = None, subjects: list[str] | None = None, dry_run: bool = False) -> dict[str, Any]:
    definition = metric(root, collection, metric_id, version)
    derivation = definition.get("derivation", {})
    if derivation.get("kind") != "event_interval":
        raise ValidationError("Only event_interval derivations are supported in v0.1")
    events = list_records(root, collection, "event")
    if subjects is None:
        subjects = sorted({case_id for event in events for case_id in event.get("case_ids", [])})
    created: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for subject in subjects:
        starts = [event for event in events if subject in event.get("case_ids", []) and event.get("type") == derivation.get("start_event_type")]
        end_types = derivation.get("end_event_types") or [derivation.get("end_event_type")]
        end_types = [item for item in end_types if item]
        ends = [event for event in events if subject in event.get("case_ids", []) and event.get("type") in end_types]
        if len(starts) != 1 or not ends:
            gaps.append({"subject_id": subject, "code": "AMBIGUOUS_OR_MISSING_ENDPOINT", "start_count": len(starts), "end_count": len(ends)})
            continue
        if derivation.get("selection") == "first_terminal_event":
            try:
                start_day = _parse_day(starts[0].get("date"), starts[0]["event_id"])
                eligible_ends = sorted(
                    (event for event in ends if _parse_day(event.get("date"), event["event_id"]) >= start_day),
                    key=lambda event: _parse_day(event.get("date"), event["event_id"]),
                )
            except ValidationError as exc:
                gaps.append({"subject_id": subject, "code": "INSUFFICIENT_DATE_PRECISION", "message": exc.message})
                continue
            if not eligible_ends:
                gaps.append({"subject_id": subject, "code": "MISSING_TERMINAL_EVENT_AFTER_START", "start_count": 1, "end_count": len(ends)})
                continue
            ends = [eligible_ends[0]]
        elif len(ends) != 1:
            gaps.append({"subject_id": subject, "code": "AMBIGUOUS_OR_MISSING_ENDPOINT", "start_count": len(starts), "end_count": len(ends)})
            continue
        try:
            value = (_parse_day(ends[0].get("date"), ends[0]["event_id"]) - _parse_day(starts[0].get("date"), starts[0]["event_id"])).days
        except ValidationError as exc:
            gaps.append({"subject_id": subject, "code": "INSUFFICIENT_DATE_PRECISION", "message": exc.message})
            continue
        observation = {
            "subject": {"kind": "case", "id": subject},
            "metric": {"id": metric_id, "version": definition["version"]},
            "value": value,
            "unit": definition.get("unit"),
            "method": "calculated",
            "status": "candidate",
            "input_event_ids": [starts[0]["event_id"], ends[0]["event_id"]],
            "terminal_event_type": ends[0].get("type"),
        }
        if dry_run:
            observation["observation_id"] = None
            created.append(observation)
        else:
            record, _ = add_record(root, collection, "observation", observation)
            created.append(record)
    return {"metric": {"id": metric_id, "version": definition["version"]}, "created": created, "gaps": gaps, "dry_run": dry_run}


def _latest_decisions(base: Path) -> dict[tuple[str, str], str]:
    outcome: dict[tuple[str, str], str] = {}
    for item in records(base / "decisions"):
        outcome[(item.get("subject_kind", ""), item.get("subject_id", ""))] = item.get("decision", "")
    return outcome


def _stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "values": []}
    ordered = sorted(values)
    probabilities = (0.1, 0.25, 0.5, 0.75, 0.9)
    quantiles = {str(probability): ordered[max(0, math.ceil(probability * len(ordered)) - 1)] for probability in probabilities}
    return {"count": len(values), "values": values, "min": min(values), "median": statistics.median(values), "max": max(values), "mean": statistics.fmean(values), "quantiles": quantiles, "quantile_convention": "nearest_rank"}


def create_analysis(root: Path, collection: str, name: str, metric_id: str, target: str | None = None, target_version: int | None = None, clusters: list[str] | None = None) -> tuple[dict[str, Any], list[str]]:
    base = collection_root(root, collection)
    definition = metric(root, collection, metric_id)
    decisions = _latest_decisions(base)
    observations = [
        item for item in list_records(root, collection, "observation")
        if item.get("metric", {}).get("id") == metric_id and item.get("metric", {}).get("version") == definition["version"]
    ]
    accepted = [item for item in observations if item.get("status") == "accepted" or decisions.get(("observation", item["observation_id"])) == "accepted"]
    subject_ids = sorted({item.get("subject", {}).get("id") for item in accepted})
    coverage = [item for item in list_records(root, collection, "coverage") if item.get("metric_id") == metric_id]
    covered = {item.get("subject", {}).get("id") for item in coverage}
    missing_coverage = sorted(set(subject_ids) - covered)
    if missing_coverage:
        raise ValidationError(f"Subjects lack explicit coverage state: {', '.join(missing_coverage)}")
    required = definition.get("required_context", [])
    cases = {case_id: read_json(base / "cases" / case_id / "case.json") for case_id in subject_ids}
    context_gaps = {case_id: [field for field in required if cases[case_id].get("context", {}).get(field) is None] for case_id in subject_ids}
    context_gaps = {key: value for key, value in context_gaps.items() if value}
    policy = definition.get("missing_context_policy", "allow")
    if context_gaps and policy == "error":
        raise ValidationError(f"Required metric context is missing: {context_gaps}")
    warnings: list[str] = []
    if context_gaps and policy == "warn":
        warnings.append(f"Required metric context is missing: {context_gaps}")
    cluster_records = []
    for group_id in clusters or []:
        group = read_json(base / "groups" / f"{group_id}.json")
        members = sorted(set(group.get("members", [])) & set(subject_ids))
        cluster_records.append({"group_id": group_id, "members": members, "reason": group.get("dependence_reason") or group.get("kind")})
    analysis_id = new_id("analysis")
    target_ref = None
    if target:
        target_record = load_version(root / "targets" / target, target_version)
        target_ref = {"id": target, "version": target_record["version"]}
    values = [item["value"] for item in accepted if isinstance(item.get("value"), (int, float)) and not isinstance(item.get("value"), bool)]
    record = {
        "analysis_id": analysis_id,
        "name": name,
        "collection_id": collection,
        "metric": {"id": metric_id, "version": definition["version"]},
        "target": target_ref,
        "subject_ids": subject_ids,
        "observation_ids": [item["observation_id"] for item in accepted],
        "n_subjects": len(subject_ids),
        "dependence_clusters": cluster_records,
        "dependence_status": "assessed_with_clusters" if cluster_records else "not_assessed",
        "n_clusters": len(cluster_records) if cluster_records else None,
        "required_context_gaps": context_gaps,
        "distribution": _stats(values),
        "created_at": now(),
    }
    directory = base / "analysis-sets" / analysis_id
    atomic_write(directory / "analysis.json", record)
    atomic_write(directory / "distribution.json", record["distribution"])
    return record, warnings


def load_analysis(root: Path, analysis_id: str) -> dict[str, Any]:
    matches = list((root / "collections").glob(f"*/analysis-sets/{analysis_id}/analysis.json"))
    if not matches:
        raise NotFound(f"Analysis not found: {analysis_id}")
    return read_json(matches[0])


def cluster_sensitivity(root: Path, analysis_id: str) -> dict[str, Any]:
    analysis = load_analysis(root, analysis_id)
    values = analysis["distribution"].get("values", [])
    if not analysis.get("dependence_clusters"):
        return {"analysis_id": analysis_id, "kind": "leave_one_cluster_out", "results": [], "warning": "No dependence clusters declared"}
    base = collection_root(root, analysis["collection_id"])
    observations = {item["observation_id"]: item for item in records(base / "observations")}
    by_subject = {observations[item]["subject"]["id"]: observations[item]["value"] for item in analysis["observation_ids"]}
    results = []
    all_subjects = set(analysis["subject_ids"])
    for cluster in analysis["dependence_clusters"]:
        remaining = [by_subject[s] for s in sorted(all_subjects - set(cluster["members"])) if s in by_subject]
        results.append({"omitted_group_id": cluster["group_id"], "distribution": _stats(remaining)})
    return {"analysis_id": analysis_id, "kind": "leave_one_cluster_out", "full_values": values, "results": results}


def _analysis_subject_values(root: Path, analysis: dict[str, Any]) -> dict[str, float]:
    base = collection_root(root, analysis["collection_id"])
    observations = {item["observation_id"]: item for item in records(base / "observations")}
    result: dict[str, float] = {}
    for observation_id in analysis["observation_ids"]:
        observation = observations[observation_id]
        value = observation.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            result[observation["subject"]["id"]] = value
    return result


def threshold_analysis(root: Path, analysis_id: str, operator: str, value: float) -> dict[str, Any]:
    operations = {
        "lt": lambda candidate: candidate < value,
        "le": lambda candidate: candidate <= value,
        "eq": lambda candidate: candidate == value,
        "ge": lambda candidate: candidate >= value,
        "gt": lambda candidate: candidate > value,
    }
    if operator not in operations:
        raise ValidationError(f"Unsupported threshold operator: {operator}; choose lt, le, eq, ge, or gt")
    analysis = load_analysis(root, analysis_id)
    by_subject = _analysis_subject_values(root, analysis)
    matching = sorted(subject for subject, candidate in by_subject.items() if operations[operator](candidate))
    nonmatching = sorted(set(by_subject) - set(matching))
    missing = sorted(set(analysis["subject_ids"]) - set(by_subject))
    count = len(by_subject)
    return {
        "analysis_id": analysis_id,
        "threshold": {"operator": operator, "value": value},
        "count_matching": len(matching),
        "count_observed": count,
        "frequency": len(matching) / count if count else None,
        "matching_subject_ids": matching,
        "nonmatching_subject_ids": nonmatching,
        "missing_subject_ids": missing,
        "dependence_status": analysis.get("dependence_status", "not_assessed"),
        "n_clusters": analysis.get("n_clusters"),
    }


def locate_value(root: Path, analysis_id: str, value: float, label: str | None = None) -> dict[str, Any]:
    analysis = load_analysis(root, analysis_id)
    by_subject = _analysis_subject_values(root, analysis)
    values = list(by_subject.values())
    if not values:
        raise ValidationError("Analysis has no numeric observations")
    median = analysis["distribution"]["median"]
    below = sorted(subject for subject, candidate in by_subject.items() if candidate < value)
    equal = sorted(subject for subject, candidate in by_subject.items() if candidate == value)
    above = sorted(subject for subject, candidate in by_subject.items() if candidate > value)
    return {
        "analysis_id": analysis_id,
        "label": label,
        "value": value,
        "empirical_rank": (len(below) + len(equal)) / len(values),
        "empirical_rank_convention": "fraction_less_than_or_equal",
        "reference_median": median,
        "difference_from_median": value - median,
        "ratio_to_median": value / median if median else None,
        "observed_support": {"min": min(values), "max": max(values)},
        "within_observed_support": min(values) <= value <= max(values),
        "subjects_below": below,
        "subjects_equal": equal,
        "subjects_above": above,
        "dependence_status": analysis.get("dependence_status", "not_assessed"),
        "n_clusters": analysis.get("n_clusters"),
    }
