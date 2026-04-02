# pantheon-webarena

[![CI](https://github.com/pantheon-auto/pantheon-webarena/actions/workflows/ci.yml/badge.svg)](https://github.com/pantheon-auto/pantheon-webarena/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pantheon-webarena)](https://pypi.org/project/pantheon-webarena/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

A vendor-neutral web agent benchmark harness. Run any agent against standardized web tasks and get comparable, reproducible metrics.

---

## Why pantheon-webarena?

Web agent benchmarks are fragmented. Every team rolls their own evaluation setup: different task definitions, different success criteria, different measurement methodology. The result is a landscape where claimed numbers are impossible to compare and easy to cherry-pick.

**pantheon-webarena** fixes this by providing:

- **One harness, any agent.** Implement a single `AgentAdapter` interface and your agent plugs into the same evaluation pipeline as everyone else.
- **Standardized tasks.** A curated set of web tasks with unambiguous success criteria, drawn from real-world browsing patterns.
- **Reproducible metrics.** Every run records the same set of metrics — success rate, latency, cost, determinism — computed identically regardless of the agent under test.
- **Transparent scoring.** No hidden weighting, no private test sets. The evaluation code is the specification.

We built this because we needed it ourselves. Pantheon AI scores 81% on WebArena and we wanted a way to prove that number that anyone could audit and reproduce. We think every team building web agents should be able to do the same.

---

## Quick Start

### Installation

```bash
pip install pantheon-webarena
```

Or install from source for development:

```bash
git clone https://github.com/pantheon-auto/pantheon-webarena.git
cd pantheon-webarena
pip install -e ".[dev]"
```

### Run a benchmark

```bash
# Run the built-in example agent against the default task suite
pbench run --agent example --suite default

# Run with a specific task
pbench run --agent example --task tasks/default/search_001.json

# Run with custom output directory
pbench run --agent example --suite default --output results/my-run/

# Generate a report from results
pbench report results/my-run/
```

### Compare agents

```bash
# Run two agents and compare
pbench run --agent my-agent --suite default --output results/agent-a/
pbench run --agent other-agent --suite default --output results/agent-b/
pbench compare results/agent-a/ results/agent-b/
```

---

## Add Your Agent

Implement the `AgentAdapter` interface to plug your agent into the harness:

```python
from pantheon_bench.adapters.base import AgentAdapter


class MyAgent(AgentAdapter):
    """Adapter for my custom web agent."""

    name = "my-agent"

    def setup(self) -> None:
        """Initialize browser, models, credentials, etc."""
        self.browser = launch_my_browser()
        self.model = load_my_model()

    def execute(self, task: dict) -> AgentResult:
        """Execute a single task and return the result.

        Args:
            task: Task definition dict with 'url', 'intent', and
                'success_criteria' keys.

        Returns:
            AgentResult with the final page state and action log.
        """
        self.browser.navigate(task["url"])
        actions = self.model.plan_and_act(task["intent"])
        return AgentResult(
            success=self.check_criteria(task["success_criteria"]),
            actions=actions,
            final_url=self.browser.current_url,
        )

    def teardown(self) -> None:
        """Clean up resources."""
        self.browser.close()
```

Register it as an entry point in your `pyproject.toml`:

```toml
[project.entry-points."pantheon_bench.agents"]
my-agent = "my_package.agent:MyAgent"
```

Then run:

```bash
pbench run --agent my-agent --suite default
```

See [docs/adding-an-agent.md](docs/adding-an-agent.md) for the full guide.

---

## Metrics

Every benchmark run produces the following metrics:

| Metric | Description |
|---|---|
| `success_rate` | Fraction of tasks completed successfully (0.0 to 1.0). The primary ranking metric. |
| `step_count_mean` | Mean number of actions taken per task. Lower indicates more efficient agents. |
| `step_count_p95` | 95th percentile step count. Captures worst-case verbosity. |
| `latency_p50` | Median wall-clock time per task in seconds. |
| `latency_p95` | 95th percentile latency. Surfaces tail-latency problems. |
| `cost_per_task_usd` | Mean estimated cost per task in USD (API calls, tokens, compute). |
| `anti_bot_evasion_rate` | Fraction of tasks where the agent was not blocked by anti-bot measures. |
| `determinism_score` | Consistency of results across repeated runs of the same task (0.0 to 1.0). Computed as the fraction of tasks that produce the same success/fail outcome across N runs. |

See [docs/metrics.md](docs/metrics.md) for computation details.

---

## Task Format

Tasks are defined as JSON files with a standardized schema:

```json
{
  "id": "search_001",
  "suite": "default",
  "url": "https://www.example.com",
  "intent": "Find the price of the cheapest laptop with at least 16GB RAM",
  "success_criteria": {
    "type": "content_match",
    "expected": "$429.99"
  },
  "tags": ["search", "e-commerce"],
  "difficulty": "medium"
}
```

See [docs/task-format.md](docs/task-format.md) for the full schema specification.

---

## Leaderboard

A public leaderboard of verified benchmark results is available at:

**[https://pantheon-auto.github.io/pantheon-webarena/leaderboard](https://pantheon-auto.github.io/pantheon-webarena/leaderboard)** *(coming soon)*

To submit your results, run the benchmark with `--verify` mode and open a PR with the output:

```bash
pbench run --agent my-agent --suite default --verify --output results/my-agent/
```

---

## Project Structure

```
pantheon-webarena/
  src/pantheon_bench/        # Core library
    adapters/                # AgentAdapter base class and built-in adapters
    runner.py                # Task execution engine
    metrics.py               # Metric computation
    reporter.py              # Report generation and comparison
    evaluator.py             # Result validation
    task_loader.py           # Task file loading
    cli.py                   # pbench CLI
  tasks/                     # Task definitions
    example/                 # Example task suite
    custom/                  # User-defined tasks
  results/                   # Benchmark output (gitignored except .gitkeep)
  tests/                     # Test suite
  docs/                      # Documentation
```

---

## Built by Pantheon AI

We're a small team building web agents. We score 81% on WebArena as of early 2026, which we believe is competitive but not the point. The point is that every team claiming a number on web agent benchmarks should be able to prove it under identical conditions, and anyone should be able to verify those claims independently.

pantheon-webarena is our attempt to make that possible. We use it internally for every release, and we're open-sourcing it because fragmented benchmarks help no one.

If you find bugs, want to add tasks, or think a metric is wrong, open an issue or a PR. The goal is a benchmark the community trusts, not one we control.

---

## License

Apache 2.0. See [LICENSE](LICENSE).
