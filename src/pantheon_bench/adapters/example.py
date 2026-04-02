"""Example adapter that simulates random success/failure.

Useful for testing the harness without a real agent.
"""

from __future__ import annotations

import random
import time

from pantheon_bench.adapters.base import AgentAdapter


class ExampleAdapter(AgentAdapter):
    """Simulated agent that randomly succeeds or fails each task."""

    name: str = "example"
    version: str = "0.1.0"

    def __init__(
        self,
        success_rate: float = 0.6,
        min_steps: int = 2,
        max_steps: int = 8,
        min_delay_ms: float = 50.0,
        max_delay_ms: float = 300.0,
        seed: int | None = None,
    ) -> None:
        self.success_rate = success_rate
        self.min_steps = min_steps
        self.max_steps = max_steps
        self.min_delay_ms = min_delay_ms
        self.max_delay_ms = max_delay_ms
        self._rng = random.Random(seed)

    def setup(self) -> None:
        """No-op for the example adapter."""

    def execute_task(self, task: dict) -> dict:
        """Simulate executing a task with random outcomes.

        Args:
            task: Task dict with at least an ``id`` key.

        Returns:
            Simulated result dict.
        """
        num_steps = self._rng.randint(self.min_steps, self.max_steps)
        steps = [f"step_{i}" for i in range(1, num_steps + 1)]

        delay_ms = self._rng.uniform(self.min_delay_ms, self.max_delay_ms)
        time.sleep(delay_ms / 1000.0)

        success = self._rng.random() < self.success_rate
        blocked = self._rng.random() < 0.1  # 10 % chance of being blocked

        if blocked:
            success = False

        cost_usd = self._rng.uniform(0.001, 0.02)

        return {
            "task_id": task.get("id", "unknown"),
            "success": success,
            "steps": steps,
            "duration_ms": delay_ms,
            "cost_usd": round(cost_usd, 6),
            "blocked": blocked,
        }

    def teardown(self) -> None:
        """No-op for the example adapter."""
