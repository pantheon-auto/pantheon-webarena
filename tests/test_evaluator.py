"""Tests for the ResultEvaluator."""

from __future__ import annotations

from pantheon_bench.evaluator import ResultEvaluator, TaskResult


def test_validate_complete_result() -> None:
    """A complete, well-formed result validates without warnings."""
    raw = {
        "task_id": "t1",
        "success": True,
        "steps": ["a", "b"],
        "duration_ms": 100.0,
        "cost_usd": 0.01,
        "blocked": False,
    }
    result, warnings = ResultEvaluator.validate(raw)
    assert isinstance(result, TaskResult)
    assert result.success is True
    assert result.task_id == "t1"
    assert len(warnings) == 0


def test_validate_missing_keys() -> None:
    """Missing keys produce warnings but still return a result."""
    raw = {"task_id": "t2", "success": True}
    result, warnings = ResultEvaluator.validate(raw)
    assert result.task_id == "t2"
    assert result.success is True
    assert result.steps == []
    assert any("Missing keys" in w for w in warnings)


def test_validate_negative_duration_clamped() -> None:
    """Negative duration_ms is clamped to 0."""
    raw = {
        "task_id": "t3",
        "success": False,
        "steps": [],
        "duration_ms": -50.0,
        "cost_usd": 0.0,
        "blocked": False,
    }
    result, warnings = ResultEvaluator.validate(raw)
    assert result.duration_ms == 0.0
    assert any("negative" in w for w in warnings)


def test_validate_negative_cost_clamped() -> None:
    """Negative cost_usd is clamped to 0."""
    raw = {
        "task_id": "t4",
        "success": False,
        "steps": [],
        "duration_ms": 10.0,
        "cost_usd": -1.0,
        "blocked": False,
    }
    result, warnings = ResultEvaluator.validate(raw)
    assert result.cost_usd == 0.0
    assert any("negative" in w for w in warnings)


def test_validate_success_coerced_to_bool() -> None:
    """Non-bool success is coerced and a warning is emitted."""
    raw = {
        "task_id": "t5",
        "success": 1,
        "steps": ["x"],
        "duration_ms": 10.0,
        "cost_usd": 0.0,
        "blocked": False,
    }
    result, warnings = ResultEvaluator.validate(raw)
    assert result.success is True
    assert any("bool" in w for w in warnings)


def test_validate_steps_coerced_to_list() -> None:
    """Non-list steps is coerced and a warning is emitted."""
    raw = {
        "task_id": "t6",
        "success": False,
        "steps": ("a", "b"),
        "duration_ms": 10.0,
        "cost_usd": 0.0,
        "blocked": False,
    }
    result, warnings = ResultEvaluator.validate(raw)
    assert isinstance(result.steps, list)
    assert any("list" in w for w in warnings)


def test_validate_batch() -> None:
    """validate_batch processes multiple raw dicts."""
    raws = [
        {
            "task_id": "b1",
            "success": True,
            "steps": [],
            "duration_ms": 1,
            "cost_usd": 0,
            "blocked": False,
        },
        {
            "task_id": "b2",
            "success": False,
            "steps": ["x"],
            "duration_ms": 2,
            "cost_usd": 0,
            "blocked": True,
        },
    ]
    results = ResultEvaluator.validate_batch(raws)
    assert len(results) == 2
    assert results[0].task_id == "b1"
    assert results[1].blocked is True


def test_validate_empty_dict() -> None:
    """A completely empty dict still returns a result with defaults."""
    result, warnings = ResultEvaluator.validate({})
    assert result.task_id == "unknown"
    assert result.success is False
    assert len(warnings) > 0
