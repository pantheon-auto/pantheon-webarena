"""Tests for the Reporter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pantheon_bench.reporter import Reporter


def test_to_json(sample_payload: dict[str, Any], tmp_path: Path) -> None:
    """to_json writes valid JSON matching the payload."""
    out = tmp_path / "results.json"
    Reporter.to_json(sample_payload, out)
    assert out.exists()

    loaded = json.loads(out.read_text())
    assert loaded["agent"]["name"] == "test-agent"
    assert len(loaded["results"]) == 5
    assert loaded["metrics"]["success_rate"] == 60.0


def test_to_markdown(sample_payload: dict[str, Any], tmp_path: Path) -> None:
    """to_markdown writes a Markdown file with expected content."""
    out = tmp_path / "report.md"
    Reporter.to_markdown(sample_payload, out)
    assert out.exists()

    text = out.read_text()
    assert "# Benchmark Report" in text
    assert "test-agent" in text
    assert "60.0%" in text
    assert "Per-Task Results" in text


def test_to_markdown_no_results(tmp_path: Path) -> None:
    """to_markdown handles a payload with no results."""
    payload: dict[str, Any] = {
        "agent": {"name": "empty", "version": "0"},
        "results": [],
        "metrics": {"total_tasks": 0, "success_rate": 0.0},
        "warnings": ["No tasks executed"],
    }
    out = tmp_path / "empty.md"
    Reporter.to_markdown(payload, out)
    text = out.read_text()
    assert "# Benchmark Report" in text
    assert "No tasks executed" in text


def test_compare(sample_payload: dict[str, Any], tmp_path: Path) -> None:
    """compare generates a diff Markdown from two JSON files."""
    file_a = tmp_path / "a.json"
    file_b = tmp_path / "b.json"

    payload_b = {
        **sample_payload,
        "agent": {"name": "agent-b", "version": "2.0.0"},
        "metrics": {
            **sample_payload["metrics"],
            "success_rate": 80.0,
            "cost_per_task_usd": 0.025,
        },
    }

    file_a.write_text(json.dumps(sample_payload))
    file_b.write_text(json.dumps(payload_b))

    out = tmp_path / "diff.md"
    Reporter.compare(file_a, file_b, out)
    assert out.exists()

    text = out.read_text()
    assert "Comparison Report" in text
    assert "test-agent" in text
    assert "agent-b" in text
    assert "Delta" in text


def test_to_json_creates_parent_dirs(tmp_path: Path) -> None:
    """to_json creates parent directories if they don't exist."""
    out = tmp_path / "nested" / "deep" / "results.json"
    Reporter.to_json({"agent": {}, "results": [], "metrics": {}}, out)
    assert out.exists()
