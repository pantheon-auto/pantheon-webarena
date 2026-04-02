"""Tests for the BenchmarkRunner."""

from __future__ import annotations

from io import StringIO

from rich.console import Console

from pantheon_bench.adapters.example import ExampleAdapter
from pantheon_bench.runner import BenchmarkRunner
from pantheon_bench.task_loader import Task


def _make_console() -> Console:
    """Create a Console that writes to a string buffer (suppresses output)."""
    return Console(file=StringIO(), force_terminal=True)


def test_runner_sequential(sample_tasks: list[Task]) -> None:
    """Runner executes all tasks sequentially and returns valid payload."""
    adapter = ExampleAdapter(seed=99)
    runner = BenchmarkRunner(
        adapter=adapter,
        tasks=sample_tasks,
        concurrency=1,
        console=_make_console(),
    )
    payload = runner.run()

    assert "agent" in payload
    assert payload["agent"]["name"] == "example"
    assert len(payload["results"]) == len(sample_tasks)
    assert "metrics" in payload
    assert payload["metrics"]["total_tasks"] == len(sample_tasks)


def test_runner_concurrent(sample_tasks: list[Task]) -> None:
    """Runner executes tasks concurrently and collects all results."""
    adapter = ExampleAdapter(seed=99)
    runner = BenchmarkRunner(
        adapter=adapter,
        tasks=sample_tasks,
        concurrency=3,
        console=_make_console(),
    )
    payload = runner.run()

    assert len(payload["results"]) == len(sample_tasks)
    assert payload["metrics"]["total_tasks"] == len(sample_tasks)


def test_runner_empty_tasks() -> None:
    """Runner handles an empty task list gracefully."""
    adapter = ExampleAdapter(seed=1)
    runner = BenchmarkRunner(
        adapter=adapter,
        tasks=[],
        console=_make_console(),
    )
    payload = runner.run()

    assert payload["metrics"]["total_tasks"] == 0
    assert payload["results"] == []


def test_runner_results_have_required_keys(sample_tasks: list[Task]) -> None:
    """Each result in the payload contains required keys."""
    adapter = ExampleAdapter(seed=7)
    runner = BenchmarkRunner(
        adapter=adapter,
        tasks=sample_tasks,
        console=_make_console(),
    )
    payload = runner.run()

    for r in payload["results"]:
        assert "task_id" in r
        assert "success" in r
        assert "steps" in r
        assert "duration_ms" in r
        assert "cost_usd" in r
        assert "blocked" in r
