from __future__ import annotations

import html
import os
import tempfile
from pathlib import Path
from typing import Any

from .comparison import load_comparison
from .errors import ValidationError
from .workspace import atomic_write, canonical_bytes, now, sha256_bytes


COLORS = ("#1f5b49", "#c4772d", "#7357a6", "#3478a4", "#a44747")


def _atomic_svg(path: Path, value: str) -> dict[str, Any]:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = value.encode("utf-8")
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


def _summary_svg(comparison: dict[str, Any]) -> str:
    analyses = comparison["analyses"]
    if any(item["distribution"].get("median") is None for item in analyses):
        raise ValidationError("Every compared analysis must have a numeric distribution")
    numeric = []
    for item in analyses:
        distribution = item["distribution"]
        quantiles = distribution.get("quantiles") or {}
        numeric.extend(value for value in (distribution.get("min"), quantiles.get("0.25"), distribution.get("median"), quantiles.get("0.75"), distribution.get("max")) if value is not None)
    raw_low, raw_high = min(numeric), max(numeric)
    span = raw_high - raw_low or 1
    low = max(0, raw_low - span * 0.05) if raw_low >= 0 else raw_low - span * 0.05
    high = raw_high + span * 0.05
    width, left, right, top, row = 1000, 290, 940, 110, 78
    height = top + row * len(analyses) + 105
    layers = []
    for index, item in enumerate(analyses):
        distribution = item["distribution"]
        quantiles = distribution.get("quantiles") or {}
        q25, q75 = quantiles.get("0.25"), quantiles.get("0.75")
        median = distribution["median"]
        y = top + index * row
        color = COLORS[index % len(COLORS)]
        layers.append(f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" stroke="#e3e8e5"/>')
        layers.append(f'<text x="{left - 16}" y="{y - 4}" text-anchor="end" font-size="14" font-weight="600">{html.escape(item["name"])}</text>')
        layers.append(f'<text x="{left - 16}" y="{y + 17}" text-anchor="end" font-size="12" fill="#66716b">n={item["n_subjects"]} · {html.escape(item["metric"]["id"])}</text>')
        if q25 is not None and q75 is not None:
            x25, x75 = _scale(q25, low, high, left, right), _scale(q75, low, high, left, right)
            layers.append(f'<line x1="{x25:.1f}" y1="{y}" x2="{x75:.1f}" y2="{y}" stroke="{color}" stroke-width="8" stroke-linecap="round"/>')
        xmedian = _scale(median, low, high, left, right)
        layers.append(f'<circle cx="{xmedian:.1f}" cy="{y}" r="8" fill="{color}"/><text x="{xmedian + 13:.1f}" y="{y + 5}" font-size="13">median {median:g}</text>')
    ticks = []
    axis_y = top + row * len(analyses) - 30
    for index in range(6):
        fraction = index / 5
        x = left + fraction * (right - left)
        value = low + fraction * (high - low)
        ticks.append(f'<line x1="{x:.1f}" y1="{axis_y}" x2="{x:.1f}" y2="{axis_y + 6}" stroke="#34413b"/><text x="{x:.1f}" y="{axis_y + 25}" text-anchor="middle" font-size="12">{value:.2g}</text>')
    title = f"Analysis comparison: {comparison['name']}"
    footer = f"IQR and median · common subjects={len(comparison['common_subject_ids'])} · {comparison['comparison_id']}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">Audited comparison of frozen reference-class analyses.</desc>
<rect width="100%" height="100%" fill="#fff"/><g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" fill="#202522">
<text x="40" y="38" font-size="22" font-weight="600">{html.escape(title)}</text>
<text x="40" y="61" font-size="13" fill="#5f6963">Points are medians; thick lines are nearest-rank P25–P75 intervals.</text>
{''.join(layers)}{''.join(ticks)}
<text x="40" y="{height - 24}" font-size="12" fill="#5f6963">{html.escape(footer)}</text></g></svg>'''


def create_comparison_plot(root: Path, comparison_id: str, output: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    comparison = load_comparison(root, comparison_id)
    output = output.resolve()
    artifact = _atomic_svg(output, _summary_svg(comparison))
    receipt = {
        "kind": "distribution_summary",
        "comparison_id": comparison_id,
        "comparison_sha256": sha256_bytes(canonical_bytes(comparison)),
        "analysis_ids": comparison["analysis_ids"],
        "output": str(output),
        "data_sha256": artifact["sha256"],
        "created_at": now(),
    }
    receipt_artifact = atomic_write(output.with_suffix(".comparison-plot.json"), receipt, replace=True)
    return receipt, [artifact, receipt_artifact]
