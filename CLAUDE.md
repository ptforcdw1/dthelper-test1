# DTHelper — Dynatrace Administrator Helper

## Project Overview

This project helps operate Dynatrace via its REST API. All API calls are submitted through Jenkins pipelines. The user interacts via chat; Claude acts as the orchestrator.

**Test environment:**
- Dynatrace mock tenant: `https://httpbin.org`
- Jenkins: `http://localhost:8080`
- GitHub: `https://github.com/ptforcdw1/dthelper-test1.git`

All live values are defined in `config/environment.json`. Read that file before executing any task.

---

## Orchestrator Behavior

You are the orchestrator. When the user sends a request:

1. Understand the intent (query, update, new template, etc.)
2. Check `config/template_records.md` to see if an existing template applies
3. If any required input is missing, ask the user — use human-friendly terms only (service names, cluster names, hostnames — never ask for IDs)
4. Resolve any human-readable input to Dynatrace entity IDs via the DT API before proceeding
5. Execute the appropriate workflow (Task or Template) as described below
6. After completion, update `logs/activity_log.md`

**Never ask for IDs.** If an ID is needed, resolve it automatically by querying the Dynatrace Entities API.

---

## Skill Routing

| Skill | When to Use |
|---|---|
| **dt-query** | User wants to read/list/check Dynatrace configurations or entities |
| **dt-update** | User wants to change, create, or delete a Dynatrace configuration |
| **task-create** | Any new user request that results in a new task |
| **jenkins-create** | After scripts are ready — generate Jenkinsfile and register pipeline |
| **template-create** | User explicitly asks to create a reusable template, or a new pattern is identified |
| **log-update** | After every completed task — append to activity log |

---

## Task Workflow

For every user request, follow these steps in order:

### Step 1 — Clarify Requirements
- Confirm what the user wants to do
- Identify required inputs (ask in human-friendly terms if missing)
- Resolve names to IDs via DT Entities API if needed

### Step 2 — Check Templates
- Read `config/template_records.md`
- If a matching template exists: use it to generate the task scripts
- If no template matches: write two new scripts from scratch:
  - `execute.py` — submits the Dynatrace API call(s)
  - `test.py` — verifies the result of the execution

### Step 3 — Generate Task ID
- Format: `TASK-YYYYMMDD-NNN` (e.g., `TASK-20260510-001`)
- Check existing entries in `tasks/` and `logs/activity_log.md` to determine the next sequential number for today

### Step 4 — Create Task Directory and Push to Git
- Create directory: `tasks/task_<task_id>/`
- Place scripts inside, plus a `metadata.json`
- `metadata.json` format:
  ```json
  {
    "task_id": "TASK-20260510-001",
    "description": "Brief description",
    "template_used": "template-name or null",
    "created_date": "2026-05-10",
    "requester": "user",
    "scripts": ["execute.py", "test.py"]
  }
  ```
- Commit with message: `[TASK-20260510-001] brief description`
- Push to `main` branch

### Step 5 — Create Jenkins Pipeline
- Generate `jenkins/pipelines/task_<task_id>/Jenkinsfile` using `jenkins/Jenkinsfile.template`
- The pipeline must: check out the repo, run `execute.py`, optionally run `test.py`

### Step 6 — Respond to User
- Show the user what was created (file paths, task ID, script summary)
- Tell them the Jenkins pipeline name so they can trigger it
- Wait for user confirmation before triggering

### Step 7 — Update Activity Log
- Append a new entry to `logs/activity_log.md` in the standard format

---

## Template Workflow

When creating a new reusable template:

1. Create directory: `templates/<template-name>/`
2. Write `execute.py` — fully parameterized, no hardcoded values
3. Write `verify.py` — validates the outcome
4. Write `guideline.md` — covers: purpose, inputs, usage, limitations, warnings
5. Update `config/template_records.md` with the new entry

---

## Script Requirements

All Python scripts must:
- Read configuration from `config/environment.json` (load at runtime, do not hardcode URLs or tokens)
- Accept inputs as command-line arguments (use `argparse`)
- Read secrets (API tokens, passwords) from environment variables only — never from files or arguments
- Print structured output (JSON preferred) for easy parsing by Jenkins
- Exit with code `0` on success, non-zero on failure
- Use `requests` for HTTP calls

---

## Naming Conventions

See `config/naming_conventions.md` for the full reference. Summary:

| Item | Format | Example |
|---|---|---|
| Task ID | `TASK-YYYYMMDD-NNN` | `TASK-20260510-001` |
| Task directory | `task_<task_id>` (lowercase) | `task_TASK-20260510-001` |
| Template directory | lowercase, hyphens | `add-alerting-profile` |
| Jenkins pipeline | `dthelper-<task_id>` | `dthelper-TASK-20260510-001` |
| Git commit | `[TASK-ID] description` | `[TASK-20260510-001] add alert rule` |
| Git branch | `main` (default) | — |

---

## Key Files

| File | Purpose |
|---|---|
| `config/environment.json` | All environment-specific URLs and variable names |
| `config/naming_conventions.md` | Full naming rules |
| `config/template_records.md` | Registry of all available templates |
| `logs/activity_log.md` | History of all executed tasks |
| `jenkins/Jenkinsfile.template` | Base template for all Jenkins pipelines |
