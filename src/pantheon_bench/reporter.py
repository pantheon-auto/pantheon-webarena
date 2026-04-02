"""Generate JSON and Markdown reports from benchmark results."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Reporter:
    """Generates reports from benchmark payloads.

    A payload is the dict returned by ``BenchmarkRunner.run()`` containing
    ``agent``, ``results``, ``metrics``, and ``warnings`` keys.
    """

    @staticmethod
    def to_json(payload: dict[str, Any], path: str | Path) -> None:
        """Write the full payload as pretty-printed JSON.

        Args:
            payload: Benchmark result payload.
            path: Output file path.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            json.dump(payload, fh, indent=2, default=str)

    @staticmethod
    def to_markdown(payload: dict[str, Any], path: str | Path) -> None:
        """Write a Markdown summary report.

        Args:
            payload: Benchmark result payload.
            path: Output file path.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        metrics = payload.get("metrics", {})
        agent = payload.get("agent", {})
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        lines: list[str] = [
            f"# Benchmark Report",
            "",
            f"**Agent:** {agent.get('name', 'unknown')} v{agent.get('version', '?')}",
            f"**Date:** {timestamp}",
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Total Tasks | {metrics.get('total_tasks', 0)} |",
            f"| Success Rate | {metrics.get('success_rate', 0)}% |",
            f"| Avg Steps | {metrics.get('step_count_mean', 0)} |",
            f"| P95 Steps | {metrics.get('step_count_p95', 0)} |",
            f"| P50 Latency | {metrics.get('latency_p50_ms', 0)} ms |",
            f"| P95 Latency | {metrics.get('latency_p95_ms', 0)} ms |",
            f"| Avg Cost/Task | ${metrics.get('cost_per_task_usd', 0)} |",
            f"| Evasion Rate | {metrics.get('anti_bot_evasion_rate', 0)}% |",
        ]

        det = metrics.get("determinism_score")
        if det is not None:
            lines.append(f"| Determinism | {det} |")

        lines.append("")

        # Per-task results table
        results = payload.get("results", [])
        if results:
            lines.extend(
                [
                    "## Per-Task Results",
                    "",
                    "| Task ID | Success | Steps | Latency (ms) | Cost (USD) | Blocked |",
                    "| --- | :---: | ---: | ---: | ---: | :---: |",
                ]
            )
            for r in results:
                ok = "Y" if r.get("success") else "N"
                blocked = "Y" if r.get("blocked") else "N"
                lines.append(
                    f"| {r.get('task_id', '?')} | {ok} "
                    f"| {len(r.get('steps', []))} "
                    f"| {r.get('duration_ms', 0)} "
                    f"| {r.get('cost_usd', 0)} "
                    f"| {blocked} |"
                )
            lines.append("")

        warnings = payload.get("warnings", [])
        if warnings:
            lines.extend(["## Warnings", ""])
            for w in warnings:
                lines.append(f"- {w}")
            lines.append("")

        path.write_text("\n".join(lines))

    @staticmethod
    def compare(
        file_a: str | Path,
        file_b: str | Path,
        output: str | Path,
    ) -> None:
        """Generate a Markdown diff report comparing two result files.

        Args:
            file_a: Path to first results JSON.
            file_b: Path to second results JSON.
            output: Path to write the comparison Markdown.
        """
        with open(file_a) as fh:
            payload_a = json.load(fh)
        with open(file_b) as fh:
            payload_b = json.load(fh)

        ma = payload_a.get("metrics", {})
        mb = payload_b.get("metrics", {})
        agent_a = payload_a.get("agent", {}).get("name", "A")
        agent_b = payload_b.get("agent", {}).get("name", "B")

        metric_keys = [
            ("Success Rate", "success_rate", "%"),
            ("Avg Steps", "step_count_mean", ""),
            ("P95 Steps", "step_count_p95", ""),
            ("P50 Latency", "latency_p50_ms", " ms"),
            ("P95 Latency", "latency_p95_ms", " ms"),
            ("Avg Cost/Task", "cost_per_task_usd", " USD"),
            ("Evasion Rate", "anti_bot_evasion_rate", "%"),
        ]

        lines: list[str] = [
            "# Comparison Report",
            "",
            f"Comparing **{agent_a}** vs **{agent_b}**",
            "",
            f"| Metric | {agent_a} | {agent_b} | Delta |",
            "| --- | ---: | ---: | ---: |",
        ]

        for label, key, suffix in metric_keys:
            va = ma.get(key, 0)
            vb = mb.get(key, 0)
            try:
                delta = round(float(vb) - float(va), 4)
                delta_s = f"{'+' if delta >= 0 else ''}{delta}{suffix}"
            except (TypeError, ValueError):
                delta_s = "N/A"
            lines.append(
                f"| {label} | {va}{suffix} | {vb}{suffix} | {delta_s} |"
            )

        lines.append("")
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text("\n".join(lines))
