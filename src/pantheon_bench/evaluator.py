"""Evaluate task results against expected criteria."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TaskResult(BaseModel):
    """Validated schema for a single task result."""

    model_config = ConfigDict(extra="allow")

    task_id: str
    success: bool
    steps: list[str] = Field(default_factory=list)
    duration_ms: float = 0.0
    cost_usd: float = 0.0
    blocked: bool = False
    error: str | None = None


_REQUIRED_KEYS = {"task_id", "success", "steps", "duration_ms", "cost_usd", "blocked"}


class ResultEvaluator:
    """Validates and normalises raw result dicts produced by adapters."""

    @staticmethod
    def validate(raw: dict) -> tuple[TaskResult, list[str]]:
        """Validate a raw result dict.

        Args:
            raw: Dict returned by an adapter's ``execute_task``.

        Returns:
            A tuple of (TaskResult, warnings) where *warnings* is a list of
            human-readable strings about missing or unexpected values.
        """
        warnings: list[str] = []

        missing = _REQUIRED_KEYS - set(raw.keys())
        if missing:
            warnings.append(f"Missing keys: {', '.join(sorted(missing))}")

        # Provide defaults for anything missing so we can still build a model
        filled = {
            "task_id": raw.get("task_id", "unknown"),
            "success": raw.get("success", False),
            "steps": raw.get("steps", []),
            "duration_ms": raw.get("duration_ms", 0.0),
            "cost_usd": raw.get("cost_usd", 0.0),
            "blocked": raw.get("blocked", False),
            "error": raw.get("error"),
        }

        if not isinstance(filled["success"], bool):
            warnings.append(
                f"'success' should be bool, got {type(filled['success']).__name__}"
            )
            filled["success"] = bool(filled["success"])

        if not isinstance(filled["steps"], list):
            warnings.append(
                f"'steps' should be list, got {type(filled['steps']).__name__}"
            )
            filled["steps"] = list(filled["steps"])

        if filled["duration_ms"] < 0:
            warnings.append("'duration_ms' is negative; clamping to 0.")
            filled["duration_ms"] = 0.0

        if filled["cost_usd"] < 0:
            warnings.append("'cost_usd' is negative; clamping to 0.")
            filled["cost_usd"] = 0.0

        result = TaskResult.model_validate(filled)
        return result, warnings

    @staticmethod
    def validate_batch(raw_list: list[dict]) -> list[TaskResult]:
        """Validate a list of raw result dicts, discarding warnings.

        Args:
            raw_list: List of raw result dicts.

        Returns:
            List of validated TaskResult objects.
        """
        return [ResultEvaluator.validate(r)[0] for r in raw_list]
