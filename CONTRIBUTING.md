# Contributing to pantheon-webarena

Thank you for your interest in contributing. This document covers everything you need to get started.

## Development Setup

### Prerequisites

- Python 3.10 or later
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Clone and install

```bash
git clone https://github.com/pantheon-auto/pantheon-webarena.git
cd pantheon-webarena
pip install -e ".[dev]"
```

### Verify your setup

```bash
# Run the test suite
pytest

# Run linting
black --check src/ tests/
ruff check src/ tests/

# Run type checking
mypy src/
```

## Running Tests

```bash
# Full test suite
pytest

# With coverage
pytest --cov=pantheon_webarena --cov-report=term-missing

# Run a specific test file
pytest tests/test_metrics.py

# Run tests matching a pattern
pytest -k "test_success_rate"
```

## Adding an Agent Adapter

Agent adapters live in `src/pantheon_webarena/adapters/`. To add one:

1. Create a new file in `src/pantheon_webarena/adapters/` (e.g., `my_agent.py`).
2. Subclass `AgentAdapter` and implement `setup()`, `execute()`, and `teardown()`.
3. Add tests in `tests/test_adapters/`.
4. Document the adapter in `docs/adding-an-agent.md` if it ships with the repo.

See [docs/adding-an-agent.md](docs/adding-an-agent.md) for the full guide.

External agents should register via the `pantheon_webarena.agents` entry point in their own package rather than adding code to this repo.

## Adding Tasks

Tasks are JSON files in the `tasks/` directory. To add new tasks:

1. Create a JSON file following the schema in [docs/task-format.md](docs/task-format.md).
2. Place it in the appropriate suite directory under `tasks/` (or `tasks/custom/` for experimental tasks).
3. Validate the task schema: `pantheon-webarena validate-task tasks/your_task.json`
4. Run at least one agent against the task to verify it works: `pantheon-webarena run --agent example --task tasks/your_task.json`
5. Add a test in `tests/test_tasks/` that validates the task file.

### Task guidelines

- Each task must have a single, unambiguous success criterion.
- Tasks should be completable by a competent human in under 5 minutes.
- URLs should point to stable, publicly accessible pages (or use the bundled mock sites).
- Include `tags` and `difficulty` fields to help with filtering and analysis.

## Code Style

### Formatting

We use [Black](https://github.com/psf/black) with default settings (line length 88). Format your code before committing:

```bash
black src/ tests/
```

### Linting

We use [Ruff](https://github.com/astral-sh/ruff) for linting:

```bash
ruff check src/ tests/
ruff check --fix src/ tests/  # Auto-fix where possible
```

### Type hints

All public functions and methods must have type annotations. We use `mypy` for type checking:

```bash
mypy src/
```

### Docstrings

Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings):

```python
def compute_metric(results: list[TaskResult], metric: str) -> float:
    """Compute a single metric from a list of task results.

    Args:
        results: List of completed task results.
        metric: Name of the metric to compute (e.g., "success_rate").

    Returns:
        The computed metric value as a float.

    Raises:
        ValueError: If the metric name is not recognized.
    """
```

### Import ordering

Ruff handles import sorting. Standard library first, then third-party, then local imports, separated by blank lines.

## PR Process

1. **Fork and branch.** Create a feature branch from `main`. Use a descriptive name like `add-metric-determinism-score` or `fix-timeout-handling`.

2. **Make your changes.** Keep PRs focused — one logical change per PR.

3. **Write tests.** All new functionality needs tests. Bug fixes should include a regression test.

4. **Run the checks locally:**
   ```bash
   black --check src/ tests/
   ruff check src/ tests/
   pytest --cov=pantheon_webarena
   mypy src/
   ```

5. **Open a PR** against `main`. Fill out the PR template.

6. **Respond to review.** We aim to review PRs within a few days. We may ask for changes — this is normal and not a reflection on the quality of your work.

### What makes a good PR

- A clear description of what changed and why.
- Tests that cover the new behavior.
- No unrelated changes mixed in.
- Passing CI.

### What we will not merge

- Changes that break backward compatibility without discussion.
- New dependencies without justification.
- Code without tests.
- PRs that do not pass CI.

## Reporting Issues

Use the appropriate issue template:

- **Bug report** — something is broken.
- **Feature request** — you want something new.
- **Add agent** — you want to register a new agent adapter.

## Questions?

Open a discussion on GitHub or reach out in the issue tracker. There are no bad questions.
