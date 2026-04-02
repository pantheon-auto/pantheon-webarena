"""Shared fixtures for pantheon_bench tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pantheon_bench.adapters.example import ExampleAdapter
from pantheon_bench.evaluator import TaskResult
from pantheon_bench.task_loader import Task


@pytest.fixture
def example_adapter() -> ExampleAdapter:
    """Return an ExampleAdapter with a fixed seed for deterministic tests."""
    return ExampleAdapter(seed=42, success_rate=0.6)


@pytest.fixture
def sample_tasks() -> list[Task]:
    """Return a small list of Task objects for testing."""
    return [
        Task(
            id=f"test-{i:03d}",
            url=f"https://example.com/page{i}",
            objective=f"Do task {i}",
            evaluation_criteria=f"Task {i} is complete",
            difficulty="medium",
        )
        for i in range(1, 6)
    ]


@pytest.fixture
def sample_results() -> list[TaskResult]:
    """Return known TaskResult objects for metric tests."""
    return [
        TaskResult(
            task_id="t1",
            success=True,
            steps=["a", "b", "c"],
            duration_ms=100.0,
            cost_usd=0.005,
            blocked=False,
        ),
        TaskResult(
            task_id="t2",
            success=True,
            steps=["a", "b"],
            duration_ms=200.0,
            cost_usd=0.010,
            blocked=False,
        ),
        TaskResult(
            task_id="t3",
            success=False,
            steps=["a"],
            duration_ms=300.0,
            cost_usd=0.015,
            blocked=False,
        ),
        TaskResult(
            task_id="t4",
            success=False,
            steps=["a", "b", "c", "d"],
            duration_ms=400.0,
            cost_usd=0.020,
            blocked=True,
        ),
        TaskResult(
            task_id="t5",
            success=True,
            steps=["a", "b", "c", "d", "e"],
            duration_ms=150.0,
            cost_usd=0.008,
            blocked=False,
        ),
    ]


@pytest.fixture
def tasks_dir(tmp_path: Path) -> Path:
    """Create a temporary tasks directory with an 'example' suite."""
    suite_dir = tmp_path / "example"
    suite_dir.mkdir()
    tasks = [
        {
            "id": f"tmp-{i:03d}",
            "url": f"https://example.com/{i}",
            "objective": f"Objective {i}",
            "evaluation_criteria": f"Criteria {i}",
            "difficulty": "easy" if i <= 2 else "medium",
        }
        for i in range(1, 6)
    ]
    (suite_dir / "tasks.json").write_text(json.dumps(tasks))
    return tmp_path


@pytest.fixture
def sample_payload(sample_results: list[TaskResult]) -> dict:
    """Return a complete benchmark payload dict."""
    return {
        "agent": {"name": "test-agent", "version": "1.0.0"},
        "results": [r.model_dump() for r in sample_results],
        "metrics": {
            "total_tasks": 5,
            "success_rate": 60.0,
            "step_count_mean": 3.0,
            "step_count_p95": 5.0,
            "latency_p50_ms": 200.0,
            "latency_p95_ms": 400.0,
            "cost_per_task_usd": 0.0116,
            "anti_bot_evasion_rate": 80.0,
            "determinism_score": None,
        },
        "warnings": [],
    }
