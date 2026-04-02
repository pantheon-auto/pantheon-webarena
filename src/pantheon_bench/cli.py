"""Click CLI for the Pantheon WebArena benchmark harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from pantheon_bench import __version__

# Default tasks directory is <repo_root>/tasks
_DEFAULT_TASKS_DIR = Path(__file__).resolve().parent.parent.parent / "tasks"


@click.group()
@click.version_option(version=__version__, prog_name="pbench")
def cli() -> None:
    """Pantheon WebArena -- vendor-neutral benchmark harness for web agents."""


@cli.command()
@click.option(
    "--agent",
    required=True,
    help="Name of the registered agent adapter.",
)
@click.option(
    "--suite",
    required=True,
    help="Name of the task suite to run.",
)
@click.option(
    "--tasks",
    "num_tasks",
    type=int,
    default=None,
    help="Number of tasks to sample (default: all).",
)
@click.option(
    "--concurrency",
    type=int,
    default=1,
    show_default=True,
    help="Maximum number of parallel tasks.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Path to write JSON results.",
)
@click.option(
    "--tasks-dir",
    type=click.Path(exists=True),
    default=None,
    help="Root directory for task suites.",
)
@click.option(
    "--seed",
    type=int,
    default=42,
    show_default=True,
    help="Random seed for task sampling and example adapter.",
)
def run(
    agent: str,
    suite: str,
    num_tasks: int | None,
    concurrency: int,
    output: str | None,
    tasks_dir: str | None,
    seed: int,
) -> None:
    """Run a benchmark suite against an agent."""
    from pantheon_bench.adapters import get_adapter
    from pantheon_bench.reporter import Reporter
    from pantheon_bench.runner import BenchmarkRunner
    from pantheon_bench.task_loader import TaskLoader

    console = Console()

    # Resolve tasks directory
    base = Path(tasks_dir) if tasks_dir else _DEFAULT_TASKS_DIR

    loader = TaskLoader(base)
    try:
        task_list = loader.load_suite(suite, sample_n=num_tasks, seed=seed)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    if not task_list:
        console.print("[yellow]No tasks found for the given filters.[/yellow]")
        sys.exit(1)

    # Build adapter kwargs
    adapter_kwargs: dict = {}
    if agent == "example":
        adapter_kwargs["seed"] = seed

    try:
        adapter_obj = get_adapter(agent, **adapter_kwargs)
    except KeyError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    runner = BenchmarkRunner(
        adapter=adapter_obj,
        tasks=task_list,
        concurrency=concurrency,
        console=console,
    )
    payload = runner.run()

    if output:
        Reporter.to_json(payload, output)
        console.print(f"\n[green]Results written to {output}[/green]")


@cli.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default="comparison.md",
    show_default=True,
    help="Output Markdown path.",
)
def compare(file1: str, file2: str, output: str) -> None:
    """Compare two benchmark result files and generate a diff report."""
    from pantheon_bench.reporter import Reporter

    console = Console()
    Reporter.compare(file1, file2, output)
    console.print(f"[green]Comparison report written to {output}[/green]")


@cli.command("list-agents")
def list_agents() -> None:
    """List all registered agent adapters."""
    from pantheon_bench.adapters import _get_registry

    console = Console()
    registry = _get_registry()

    table = Table(title="Registered Adapters")
    table.add_column("Name", style="bold")
    table.add_column("Class")
    table.add_column("Version")

    for name in sorted(registry):
        cls = registry[name]
        table.add_row(name, f"{cls.__module__}.{cls.__name__}", cls.version)

    console.print(table)


@cli.command("list-suites")
@click.option(
    "--tasks-dir",
    type=click.Path(exists=True),
    default=None,
    help="Root directory for task suites.",
)
def list_suites(tasks_dir: str | None) -> None:
    """List available task suites."""
    from pantheon_bench.task_loader import TaskLoader

    console = Console()
    base = Path(tasks_dir) if tasks_dir else _DEFAULT_TASKS_DIR
    loader = TaskLoader(base)
    suites = loader.list_suites()

    if not suites:
        console.print("[yellow]No suites found.[/yellow]")
        return

    table = Table(title="Available Suites")
    table.add_column("Suite", style="bold")
    for s in suites:
        table.add_row(s)
    console.print(table)


if __name__ == "__main__":
    cli()
