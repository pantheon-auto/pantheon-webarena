"""Core benchmark runner that orchestrates task execution."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from pantheon_bench.adapters.base import AgentAdapter
from pantheon_bench.evaluator import ResultEvaluator, TaskResult
from pantheon_bench.metrics import compute_metrics
from pantheon_bench.task_loader import Task


class BenchmarkRunner:
    """Runs a suite of tasks against an agent adapter and collects results.

    Args:
        adapter: An instantiated AgentAdapter.
        tasks: List of Task objects to execute.
        concurrency: Maximum number of tasks to run in parallel.
            Use 1 for sequential execution.
        console: Optional Rich Console for output. Created if not provided.
    """

    def __init__(
        self,
        adapter: AgentAdapter,
        tasks: list[Task],
        concurrency: int = 1,
        console: Console | None = None,
    ) -> None:
        self.adapter = adapter
        self.tasks = tasks
        self.concurrency = max(1, concurrency)
        self.console = console or Console()
        self._results: list[TaskResult] = []
        self._warnings: list[str] = []

    def _execute_one(self, task: Task) -> tuple[TaskResult, list[str]]:
        """Run a single task and validate the result."""
        raw = self.adapter.execute_task(task.model_dump())
        result, warnings = ResultEvaluator.validate(raw)
        return result, warnings

    def run(self) -> dict[str, Any]:
        """Execute all tasks and return the full benchmark payload.

        Returns:
            Dict containing ``agent``, ``results``, ``metrics``, and
            ``warnings`` keys.
        """
        self.console.print(
            f"\n[bold]Running {len(self.tasks)} tasks with "
            f"adapter [cyan]{self.adapter.name}[/cyan] "
            f"(concurrency={self.concurrency})[/bold]\n"
        )

        self.adapter.setup()
        self._results = []
        self._warnings = []

        try:
            if self.concurrency == 1:
                self._run_sequential()
            else:
                self._run_concurrent()
        finally:
            self.adapter.teardown()

        metrics = compute_metrics(self._results)
        self._print_summary(metrics)

        return {
            "agent": {
                "name": self.adapter.name,
                "version": self.adapter.version,
            },
            "results": [r.model_dump() for r in self._results],
            "metrics": metrics,
            "warnings": self._warnings,
        }

    def _run_sequential(self) -> None:
        """Execute tasks one at a time with a progress bar."""
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            bar = progress.add_task("Tasks", total=len(self.tasks))
            for task in self.tasks:
                result, warnings = self._execute_one(task)
                self._results.append(result)
                self._warnings.extend(warnings)
                progress.advance(bar)

    def _run_concurrent(self) -> None:
        """Execute tasks with a thread pool and a progress bar."""
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            bar = progress.add_task("Tasks", total=len(self.tasks))

            with ThreadPoolExecutor(
                max_workers=self.concurrency
            ) as executor:
                futures = {
                    executor.submit(self._execute_one, t): t
                    for t in self.tasks
                }
                for future in as_completed(futures):
                    result, warnings = future.result()
                    self._results.append(result)
                    self._warnings.extend(warnings)
                    progress.advance(bar)

    def _print_summary(self, metrics: dict[str, Any]) -> None:
        """Print a summary table of key metrics."""
        table = Table(title="Benchmark Summary")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")

        table.add_row("Total Tasks", str(metrics["total_tasks"]))
        table.add_row("Success Rate", f"{metrics['success_rate']}%")
        table.add_row("Avg Steps", str(metrics["step_count_mean"]))
        table.add_row("P95 Steps", str(metrics["step_count_p95"]))
        table.add_row("P50 Latency", f"{metrics['latency_p50_ms']} ms")
        table.add_row("P95 Latency", f"{metrics['latency_p95_ms']} ms")
        table.add_row("Avg Cost/Task", f"${metrics['cost_per_task_usd']}")
        table.add_row("Evasion Rate", f"{metrics['anti_bot_evasion_rate']}%")
        if metrics["determinism_score"] is not None:
            table.add_row("Determinism", str(metrics["determinism_score"]))

        self.console.print()
        self.console.print(table)
