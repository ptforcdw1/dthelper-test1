# Template Records

This file is the registry of all reusable task templates. Update it whenever a new template is created.

---

## Template List

| Template Name | Directory | Use Case | Approval Required | Created Date |
|---|---|---|---|---|
| create-metric-alert | `templates/create-metric-alert/` | Create a static-threshold metric event alert for any DT metric (CPU, memory, error rate, etc.) | No | 2026-05-10 |
| route-logs-to-bucket | `templates/route-logs-to-bucket/` | Route logs matching any attribute/value (e.g. k8s namespace, pod, deployment) to a Grail bucket | Yes | 2026-05-10 |

---

## Field Descriptions

| Field | Description |
|---|---|
| **Template Name** | Human-readable name of the template |
| **Directory** | Path under `templates/` (e.g., `templates/add-alerting-profile/`) |
| **Use Case** | One-sentence description of when to use this template |
| **Approval Required** | `Yes` or `No` — whether this template requires human approval before execution |
| **Created Date** | Date the template was added (YYYY-MM-DD) |

---

## How to Use This Registry

Before creating scripts for a new task:
1. Scan this table for a template that matches the requested operation
2. If a match is found, read the template's `guideline.md` for usage instructions
3. Use the template's `execute.py` and `verify.py` as the basis for the task scripts
4. Record the template name used in the task's `metadata.json`

If no template matches, create the scripts from scratch. If the new scripts represent a reusable pattern, create a new template following the Template Workflow in `CLAUDE.md`.
