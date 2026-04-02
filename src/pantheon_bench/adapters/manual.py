"""Manual adapter that replays pre-recorded results from a JSON file.

This is useful for benchmarking against published numbers or replaying
previously captured agent runs.
"""

from __future__ import annotations

import json
from pathlib import Path

from pantheon_bench.adapters.base import AgentAdapter


class ManualAdapter(AgentAdapter):
    """Adapter that returns pre-recorded results loaded from a JSON file.

    The JSON file should contain a list of result dicts, each with at least
    a ``task_id`` key that matches the task's ``id``.
    """

    name: str = "manual"
    version: str = "0.1.0"

    def __init__(self, results_file: str | Path | None = None) -> None:
        self._results_file = Path(results_file) if results_file else None
        self._results_by_id: dict[str, dict] = {}

    def setup(self) -> None:
        """Load pre-recorded results from the JSON file."""
        if self._results_file is None:
            return
        if not self._results_file.exists():
            raise FileNotFoundError(
                f"Results file not found: {self._results_file}"
            )
        with open(self._results_file, "r") as fh:
            records = json.load(fh)
        if not isinstance(records, list):
            raise ValueError("Results file must contain a JSON array.")
        for record in records:
            tid = record.get("task_id", record.get("id"))
            if tid is not None:
                self._results_by_id[str(tid)] = record

    def execute_task(self, task: dict) -> dict:
        """Return the pre-recorded result for a given task.

        Args:
            task: Task dict containing an ``id`` field.

        Returns:
            The recorded result dict, or a failure stub if no recording
            exists for this task.
        """
        task_id = str(task.get("id", ""))
        if task_id in self._results_by_id:
            return self._results_by_id[task_id]
        return {
            "task_id": task_id,
            "success": False,
            "steps": [],
            "duration_ms": 0.0,
            "cost_usd": 0.0,
            "blocked": False,
            "error": "No pre-recorded result for this task.",
        }

    def teardown(self) -> None:
        """Release loaded data."""
        self._results_by_id.clear()
