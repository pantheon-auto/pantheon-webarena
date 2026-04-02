"""Tests for the CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from pantheon_bench.cli import cli


def test_cli_version() -> None:
    """--version prints the version string."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_list_agents() -> None:
    """list-agents prints registered adapter names."""
    runner = CliRunner()
    result = runner.invoke(cli, ["list-agents"])
    assert result.exit_code == 0
    assert "example" in result.output
    assert "manual" in result.output


def test_cli_list_suites() -> None:
    """list-suites shows available suites from the default tasks dir."""
    runner = CliRunner()
    # Use the project's own tasks directory
    tasks_dir = str(Path(__file__).resolve().parent.parent / "tasks")
    result = runner.invoke(cli, ["list-suites", "--tasks-dir", tasks_dir])
    assert result.exit_code == 0
    assert "example" in result.output


def test_cli_run_example(tmp_path: Path) -> None:
    """'run' with example adapter produces JSON output."""
    runner = CliRunner()
    output = str(tmp_path / "results.json")
    tasks_dir = str(Path(__file__).resolve().parent.parent / "tasks")

    result = runner.invoke(
        cli,
        [
            "run",
            "--agent",
            "example",
            "--suite",
            "example",
            "--tasks",
            "3",
            "--output",
            output,
            "--tasks-dir",
            tasks_dir,
            "--seed",
            "42",
        ],
    )
    assert result.exit_code == 0, result.output

    data = json.loads(Path(output).read_text())
    assert data["agent"]["name"] == "example"
    assert len(data["results"]) == 3
    assert "metrics" in data


def test_cli_run_unknown_agent() -> None:
    """'run' with an unknown agent name exits with an error."""
    runner = CliRunner()
    tasks_dir = str(Path(__file__).resolve().parent.parent / "tasks")
    result = runner.invoke(
        cli,
        [
            "run",
            "--agent",
            "nonexistent",
            "--suite",
            "example",
            "--tasks-dir",
            tasks_dir,
        ],
    )
    assert result.exit_code != 0


def test_cli_run_unknown_suite() -> None:
    """'run' with an unknown suite exits with an error."""
    runner = CliRunner()
    tasks_dir = str(Path(__file__).resolve().parent.parent / "tasks")
    result = runner.invoke(
        cli,
        [
            "run",
            "--agent",
            "example",
            "--suite",
            "nonexistent",
            "--tasks-dir",
            tasks_dir,
        ],
    )
    assert result.exit_code != 0


def test_cli_compare(tmp_path: Path) -> None:
    """'compare' generates a diff report from two JSON files."""
    runner = CliRunner()

    payload_a = {
        "agent": {"name": "a"},
        "results": [],
        "metrics": {"success_rate": 50.0},
    }
    payload_b = {
        "agent": {"name": "b"},
        "results": [],
        "metrics": {"success_rate": 75.0},
    }
    fa = tmp_path / "a.json"
    fb = tmp_path / "b.json"
    fa.write_text(json.dumps(payload_a))
    fb.write_text(json.dumps(payload_b))

    out = str(tmp_path / "cmp.md")
    result = runner.invoke(cli, ["compare", str(fa), str(fb), "-o", out])
    assert result.exit_code == 0
    text = Path(out).read_text()
    assert "Comparison Report" in text
