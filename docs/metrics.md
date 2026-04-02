# Metrics

pantheon-webarena computes the following metrics from benchmark results.

## Core metrics

### `success_rate`
Percentage of tasks completed successfully. The primary comparison metric.

**Formula:** `(successful_tasks / total_tasks) * 100`

### `step_count_mean`
Average number of actions taken per task. Fewer steps indicates better agent planning and efficiency.

**Formula:** Mean of `len(result.steps)` across all tasks.

### `step_count_p95`
95th percentile step count. Captures worst-case agent behavior — how many steps does the agent need for its hardest tasks?

### `latency_p50_ms`
Median task completion time in milliseconds. Reflects typical performance.

### `latency_p95_ms`
95th percentile completion time. Captures tail latency — important for production use where SLAs matter.

## Cost and reliability metrics

### `cost_per_task_usd`
Average dollar cost per task. Includes API calls, compute, and any external service fees.

Reported by the adapter via the `cost_usd` field in task results. Tasks reporting `null` cost are excluded from the average.

### `anti_bot_evasion_rate`
Percentage of tasks where the agent was **not** blocked by anti-bot systems (Cloudflare, Akamai, PerimeterX, etc.).

**Formula:** `(tasks_not_blocked / total_tasks) * 100`

A task is considered blocked if the result includes `"blocked": true`.

### `determinism_score`
When the same task is run multiple times, what percentage produce identical success/failure outcomes?

**Formula:** For each task run N times, check if all runs agree on `success`. The score is `(agreeing_tasks / total_tasks) * 100`.

Requires multiple runs of the same task set. Only computed when duplicate task IDs are present in results.

## Interpreting results

| Agent Type | Likely Strengths | Likely Weaknesses |
|-----------|-----------------|-------------------|
| Screenshot-based (GPT-4V, etc.) | High success on visual tasks | High cost, high latency, low determinism |
| API/network-level (Pantheon, etc.) | Low cost, low latency, high determinism | Requires per-site recording |
| Browser automation (Selenium, etc.) | Wide compatibility | Low anti-bot evasion, moderate success |
