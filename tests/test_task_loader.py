"""Tests for the TaskLoader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pantheon_bench.task_loader import Task, TaskLoader


def test_load_suite(tasks_dir: Path) -> None:
    """Loading the example suite returns the expected number of tasks."""
    loader = TaskLoader(tasks_dir)
    tasks = loader.load_suite("example")
    assert len(tasks) == 5
    assert all(isinstance(t, Task) for t in tasks)


def test_load_suite_filter_difficulty(tasks_dir: Path) -> None:
    """Filtering by difficulty returns only matching tasks."""
    loader = TaskLoader(tasks_dir)
    easy = loader.load_suite("example", difficulty="easy")
    assert len(easy) == 2
    assert all(t.difficulty == "easy" for t in easy)


def test_load_suite_sample(tasks_dir: Path) -> None:
    """Sampling N tasks returns exactly N tasks."""
    loader = TaskLoader(tasks_dir)
    sampled = loader.load_suite("example", sample_n=3, seed=0)
    assert len(sampled) == 3


def test_load_suite_sample_larger_than_total(tasks_dir: Path) -> None:
    """Requesting more tasks than available returns all of them."""
    loader = TaskLoader(tasks_dir)
    sampled = loader.load_suite("example", sample_n=100, seed=0)
    assert len(sampled) == 5


def test_load_suite_not_found(tasks_dir: Path) -> None:
    """FileNotFoundError is raised for a missing suite."""
    loader = TaskLoader(tasks_dir)
    with pytest.raises(FileNotFoundError):
        loader.load_suite("nonexistent")


def test_list_suites(tasks_dir: Path) -> None:
    """list_suites returns available suite directory names."""
    loader = TaskLoader(tasks_dir)
    suites = loader.list_suites()
    assert "example" in suites


def test_list_suites_empty(tmp_path: Path) -> None:
    """list_suites returns an empty list when base_dir has no sub-directories."""
    loader = TaskLoader(tmp_path)
    assert loader.list_suites() == []


def test_load_single_task_file(tmp_path: Path) -> None:
    """A JSON file with a single task dict (not a list) is loaded correctly."""
    suite_dir = tmp_path / "single"
    suite_dir.mkdir()
    task_data = {
        "id": "s1",
        "url": "https://example.com",
        "objective": "Do something",
        "evaluation_criteria": "Done",
        "difficulty": "hard",
    }
    (suite_dir / "task.json").write_text(json.dumps(task_data))
    loader = TaskLoader(tmp_path)
    tasks = loader.load_suite("single")
    assert len(tasks) == 1
    assert tasks[0].id == "s1"
    assert tasks[0].difficulty == "hard"


def test_task_model_extra_fields() -> None:
    """Task model allows extra fields without error."""
    t = Task(
        id="x",
        url="https://example.com",
        objective="obj",
        evaluation_criteria="crit",
        custom_field="hello",
    )
    assert t.id == "x"
