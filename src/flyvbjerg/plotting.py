from __future__ import annotations

import html
import os
import tempfile
from pathlib import Path
from typing import Any

from .analysis import load_analysis
from .errors import ValidationError
from .workspace import atomic_write, collection_root, now, records, sha256_bytes


def _subject_values(root: Path, analysis: dict[str, Any]) -> list[tuple[str, float, str]]:
    base = collection_root(root, analysis["collection_id"])
    observations = {item["observation_id"]: item for item in records(base / "observations")}
    case_names = {item["case_id"]: item.get("name", item["case_id"]) for item in records(base / "cases", "*/case.json")}
    values = []
    for observation_id in analysis["observation_ids"]:
        observation = observations[observation_id]
        value = observation.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            subject = observation["subject"]["id"]
            values.append((subject, float(value), case_names.get(subject, subject)))
    if not values:
        raise ValidationError("Analysis has no numeric observations to plot")
    return sorted(values, key=lambda item: (item[1], item[0]))


def _atomic_text(path: Path, text: str) -> dict[str, Any]:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = text.encode("utf-8")
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
    return {"path": str(path), "media_type": "image/svg+xml", "sha256": sha256_bytes(payload)}


def _scale(value: float, low: float, high: float, start: float, end: float) -> float:
    if high == low:
        return (start + end) / 2
    return start + (value - low) * (end - start) / (high - low)


def _footer(analysis: dict[str, Any], missing: int) -> str:
    dependence = analysis.get("dependence_status", "not_assessed").replace("_", " ")
    convention = analysis["distribution"].get("quantile_convention", "unspecified")
    return f"n={analysis['n_subjects']} · missing={missing} · dependence: {dependence} · quantiles: {convention} · {analysis['analysis_id']}"


def _ecdf_svg(analysis: dict[str, Any], values: list[tuple[str, float, str]], target: float | None, threshold: float | None) -> str:
    width, height = 900, 540
    left, right, top, bottom = 85, 845, 70, 430
    numeric = [value for _, value, _ in values]
    markers = [x for x in (target, threshold) if x is not None]
    low, high = min([*numeric, *markers]), max([*numeric, *markers])
    span = high - low or 1
    low -= span * 0.05; high += span * 0.05
    points = [(left, bottom)]
    for index, (_, value, _) in enumerate(values, 1):
        x = _scale(value, low, high, left, right)
        y = bottom - index / len(values) * (bottom - top)
        points.extend([(x, points[-1][1]), (x, y)])
    points.append((right, points[-1][1]))
    path = " ".join(("M" if i == 0 else "L") + f" {x:.1f} {y:.1f}" for i, (x, y) in enumerate(points))
    layers = [f'<path d="{path}" fill="none" stroke="#1f5b49" stroke-width="3"/>']
    marker_specs = [("target / threshold", target, "#c24d2c")] if target is not None and target == threshold else [("target", target, "#c24d2c"), ("threshold", threshold, "#7357a6")]
    for label, marker, color in marker_specs:
        if marker is not None:
            x = _scale(marker, low, high, left, right)
            layers.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="{color}" stroke-width="2" stroke-dasharray="7 5"/>')
            layers.append(f'<text x="{x + 6:.1f}" y="{top + 18}" fill="{color}" font-size="14">{label}: {marker:g}</text>')
    ticks = []
    for index in range(6):
        fraction = index / 5
        x = left + fraction * (right - left); value = low + fraction * (high - low)
        ticks.append(f'<line x1="{x:.1f}" y1="{bottom}" x2="{x:.1f}" y2="{bottom + 6}" stroke="#34413b"/><text x="{x:.1f}" y="{bottom + 25}" text-anchor="middle" font-size="13">{value:.0f}</text>')
        y = bottom - fraction * (bottom - top)
        ticks.append(f'<line x1="{left - 6}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="#34413b"/><text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" font-size="13">{fraction:.1f}</text>')
    missing = len(set(analysis["subject_ids"]) - {subject for subject, _, _ in values})
    return _svg_shell(width, height, "Empirical cumulative distribution", analysis, layers + ticks, _footer(analysis, missing))


def _ordered_svg(analysis: dict[str, Any], values: list[tuple[str, float, str]], target: float | None, threshold: float | None) -> str:
    width = 1000; row = 34; top = 85; bottom = top + row * len(values); height = bottom + 95
    left, right = 250, 940
    numeric = [value for _, value, _ in values]; markers = [x for x in (target, threshold) if x is not None]
    low, high = min([*numeric, *markers]), max([*numeric, *markers]); span = high - low or 1
    low -= span * 0.05; high += span * 0.05
    layers = []
    for index, (subject, value, label) in enumerate(values):
        y = top + index * row
        x = _scale(value, low, high, left, right)
        layers.append(f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" stroke="#e3e8e5"/>')
        layers.append(f'<text x="{left - 12}" y="{y + 5}" text-anchor="end" font-size="14">{html.escape(label)}</text>')
        layers.append(f'<circle cx="{x:.1f}" cy="{y}" r="6" fill="#1f5b49"/><text x="{x + 10:.1f}" y="{y + 5}" font-size="13">{value:g}</text>')
    marker_specs = [("target / threshold", target, "#c24d2c")] if target is not None and target == threshold else [("target", target, "#c24d2c"), ("threshold", threshold, "#7357a6")]
    for label, marker, color in marker_specs:
        if marker is not None:
            x = _scale(marker, low, high, left, right)
            layers.append(f'<line x1="{x:.1f}" y1="{top - 25}" x2="{x:.1f}" y2="{bottom - row + 12}" stroke="{color}" stroke-width="2" stroke-dasharray="7 5"/>')
            layers.append(f'<text x="{x + 6:.1f}" y="{top - 32}" fill="{color}" font-size="14">{label}: {marker:g}</text>')
    missing = len(set(analysis["subject_ids"]) - {subject for subject, _, _ in values})
    return _svg_shell(width, height, "Ordered observations", analysis, layers, _footer(analysis, missing))


def _svg_shell(width: int, height: int, heading: str, analysis: dict[str, Any], layers: list[str], footer: str) -> str:
    metric = analysis["metric"]
    title = f"{heading}: {analysis['name']}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">Audited reference-class plot for {html.escape(analysis['analysis_id'])}</desc>
<rect width="100%" height="100%" fill="#fff"/><g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" fill="#202522">
<text x="40" y="36" font-size="22" font-weight="600">{html.escape(title)}</text>
<text x="40" y="58" font-size="14" fill="#5f6963">metric: {html.escape(metric['id'])} v{metric['version']}</text>
{''.join(layers)}
<text x="40" y="{height - 25}" font-size="12" fill="#5f6963">{html.escape(footer)}</text></g></svg>'''


def create_plot(root: Path, analysis_id: str, kind: str, output: Path, target_value: float | None = None, threshold: float | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    analysis = load_analysis(root, analysis_id)
    values = _subject_values(root, analysis)
    renderers = {"ecdf": _ecdf_svg, "ordered": _ordered_svg}
    if kind not in renderers:
        raise ValidationError("Unsupported plot kind; choose ecdf or ordered")
    output = output.resolve()
    svg = renderers[kind](analysis, values, target_value, threshold)
    image_artifact = _atomic_text(output, svg)
    receipt = {"kind": kind, "analysis_id": analysis_id, "target_value": target_value, "threshold": threshold, "output": str(output), "data_sha256": image_artifact["sha256"], "created_at": now()}
    receipt_path = output.with_suffix(".plot.json")
    receipt_artifact = atomic_write(receipt_path, receipt, replace=True)
    return receipt, [image_artifact, receipt_artifact]
