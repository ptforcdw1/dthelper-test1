# /task — Execute a New Dynatrace Task

The user has requested: **$ARGUMENTS**

Follow the 7-step task workflow defined in CLAUDE.md exactly, in order. Do not skip any step.

---

## Step 1 — Clarify Requirements

- Confirm you understand what the user wants to do.
- Identify any missing inputs (thresholds, durations, names, bucket names, etc.).
- If anything is unclear, ask now — in human-friendly terms, never ask for entity IDs.
- If inputs are complete, state what you understood and proceed.

---

## Step 2 — Check Templates

- Read `config/template_records.md`.
- If a matching template exists, read its `guideline.md` and state which template you will use.
- If no template matches, state that you will write scripts from scratch.

---

## Step 3 — Generate Task ID

- Read `logs/activity_log.md` and list the contents of `tasks/` to find the highest existing task number for today's date.
- Assign the next sequential number. Format: `TASK-YYYYMMDD-NNN` using today's date from context.

---

## Step 4 — Create Task Directory and Push to Git

- Create directory: `tasks/task_<task_id>/`
- Write `execute.py` — all inputs as argparse arguments, config loaded from `config/environment.json`, secrets from env vars only, structured JSON output, exit 0 on success.
- Write `test.py` — verifies the result of execute.py via a GET call; detects mock mode (`"httpbin.org" in tenant_url`) and passes on HTTP 200 alone when in mock mode.
- Write `metadata.json` with fields: `task_id`, `description`, `template_used`, `created_date`, `requester`, `scripts`.
- Commit with message: `[<task_id>] <brief description>`
- Push to `master` branch.

---

## Step 5 — Create Jenkins Pipeline

- Generate `jenkins/pipelines/task_<task_id>/Jenkinsfile` from `jenkins/Jenkinsfile.template`.
- Pipeline must: check out repo from `master`, run `python3 --version`, run `pip3 install requests --quiet --break-system-packages`, run `execute.py` with all required arguments, run `test.py`.
- Use `credentials('DT_API_TOKEN')` in the environment block.
- Do NOT include `archiveArtifacts` — it causes MissingContextVariableException.
- Do NOT use `${env.TASK_ID}` in post blocks — use the literal task ID string.
- Commit and push the Jenkinsfile.
- Run `jenkins/create_pipeline.ps1` to register the pipeline in Jenkins.

---

## Step 6 — Report to User and Wait for Confirmation

Tell the user:
- The task ID
- What scripts were created and what they do
- The Jenkins pipeline name (`dthelper-<task_id>`)
- The exact execute.py arguments that will be passed

**Stop here and wait for the user to confirm before triggering the build.**

---

## Step 7 — Update Activity Log

After the user confirms and the build completes, append a new entry to `logs/activity_log.md` using the standard format:

```
### <task_id> — <Brief Description>

| Field | Value |
|---|---|
| **Requester** | user |
| **Description** | ... |
| **Template Used** | ... |
| **Scripts** | execute.py, test.py |
| **Jenkins Pipeline** | dthelper-<task_id> |
| **Execution Time** | YYYY-MM-DD HH:MM UTC |
| **Result** | Success / Failed / Pending |
| **Notes** | ... |
```
