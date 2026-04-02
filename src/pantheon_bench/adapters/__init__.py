"""Adapter registry for benchmark agents."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pantheon_bench.adapters.base import AgentAdapter


def _build_registry() -> dict[str, type["AgentAdapter"]]:
    """Build the default adapter registry from built-in adapters."""
    from pantheon_bench.adapters.example import ExampleAdapter
    from pantheon_bench.adapters.manual import ManualAdapter

    return {
        "example": ExampleAdapter,
        "manual": ManualAdapter,
    }


_REGISTRY: dict[str, type["AgentAdapter"]] | None = None


def _get_registry() -> dict[str, type["AgentAdapter"]]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return _REGISTRY


def get_adapter(name: str, **kwargs: object) -> "AgentAdapter":
    """Look up and instantiate an adapter by name.

    Args:
        name: Registered adapter name.
        **kwargs: Arguments forwarded to the adapter constructor.

    Returns:
        An instantiated AgentAdapter.

    Raises:
        KeyError: If no adapter is registered under *name*.
    """
    registry = _get_registry()
    if name not in registry:
        available = ", ".join(sorted(registry.keys()))
        raise KeyError(f"Unknown adapter '{name}'. Available adapters: {available}")
    return registry[name](**kwargs)


def register_adapter(name: str, cls: type["AgentAdapter"]) -> None:
    """Register a custom adapter class.

    Args:
        name: Name to register under.
        cls: The adapter class.
    """
    _get_registry()[name] = cls


def list_adapters() -> list[str]:
    """Return sorted list of registered adapter names."""
    return sorted(_get_registry().keys())
