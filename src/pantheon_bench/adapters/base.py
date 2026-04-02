"""Abstract base class for agent adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod


class AgentAdapter(ABC):
    """Base class that every agent adapter must implement.

    Subclasses declare a ``name`` and ``version``, then implement the three
    lifecycle hooks: ``setup``, ``execute_task``, and ``teardown``.
    """

    name: str = "base"
    version: str = "0.0.0"

    @abstractmethod
    def setup(self) -> None:
        """Prepare the adapter (launch browser, authenticate, etc.)."""

    @abstractmethod
    def execute_task(self, task: dict) -> dict:
        """Execute a single benchmark task.

        Args:
            task: A dict matching the Task schema (id, url, objective, ...).

        Returns:
            A result dict with at least:
                - success (bool)
                - steps (list[str])
                - duration_ms (float)
                - cost_usd (float)
                - blocked (bool)
        """

    @abstractmethod
    def teardown(self) -> None:
        """Clean up resources held by the adapter."""
