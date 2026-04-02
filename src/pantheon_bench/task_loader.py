"""Load and filter benchmark tasks from JSON files."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Task(BaseModel):
    """Schema for a single benchmark task."""

    model_config = ConfigDict(extra="allow")

    id: str
    url: str
    objective: str
    evaluation_criteria: str
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class TaskLoader:
    """Loads tasks from a directory of JSON files.

    Each JSON file should contain either a single task dict or a list of
    task dicts conforming to the ``Task`` schema.

    Args:
        base_dir: Root directory containing suite sub-directories.
    """

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)

    def _load_file(self, path: Path) -> list[Task]:
        """Parse a single JSON file into a list of Task objects."""
        with open(path, "r") as fh:
            raw = json.load(fh)
        if isinstance(raw, dict):
            raw = [raw]
        return [Task.model_validate(item) for item in raw]

    def list_suites(self) -> list[str]:
        """Return names of available task suites (sub-directories).

        Returns:
            Sorted list of suite directory names.
        """
        if not self.base_dir.exists():
            return []
        return sorted(
            d.name for d in self.base_dir.iterdir() if d.is_dir()
        )

    def load_suite(
        self,
        suite: str,
        *,
        difficulty: str | None = None,
        sample_n: int | None = None,
        seed: int | None = None,
    ) -> list[Task]:
        """Load tasks from a named suite directory.

        Args:
            suite: Name of the suite sub-directory.
            difficulty: If given, keep only tasks with this difficulty.
            sample_n: If given, randomly sample this many tasks.
            seed: Random seed used when sampling.

        Returns:
            List of Task objects.

        Raises:
            FileNotFoundError: If the suite directory does not exist.
        """
        suite_dir = self.base_dir / suite
        if not suite_dir.exists():
            raise FileNotFoundError(f"Suite directory not found: {suite_dir}")

        tasks: list[Task] = []
        for path in sorted(suite_dir.glob("*.json")):
            tasks.extend(self._load_file(path))

        if difficulty is not None:
            tasks = [t for t in tasks if t.difficulty == difficulty]

        if sample_n is not None and sample_n < len(tasks):
            rng = random.Random(seed)
            tasks = rng.sample(tasks, sample_n)

        return tasks
