# Template: route-logs-to-bucket

Creates a Dynatrace log storage rule via Settings API v2 (`builtin:logmonitoring.log-storage-settings`) that routes logs matching a specified attribute and value to a Grail bucket.

---

## When to Use

Use this template when the user wants to route logs to a specific Grail bucket based on any log attribute — such as k8s namespace, pod name, deployment name, or custom log attribute.

**Examples:**
- Route logs from k8s namespace `payment-ns` to bucket `payment-logs`
- Route logs from k8s deployment `frontend` to bucket `frontend-logs`
- Route logs from host group `prod-hosts` to bucket `prod-bucket`
- Route logs where `log.source` contains `nginx` to bucket `nginx-logs`

---

## Inputs

| Argument | Required | Default | Description |
|---|---|---|---|
| `--bucket-name` | Yes | — | Dynatrace Grail bucket name (must already exist) |
| `--matcher-attribute` | Yes | — | Log attribute to filter on |
| `--matcher-value` | Yes | — | Value to match against the attribute |
| `--matcher-operator` | No | `EQUALS` | `EQUALS`, `CONTAINS`, or `STARTS_WITH` |
| `--rule-name` | No | auto-generated | Display name for the rule in Dynatrace |
| `--dry-run` | No | false | Print payload without submitting |

---

## Common Matcher Attributes

| Use Case | Matcher Attribute |
|---|---|
| Kubernetes namespace | `k8s.namespace.name` |
| Kubernetes pod name | `k8s.pod.name` |
| Kubernetes deployment | `k8s.deployment.name` |
| Kubernetes cluster | `k8s.cluster.name` |
| Host name | `host.name` |
| Log source / file path | `log.source` |
| Custom attribute | any OpenTelemetry or DT attribute key |

---

## Usage in a Task

When generating a task from this template:

1. Copy `execute.py` → `tasks/task_<id>/execute.py`
2. Copy `verify.py`  → `tasks/task_<id>/test.py`
3. Pass values in the Jenkinsfile `Execute` stage:
   ```groovy
   sh """python3 ${env.TASK_DIR}/execute.py \
       --bucket-name 'my-bucket' \
       --matcher-attribute 'k8s.namespace.name' \
       --matcher-value 'my-namespace'"""
   ```
4. Pass `--matcher-value` to `test.py` in the `Test` stage:
   ```groovy
   sh "python3 ${env.TASK_DIR}/test.py --matcher-value 'my-namespace'"
   ```
5. Record `"template_used": "route-logs-to-bucket"` in `metadata.json`

---

## Limitations

- Only supports a **single matcher** per rule. Multiple matchers require extending the payload.
- The Grail bucket (`--bucket-name`) must already exist in Dynatrace before this rule is applied.
- Rule ordering is managed by Dynatrace — this template always appends the new rule at the end of the list.

---

## Warnings

- Approval recommended before running on a production tenant — log routing rules affect where logs are stored and may impact retention and cost.
- A misconfigured rule (wrong bucket name) will silently drop logs if the bucket does not exist.
