# Naming Conventions

## Task IDs

**Format:** `TASK-YYYYMMDD-NNN`

- `YYYYMMDD` — date the task was created (e.g., `20260510`)
- `NNN` — three-digit sequence number, resets each day, starting at `001`

**Example:** `TASK-20260510-001`, `TASK-20260510-002`

**How to determine the next NNN:**
1. List all entries in `logs/activity_log.md` for today's date
2. Find the highest sequence number used today
3. Increment by 1

---

## Directory Names

| Item | Pattern | Example |
|---|---|---|
| Task directory | `tasks/task_<task_id>/` | `tasks/task_TASK-20260510-001/` |
| Template directory | `templates/<template-name>/` (lowercase, hyphens) | `templates/add-alerting-profile/` |
| Jenkins pipeline dir | `jenkins/pipelines/task_<task_id>/` | `jenkins/pipelines/task_TASK-20260510-001/` |

---

## Script Names

| Script | Location | Purpose |
|---|---|---|
| `execute.py` | `tasks/task_<id>/` or `templates/<name>/` | Performs the Dynatrace API operation |
| `test.py` | `tasks/task_<id>/` | Verifies result of a specific task |
| `verify.py` | `templates/<name>/` | Reusable verification for a template |
| `metadata.json` | `tasks/task_<id>/` | Task metadata record |
| `guideline.md` | `templates/<name>/` | Template usage documentation |
| `Jenkinsfile` | `jenkins/pipelines/task_<id>/` | Jenkins declarative pipeline |

---

## Jenkins Pipeline Names

**Format:** `dthelper-<task_id>`

**Example:** `dthelper-TASK-20260510-001`

Jenkins job folder: configured under `/job/dthelper/` (see `config/environment.json`).

---

## Git Conventions

| Item | Convention | Example |
|---|---|---|
| Commit message | `[TASK-ID] brief lowercase description` | `[TASK-20260510-001] add alerting profile for payment-service` |
| Default branch | `main` | — |
| Template commit | `[TEMPLATE] add <template-name> template` | `[TEMPLATE] add alerting-profile template` |

---

## Template Names

- Lowercase letters and hyphens only
- Name should describe the operation, not the entity (e.g., `add-alerting-profile` not `alerting`)
- Use verb-noun format: `<verb>-<noun>` (e.g., `add-alerting-profile`, `update-threshold`, `disable-maintenance-window`)

---

## Environment Variable Names

All secrets must be passed via environment variables. Standard names:

| Variable | Purpose |
|---|---|
| `DT_API_TOKEN` | Dynatrace API bearer token |
| `JENKINS_USER` | Jenkins username |
| `JENKINS_TOKEN` | Jenkins API token or password |

Variable names must match exactly as defined in `config/environment.json`.
