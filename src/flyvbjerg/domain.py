from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .errors import NotFound, ValidationError
from .workspace import atomic_write, collection_root, new_id, now, read_json, records, sha256_bytes


KIND_PATHS = {
    "source": ("intake/sources", "source_id", "src"),
    "item": ("intake/items", "item_id", "item"),
    "resolution": ("intake/resolutions", "resolution_id", "res"),
    "claim": ("claims", "claim_id", "claim"),
    "event": ("events", "event_id", "event"),
    "relationship": ("relationships", "relationship_id", "rel"),
    "group": ("groups", "group_id", "group"),
    "observation": ("observations", "observation_id", "obs"),
    "coverage": ("coverage", "coverage_id", "cov"),
}


def add_record(root: Path, collection: str, kind: str, value: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    base = collection_root(root, collection)
    relative, id_field, prefix = KIND_PATHS[kind]
    record_id = value.get(id_field) or new_id(prefix)
    record = {**value, id_field: record_id, "created_at": value.get("created_at", now())}
    artifact = atomic_write(base / relative / f"{record_id}.json", record)
    return record, artifact


def list_records(root: Path, collection: str, kind: str) -> list[dict[str, Any]]:
    relative, _, _ = KIND_PATHS[kind]
    return records(collection_root(root, collection) / relative)


def get_record(root: Path, collection: str, kind: str, record_id: str) -> dict[str, Any]:
    relative, _, _ = KIND_PATHS[kind]
    return read_json(collection_root(root, collection) / relative / f"{record_id}.json")


def add_case(root: Path, collection: str, value: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    case_id = value.get("case_id") or value.get("id")
    if not case_id:
        raise ValidationError("A case_id is required")
    record = {**value, "case_id": case_id, "created_at": value.get("created_at", now())}
    path = collection_root(root, collection) / "cases" / case_id / "case.json"
    artifact = atomic_write(path, record)
    for directory in ("materials", "relationships", "observations", "decisions"):
        (path.parent / directory).mkdir(exist_ok=True)
    return record, artifact


def get_case(root: Path, collection: str, case_id: str, *, compose: bool = False) -> dict[str, Any]:
    base = collection_root(root, collection)
    case = read_json(base / "cases" / case_id / "case.json")
    if not compose:
        return case
    return {
        **case,
        "events": [x for x in records(base / "events") if case_id in x.get("case_ids", [])],
        "relationships": [x for x in records(base / "relationships") if case_id in (x.get("from_case"), x.get("to_case"))],
        "groups": [x for x in records(base / "groups") if case_id in x.get("members", [])],
        "claims": [x for x in records(base / "claims") if case_id in x.get("scope_ids", [])],
        "observations": [x for x in records(base / "observations") if x.get("subject", {}).get("id") == case_id],
        "coverage": [x for x in records(base / "coverage") if x.get("subject", {}).get("id") == case_id],
    }


def add_capture(root: Path, collection: str, source_id: str, source_file: Path, parent: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    get_record(root, collection, "source", source_id)
    capture_id = new_id("cap")
    base = collection_root(root, collection) / "intake" / "captures" / capture_id
    base.mkdir(parents=True)
    destination = base / source_file.name
    shutil.copy2(source_file, destination)
    digest = sha256_bytes(destination.read_bytes())
    record = {"capture_id": capture_id, "source_id": source_id, "parent_capture_id": parent, "file": source_file.name, "sha256": digest, "created_at": now()}
    artifact = atomic_write(base / "capture.json", record)
    return record, artifact


def load_capture(root: Path, collection: str, capture_id: str) -> dict[str, Any]:
    return read_json(collection_root(root, collection) / "intake" / "captures" / capture_id / "capture.json")


def add_decision(root: Path, collection: str, subject_kind: str, subject_id: str, decision: str, reason: str) -> tuple[dict[str, Any], dict[str, Any]]:
    decision_id = new_id("dec")
    record = {"decision_id": decision_id, "subject_kind": subject_kind, "subject_id": subject_id, "decision": decision, "reason": reason, "created_at": now()}
    path = collection_root(root, collection) / "decisions" / f"{decision_id}.json"
    return record, atomic_write(path, record)

