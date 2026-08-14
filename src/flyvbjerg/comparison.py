from __future__ import annotations

from pathlib import Path
from typing import Any

from .analysis import _analysis_subject_values, load_analysis, threshold_analysis
from .errors import NotFound, ValidationError
from .workspace import atomic_write, canonical_bytes, collection_root, new_id, now, read_json, sha256_bytes


def _summary(analysis: dict[str, Any]) -> dict[str, Any]:
    distribution = analysis["distribution"]
    return {
        "analysis_id": analysis["analysis_id"],
        "name": analysis["name"],
        "collection_id": analysis["collection_id"],
        "metric": analysis["metric"],
        "target": analysis.get("target"),
        "n_subjects": analysis["n_subjects"],
        "subject_ids": analysis["subject_ids"],
        "dependence_status": analysis.get("dependence_status", "not_assessed"),
        "n_clusters": analysis.get("n_clusters"),
        "distribution": {key: distribution.get(key) for key in ("count", "min", "median", "max", "mean", "quantiles", "quantile_convention")},
        "created_at": analysis.get("created_at"),
    }


def create_comparison(root: Path, collection: str, name: str, analysis_ids: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    if len(analysis_ids) < 2:
        raise ValidationError("A comparison requires at least two analyses")
    if len(set(analysis_ids)) != len(analysis_ids):
        raise ValidationError("Analysis IDs in a comparison must be unique")
    base = collection_root(root, collection)
    analyses = [load_analysis(root, analysis_id) for analysis_id in analysis_ids]
    wrong_collection = [item["analysis_id"] for item in analyses if item["collection_id"] != collection]
    if wrong_collection:
        raise ValidationError(f"Analyses do not belong to collection {collection}: {', '.join(wrong_collection)}")

    baseline = analyses[0]
    baseline_subjects = set(baseline["subject_ids"])
    all_subjects = set().union(*(set(item["subject_ids"]) for item in analyses))
    common_subjects = set.intersection(*(set(item["subject_ids"]) for item in analyses))
    baseline_distribution = baseline["distribution"]
    deltas = []
    for item in analyses:
        distribution = item["distribution"]
        deltas.append({
            "analysis_id": item["analysis_id"],
            "median_from_baseline": distribution.get("median") - baseline_distribution.get("median") if distribution.get("median") is not None and baseline_distribution.get("median") is not None else None,
            "mean_from_baseline": distribution.get("mean") - baseline_distribution.get("mean") if distribution.get("mean") is not None and baseline_distribution.get("mean") is not None else None,
            "subjects_only_in_analysis": sorted(set(item["subject_ids"]) - baseline_subjects),
            "baseline_subjects_absent": sorted(baseline_subjects - set(item["subject_ids"])),
        })
    record = {
        "comparison_id": new_id("comparison"),
        "name": name,
        "collection_id": collection,
        "analysis_ids": analysis_ids,
        "analyses": [_summary(item) for item in analyses],
        "common_subject_ids": sorted(common_subjects),
        "all_subject_ids": sorted(all_subjects),
        "subject_sets_equal": all(set(item["subject_ids"]) == baseline_subjects for item in analyses[1:]),
        "metrics_equal": all(item["metric"] == baseline["metric"] for item in analyses[1:]),
        "targets_equal": all(item.get("target") == baseline.get("target") for item in analyses[1:]),
        "dependence_equal": all((item.get("dependence_status"), item.get("n_clusters")) == (baseline.get("dependence_status"), baseline.get("n_clusters")) for item in analyses[1:]),
        "numeric_coverage_equal": all(item["distribution"].get("count") == baseline_distribution.get("count") for item in analyses[1:]),
        "quantile_conventions_equal": all(item["distribution"].get("quantile_convention") == baseline_distribution.get("quantile_convention") for item in analyses[1:]),
        "distribution_deltas": deltas,
        "created_at": now(),
    }
    artifact = atomic_write(base / "comparison-sets" / record["comparison_id"] / "comparison.json", record)
    return record, artifact


def load_comparison(root: Path, comparison_id: str) -> dict[str, Any]:
    matches = list((root / "collections").glob(f"*/comparison-sets/{comparison_id}/comparison.json"))
    if not matches:
        raise NotFound(f"Comparison not found: {comparison_id}")
    return read_json(matches[0])


def threshold_comparison(root: Path, comparison_id: str, operator: str, values: list[float]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not values:
        raise ValidationError("Provide at least one --value")
    comparison = load_comparison(root, comparison_id)
    analyses = [load_analysis(root, analysis_id) for analysis_id in comparison["analysis_ids"]]
    subject_values = {item["analysis_id"]: _analysis_subject_values(root, item) for item in analyses}
    thresholds = []
    for value in values:
        results = [threshold_analysis(root, item["analysis_id"], operator, value) for item in analyses]
        common = set(comparison["common_subject_ids"])
        baseline_matching = set(results[0]["matching_subject_ids"])
        baseline_missing = set(results[0]["missing_subject_ids"])
        switches = []
        missingness_changes = []
        for result in results[1:]:
            matching = set(result["matching_subject_ids"])
            missing = set(result["missing_subject_ids"])
            for subject in sorted(baseline_missing ^ missing):
                missingness_changes.append({
                    "subject_id": subject,
                    "baseline_analysis_id": results[0]["analysis_id"],
                    "comparison_analysis_id": result["analysis_id"],
                    "baseline_missing": subject in baseline_missing,
                    "comparison_missing": subject in missing,
                })
            for subject in sorted(common):
                if subject in baseline_missing or subject in missing:
                    continue
                before = subject in baseline_matching
                after = subject in matching
                if before != after:
                    switches.append({
                        "subject_id": subject,
                        "baseline_analysis_id": results[0]["analysis_id"],
                        "comparison_analysis_id": result["analysis_id"],
                        "baseline_value": subject_values[results[0]["analysis_id"]].get(subject),
                        "comparison_value": subject_values[result["analysis_id"]].get(subject),
                        "baseline_matches": before,
                        "comparison_matches": after,
                    })
        frequencies = [result["frequency"] for result in results]
        invariant = not switches and not missingness_changes and len(set(frequencies)) == 1 and comparison["subject_sets_equal"]
        thresholds.append({
            "threshold": {"operator": operator, "value": value},
            "analysis_results": results,
            "classification_switches": switches,
            "missingness_changes": missingness_changes,
            "classification_invariant": invariant,
            "conclusion": "robust" if invariant else "assumption_sensitive",
        })
    record = {
        "comparison_threshold_id": new_id("comparison_threshold"),
        "comparison_id": comparison_id,
        "comparison_sha256": sha256_bytes(canonical_bytes(comparison)),
        "operator": operator,
        "values": values,
        "results": thresholds,
        "created_at": now(),
    }
    base = collection_root(root, comparison["collection_id"])
    artifact = atomic_write(base / "comparison-sets" / comparison_id / "thresholds" / f"{record['comparison_threshold_id']}.json", record)
    return record, artifact
