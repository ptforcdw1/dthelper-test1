# Template: create-metric-alert

Creates a Dynatrace metric event alert using a **static threshold** via the Settings API v2 (`builtin:anomaly-detection.metric-events`).

---

## When to Use

Use this template when the user wants to alert when any Dynatrace metric:
- Crosses a fixed numeric threshold (above or below)
- Sustained for a configurable number of minutes
- Applies to the whole environment or a specific scope

**Examples:**
- Host CPU > 90% for 10 minutes
- Host memory usage > 80% for 5 minutes
- Service error rate > 5% for 3 minutes
- Disk usage > 95% for 15 minutes

---

## Inputs

| Argument | Required | Default | Description |
|---|---|---|---|
| `--summary` | Yes | — | Unique alert name shown in Dynatrace |
| `--metric-selector` | Yes | — | DT metric selector string |
| `--threshold` | Yes | — | Numeric threshold value |
| `--alert-condition` | No | `ABOVE` | `ABOVE` or `BELOW` |
| `--duration-minutes` | No | `10` | Minutes the condition must hold before alerting |
| `--event-type` | No | `PERFORMANCE` | `PERFORMANCE`, `AVAILABILITY`, `ERROR`, `RESOURCE_CONTENTION` |
| `--event-title` | No | same as `--summary` | Title on the Davis event card |
| `--event-description` | No | auto-generated | Description on the Davis event card |
| `--scope` | No | `environment` | Settings scope — use `environment` for all hosts/services |
| `--dry-run` | No | false | Print payload without submitting |

---

## Common Metric Selectors

| Use Case | Metric Selector |
|---|---|
| Host CPU usage | `builtin:host.cpu.usage:avg:auto` |
| Host memory usage | `builtin:host.mem.usage:avg:auto` |
| Host disk usage | `builtin:host.disk.usedPct:avg:auto` |
| Service error rate | `builtin:service.errors.total.rate:avg:auto` |
| Service response time | `builtin:service.response.time:avg:auto` |
| JVM heap usage | `builtin:tech.jvm.memory.heap.used:avg:auto` |

---

## Usage in a Task

When generating a task from this template:

1. Copy `execute.py` → `tasks/task_<id>/execute.py`
2. Copy `verify.py`  → `tasks/task_<id>/test.py`
3. Pass all values as arguments in the Jenkinsfile `Execute` stage:
   ```groovy
   sh "python3 ${env.TASK_DIR}/execute.py \
       --summary 'My Alert Name' \
       --metric-selector 'builtin:host.cpu.usage:avg:auto' \
       --threshold 90 \
       --duration-minutes 10"
   ```
4. Pass `--summary` to `test.py` in the `Test` stage:
   ```groovy
   sh "python3 ${env.TASK_DIR}/test.py --summary 'My Alert Name'"
   ```
5. Record `"template_used": "create-metric-alert"` in `metadata.json`

---

## Limitations

- Only supports **static threshold** model. For anomaly-based (baseline) alerts, a different template is needed.
- `alertingScope` is always empty (applies to all entities). Scoping to specific hosts/services/tags requires extending the payload.
- `dealertingSamples` is auto-set to `max(1, duration_minutes // 2)`. Adjust manually if needed.

---

## Warnings

- `--summary` must be **unique** in the Dynatrace environment. Creating a duplicate summary overwrites the existing alert.
- Approval recommended before running on a production tenant — this creates or modifies anomaly detection rules.
