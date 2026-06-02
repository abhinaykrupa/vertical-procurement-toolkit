"""
CLI smoke tests — confirm the CLI runs end-to-end and produces valid JSON.
"""

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(*args, cwd: Path) -> tuple[int, str, str]:
    """Run the vpt CLI via python -m, return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "vpt.cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


def test_cli_version(project_root):
    code, out, _ = _run_cli("--version", cwd=project_root)
    assert code == 0
    assert "vpt" in out


def test_cli_adapters_lists_known(project_root):
    code, out, _ = _run_cli("adapters", cwd=project_root)
    assert code == 0
    assert "Benco" in out
    assert "Vetcove" in out
    assert "generic" in out


def test_cli_detect_benco(project_root):
    code, out, _ = _run_cli(
        "detect", "-s", "sample_data/auburn_dental_benco.csv",
        cwd=project_root,
    )
    assert code == 0
    assert "Benco" in out


def test_cli_analyze_end_to_end(project_root, tmp_path):
    out_path = tmp_path / "results.json"
    code, _, stderr = _run_cli(
        "analyze",
        "-s", "sample_data/auburn_dental_benco.csv",
        "-c", "sample_data/sourceclub_catalog.csv",
        "-o", str(out_path),
        cwd=project_root,
    )
    assert code == 0, f"CLI failed: {stderr}"
    assert out_path.exists()
    data = json.loads(out_path.read_text())
    assert "summary" in data
    assert "line_items" in data
    assert data["summary"]["adapter"] == "Benco"
    assert data["summary"]["total_lines"] > 0
