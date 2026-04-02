"""Compute aggregate metrics from a list of task results."""

from __future__ import annotations

import statistics
from typing import Any

from pantheon_bench.evaluator import TaskResult


def _percentile(values: list[float], pct: float) -> float:
    """Compute a percentile from a sorted list using nearest-rank method.

    Args:
        values: Non-empty list of numeric values (will be sorted internally).
        pct: Percentile in [0, 100].

    Returns:
        The value at the requested percentile.
    """
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(len(s) * pct / 100.0)))
    return s[k]


def compute_metrics(
    results: list[TaskResult],
    *,
    repeat_runs: list[list[TaskResult]] | None = None,
) -> dict[str, Any]:
    """Compute aggregate benchmark metrics.

    Args:
        results: List of validated TaskResult objects from a single run.
        repeat_runs: Optional list of additional runs (each a list of
            TaskResult) used to compute determinism_score. If provided,
            the first element of repeat_runs should be identical to *results*.

    Returns:
        Dict of computed metrics.
    """
    if not results:
        return {
            "total_tasks": 0,
            "success_rate": 0.0,
            "step_count_mean": 0.0,
            "step_count_p95": 0.0,
            "latency_p50_ms": 0.0,
            "latency_p95_ms": 0.0,
            "cost_per_task_usd": 0.0,
            "anti_bot_evasion_rate": 0.0,
            "determinism_score": None,
        }

    total = len(results)
    successes = sum(1 for r in results if r.success)
    success_rate = (successes / total) * 100.0

    step_counts = [float(len(r.steps)) for r in results]
    step_count_mean = statistics.mean(step_counts)
    step_count_p95 = _percentile(step_counts, 95)

    latencies = [r.duration_ms for r in results]
    latency_p50 = _percentile(latencies, 50)
    latency_p95 = _percentile(latencies, 95)

    costs = [r.cost_usd for r in results]
    cost_per_task = statistics.mean(costs)

    not_blocked = sum(1 for r in results if not r.blocked)
    evasion_rate = (not_blocked / total) * 100.0

    determinism: float | None = None
    if repeat_runs and len(repeat_runs) >= 2:
        determinism = _compute_determinism(repeat_runs)

    return {
        "total_tasks": total,
        "success_rate": round(success_rate, 2),
        "step_count_mean": round(step_count_mean, 2),
        "step_count_p95": round(step_count_p95, 2),
        "latency_p50_ms": round(latency_p50, 2),
        "latency_p95_ms": round(latency_p95, 2),
        "cost_per_task_usd": round(cost_per_task, 6),
        "anti_bot_evasion_rate": round(evasion_rate, 2),
        "determinism_score": round(determinism, 4) if determinism is not None else None,
    }


def _compute_determinism(runs: list[list[TaskResult]]) -> float:
    """Compute determinism as the fraction of tasks whose success outcome
    is identical across all provided runs.

    Args:
        runs: Two or more lists of TaskResult, each representing a complete
            benchmark run. Tasks are matched by ``task_id``.

    Returns:
        A float in [0, 1] where 1.0 means perfectly deterministic.
    """
    # Build per-task outcome vectors keyed by task_id
    outcomes: dict[str, list[bool]] = {}
    for run in runs:
        for r in run:
            outcomes.setdefault(r.task_id, []).append(r.success)

    if not outcomes:
        return 1.0

    consistent = sum(1 for ov in outcomes.values() if len(set(ov)) == 1)
    return consistent / len(outcomes)
