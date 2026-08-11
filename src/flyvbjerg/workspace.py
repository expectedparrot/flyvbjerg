from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .errors import Conflict, NotFound, ValidationError

ROOT_NAME = ".flyvbjerg"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise NotFound(f"Record not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"Expected a JSON object in {path}")
    return value


def read_input(path: Path) -> dict[str, Any]:
    return read_json(path.resolve())


def atomic_write(path: Path, value: Any, *, replace: bool = False) -> dict[str, Any]:
    if path.exists() and not replace:
        raise Conflict(f"Record already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_bytes(value)
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(raw_tmp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
    return {"path": str(path), "media_type": "application/json", "sha256": sha256_bytes(payload)}


def discover(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        root = candidate / ROOT_NAME
        if (root / "workspace.json").is_file():
            return root
    raise NotFound("No Flyvbjerg workspace found", "Run `flyvbjerg init [PATH]` first.")


def initialize(path: Path) -> tuple[Path, dict[str, Any]]:
    base = path.resolve()
    root = base / ROOT_NAME
    root.mkdir(parents=True, exist_ok=True)
    record = {
        "schema_version": "1.0",
        "workspace_id": new_id("ws"),
        "created_at": now(),
        "format": "flyvbjerg-workspace",
    }
    artifact = atomic_write(root / "workspace.json", record)
    for name in ("targets", "collections", "schemas", "receipts"):
        (root / name).mkdir(exist_ok=True)
    return root, artifact


def collection_root(root: Path, collection: str, *, require: bool = True) -> Path:
    path = root / "collections" / collection
    if require and not (path / "collection.json").is_file():
        raise NotFound(f"Collection not found: {collection}")
    return path


def records(path: Path, pattern: str = "*.json") -> list[dict[str, Any]]:
    return [read_json(item) for item in sorted(path.glob(pattern)) if item.is_file()]


def json_value(raw: str | None, default: Any = None) -> Any:
    if raw is None:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON value: {exc}") from exc


def require_fields(value: dict[str, Any], fields: Iterable[str]) -> None:
    missing = [field for field in fields if value.get(field) in (None, "", [])]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")


def versioned_write(directory: Path, value: dict[str, Any], *, id_field: str) -> tuple[dict[str, Any], dict[str, Any]]:
    versions = sorted(directory.glob("v*.json")) if directory.exists() else []
    version = len(versions) + 1
    record = {**value, "version": version, "created_at": now()}
    require_fields(record, [id_field])
    artifact = atomic_write(directory / f"v{version}.json", record)
    return record, artifact


def load_version(directory: Path, version: int | None = None) -> dict[str, Any]:
    if version is not None:
        return read_json(directory / f"v{version}.json")
    versions = sorted(directory.glob("v*.json"), key=lambda p: int(p.stem[1:]))
    if not versions:
        raise NotFound(f"No versions found: {directory}")
    return read_json(versions[-1])

