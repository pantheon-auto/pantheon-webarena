"""Tests for metric computation."""

from __future__ import annotations

from pantheon_bench.evaluator import TaskResult
from pantheon_bench.metrics import compute_metrics


def test_compute_metrics_basic(sample_results: list[TaskResult]) -> None:
    """Metrics are computed correctly from known results."""
    m = compute_metrics(sample_results)

    assert m["total_tasks"] == 5
    # 3 out of 5 succeed => 60%
    assert m["success_rate"] == 60.0
    # Steps: 3, 2, 1, 4, 5 => mean = 3.0
    assert m["step_count_mean"] == 3.0
    # Costs: 0.005, 0.010, 0.015, 0.020, 0.008 => mean = 0.0116
    assert m["cost_per_task_usd"] == 0.0116
    # 4 out of 5 not blocked => 80%
    assert m["anti_bot_evasion_rate"] == 80.0
    # No repeat runs => determinism is None
    assert m["determinism_score"] is None


def test_compute_metrics_empty() -> None:
    """Empty result list returns zeroed metrics."""
    m = compute_metrics([])
    assert m["total_tasks"] == 0
    assert m["success_rate"] == 0.0
    assert m["determinism_score"] is None


def test_compute_metrics_all_success() -> None:
    """100% success rate when all tasks succeed."""
    results = [
        TaskResult(
            task_id=f"s{i}",
            success=True,
            steps=["a"],
            duration_ms=100.0,
            cost_usd=0.01,
            blocked=False,
        )
        for i in range(10)
    ]
    m = compute_metrics(results)
    assert m["success_rate"] == 100.0
    assert m["anti_bot_evasion_rate"] == 100.0


def test_compute_metrics_all_blocked() -> None:
    """0% evasion when all tasks are blocked."""
    results = [
        TaskResult(
            task_id=f"b{i}",
            success=False,
            steps=[],
            duration_ms=50.0,
            cost_usd=0.0,
            blocked=True,
        )
        for i in range(5)
    ]
    m = compute_metrics(results)
    assert m["anti_bot_evasion_rate"] == 0.0


def test_determinism_perfect() -> None:
    """Determinism score is 1.0 when all runs agree."""
    run = [
        TaskResult(task_id="d1", success=True, steps=[], duration_ms=0, cost_usd=0, blocked=False),
        TaskResult(task_id="d2", success=False, steps=[], duration_ms=0, cost_usd=0, blocked=False),
    ]
    m = compute_metrics(run, repeat_runs=[run, run])
    assert m["determinism_score"] == 1.0


def test_determinism_partial() -> None:
    """Determinism score reflects disagreements across runs."""
    run_a = [
        TaskResult(task_id="d1", success=True, steps=[], duration_ms=0, cost_usd=0, blocked=False),
        TaskResult(task_id="d2", success=True, steps=[], duration_ms=0, cost_usd=0, blocked=False),
    ]
    run_b = [
        TaskResult(task_id="d1", success=True, steps=[], duration_ms=0, cost_usd=0, blocked=False),
        TaskResult(task_id="d2", success=False, steps=[], duration_ms=0, cost_usd=0, blocked=False),
    ]
    m = compute_metrics(run_a, repeat_runs=[run_a, run_b])
    # d1 agrees (True, True), d2 disagrees (True, False) => 0.5
    assert m["determinism_score"] == 0.5


def test_latency_percentiles() -> None:
    """P50 and P95 latency are computed correctly."""
    results = [
        TaskResult(
            task_id=f"l{i}",
            success=True,
            steps=["a"],
            duration_ms=float(i * 100),
            cost_usd=0.0,
            blocked=False,
        )
        for i in range(1, 11)  # 100, 200, ..., 1000
    ]
    m = compute_metrics(results)
    # Values: 100..1000, nearest-rank P50 index = int(10*0.5) = 5 => 600
    assert m["latency_p50_ms"] == 600.0
    # nearest-rank P95 index = int(10*0.95) = 9 => 1000
    assert m["latency_p95_ms"] == 1000.0
