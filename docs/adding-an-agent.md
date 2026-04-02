# Adding an Agent Adapter

This guide walks you through adding your web agent to pantheon-webarena.

## 1. Create the adapter file

Create `src/pantheon_bench/adapters/your_agent.py`:

```python
from pantheon_bench.adapters.base import AgentAdapter


class YourAgent(AgentAdapter):
    name = "your-agent"
    version = "0.1.0"

    def setup(self) -> None:
        """Initialize your agent — load models, start browser, etc."""
        # self.client = YourAgentClient(api_key=os.environ["YOUR_API_KEY"])
        pass

    def execute_task(self, task: dict) -> dict:
        """
        Execute a single benchmark task.

        Args:
            task: dict with keys:
                - id (str): Unique task identifier
                - url (str): Starting URL for the task
                - objective (str): What the agent should accomplish
                - evaluation_criteria (str): How success is determined
                - difficulty (str): "easy", "medium", or "hard"

        Returns:
            dict with keys:
                - success (bool): Whether the task was completed
                - steps (list[dict]): Actions taken, each with 'action' and 'detail'
                - duration_ms (int): Wall-clock time in milliseconds
                - cost_usd (float | None): API/compute cost, or None if unknown
                - blocked (bool, optional): True if blocked by anti-bot
        """
        import time

        start = time.time()
        # result = self.client.run(url=task["url"], objective=task["objective"])
        duration = int((time.time() - start) * 1000)

        return {
            "success": True,  # or False
            "steps": [{"action": "navigate", "detail": task["url"]}],
            "duration_ms": duration,
            "cost_usd": 0.01,
        }

    def teardown(self) -> None:
        """Clean up resources."""
        pass
```

## 2. Register the adapter

In `src/pantheon_bench/adapters/__init__.py`, add:

```python
from pantheon_bench.adapters.your_agent import YourAgent
register_adapter(YourAgent)
```

## 3. Add tests

Create `tests/test_adapters/test_your_agent.py`:

```python
from pantheon_bench.adapters.your_agent import YourAgent

def test_your_agent_metadata():
    agent = YourAgent()
    assert agent.name == "your-agent"
    assert agent.version

def test_your_agent_runs_task():
    agent = YourAgent()
    agent.setup()
    result = agent.execute_task({
        "id": "test-1",
        "url": "https://example.com",
        "objective": "Click the first link",
        "evaluation_criteria": "A link was clicked",
        "difficulty": "easy",
    })
    assert isinstance(result["success"], bool)
    assert isinstance(result["steps"], list)
    assert isinstance(result["duration_ms"], int)
    agent.teardown()
```

## 4. Run the benchmark

```bash
pbench run --agent your-agent --suite example --tasks 5 --output results/your-agent.json
```

## 5. Submit a PR

- Include the adapter, tests, and any docs updates
- CI will run lint + tests automatically
