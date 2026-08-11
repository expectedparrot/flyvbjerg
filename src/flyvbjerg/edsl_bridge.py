"""Native EDSL construction boundary. This module never executes jobs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ValidationError


PROMPTS = {
    "extract": """Read only the registered capture below. Propose evidence items and scoped claims relevant to the named collection. Preserve exact wording and return a JSON array with kind, text, locator, scope_kind, scope_ids, claim_kind, value, unit, and limitations. Do not browse or add outside facts.\n\nCollection: {{ collection_title }}\nCapture id: {{ capture_id }}\nCapture text:\n{{ capture_text }}""",
    "code": """Apply the supplied rubric only to the registered capture. Return a JSON array of candidate codings with exact locators and limitations. Do not browse.\n\nRubric: {{ task }}\nCapture id: {{ capture_id }}\nCapture text:\n{{ capture_text }}""",
    "verify": """Verify the candidate only against the registered capture. Return JSON with supported, exact_locator, explanation, and limitations. Do not browse or use outside knowledge.\n\nCandidate: {{ task }}\nCapture id: {{ capture_id }}\nCapture text:\n{{ capture_text }}""",
}


def imports() -> tuple[Any, Any, Any, Any]:
    try:
        from edsl import Jobs, QuestionFreeText, Scenario, ScenarioList
    except ImportError as exc:
        raise ValidationError("EDSL is required to build processing artifacts", "Install a compatible EDSL release or overlay ../edsl.") from exc
    return Jobs, QuestionFreeText, Scenario, ScenarioList


def build_jobs(mode: str, scenarios: list[dict[str, Any]]) -> Any:
    if mode not in PROMPTS:
        raise ValidationError(f"Unsupported processing mode: {mode}")
    Jobs, QuestionFreeText, Scenario, ScenarioList = imports()
    question = QuestionFreeText(question_name=f"flyvbjerg_{mode}", question_text=PROMPTS[mode])
    return Jobs(survey=question.to_survey()).by(ScenarioList([Scenario(item) for item in scenarios]))


def save_and_verify(value: Any, path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    saved = value.git.save(path)
    type(value).git.load(saved["path"])
    return {"path": str(saved["path"]), "media_type": "application/vnd.expectedparrot.ep", "role": "edsl_jobs"}


def audit_results(jobs_path: Path, results_path: Path) -> dict[str, Any]:
    try:
        from edsl import Jobs, Results
    except ImportError as exc:
        raise ValidationError("EDSL is required to audit Results") from exc
    jobs = Jobs.git.load(jobs_path)
    results = Results.git.load(results_path)
    expected = len(jobs.scenarios) * len(jobs.models) * len(jobs.agents)
    actual = len(results)
    exceptions = 0
    null_answers = 0
    for result in results:
        answer = getattr(result, "answer", {}) or {}
        if any(value is None for value in answer.values()):
            null_answers += 1
        if getattr(result, "exceptions", None):
            exceptions += 1
    return {"expected_results": expected, "actual_results": actual, "complete": actual == expected and not exceptions and not null_answers, "exceptions": exceptions, "null_answers": null_answers}

