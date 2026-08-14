from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "simulations" / "theatrical-musicals"


def test_cohort_fixture_separates_membership_from_outcomes() -> None:
    fixture = json.loads((EXAMPLE / "cohort.json").read_text(encoding="utf-8"))
    candidates = fixture["candidates"]
    included = [candidate for candidate in candidates if candidate["included"]]
    excluded = [candidate for candidate in candidates if not candidate["included"]]

    assert len(candidates) == 20
    assert len(included) == 18
    assert len(excluded) == 2
    assert all(candidate["membership_evidence"] for candidate in candidates)
    assert all(candidate["exclusion_reason"] for candidate in excluded)
    assert all("worldwide_gross" not in candidate for candidate in excluded)
    assert all({"budget_low", "budget_high", "worldwide_gross"} <= candidate.keys() for candidate in included)


def test_musical_tutorial_rebuilds_through_cli(tmp_path: Path) -> None:
    workspace = tmp_path / "musical-workspace"
    network_guard = tmp_path / "network-guard"
    network_guard.mkdir()
    (network_guard / "sitecustomize.py").write_text(
        "import socket\n"
        "def blocked(*args, **kwargs):\n"
        "    raise RuntimeError('network access is forbidden in the tutorial smoke test')\n"
        "socket.create_connection = blocked\n"
        "socket.socket.connect = blocked\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(network_guard) if not existing_pythonpath else f"{network_guard}{os.pathsep}{existing_pythonpath}"
    result = subprocess.run(
        [sys.executable, str(EXAMPLE / "rebuild.py"), str(workspace), "--quiet"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads(result.stdout)

    assert summary["candidate_count"] == 20
    assert summary["included_count"] == 18
    assert summary["excluded_count"] == 2
    assert summary["observation_count"] == 90
    assert summary["distribution"]["median"] == 1.45435
    assert summary["validation"]["valid"] is True
    assert summary["validation"]["json_records"] == 358

    collection = workspace / ".flyvbjerg" / "collections" / "theatrical_musicals"
    assert len(list((collection / "cases").glob("*/case.json"))) == 18
    assert len(list((collection / "observations").glob("*.json"))) == 90
    assert len(list((collection / "intake" / "items").glob("*.json"))) == 20
    assert not list(workspace.rglob("*.ep")), "tutorial must not construct or execute EDSL jobs"


def test_tutorial_documentation_points_to_canonical_runner() -> None:
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert "cohort.json" in html
    assert "rebuild.py" in html
    assert "flyvbjerg next" in html
    assert "ep run" not in html
