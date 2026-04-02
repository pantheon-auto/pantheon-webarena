# Task Format

Tasks are stored as JSON arrays. Each task suite is a directory under `tasks/` containing one or more `.json` files.

## Schema

```json
[
  {
    "id": "unique-task-id",
    "url": "https://example.com/start-page",
    "objective": "What the agent should accomplish",
    "evaluation_criteria": "How to determine success",
    "difficulty": "easy"
  }
]
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for the task |
| `url` | string | Yes | Starting URL the agent navigates to |
| `objective` | string | Yes | Plain-language description of the goal |
| `evaluation_criteria` | string | Yes | How success is evaluated |
| `difficulty` | string | No | `"easy"`, `"medium"`, or `"hard"`. Defaults to `"medium"` |

### Difficulty levels

- **easy** — Single page, one action (click, fill, navigate)
- **medium** — Multi-step, 2-5 actions across 1-3 pages
- **hard** — Complex workflows, authentication, dynamic content, anti-bot

## Example

```json
[
  {
    "id": "search-product",
    "url": "https://store.example.com",
    "objective": "Search for 'wireless keyboard' and add the first result to cart",
    "evaluation_criteria": "Cart contains at least one wireless keyboard",
    "difficulty": "medium"
  }
]
```

## Adding a task suite

1. Create a directory: `tasks/your_suite/`
2. Add one or more `.json` files following the schema above
3. Minimum 10 tasks per suite
4. Each task should have a manually verified expected outcome
5. Submit a PR with the `new-tasks` label
