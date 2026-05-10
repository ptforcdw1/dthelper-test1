# Task Activity Log

This file records all tasks that have been executed. Append a new entry after each completed task. Do not edit past entries.

---

## Log Format

Each entry uses the following structure:

```
### TASK-YYYYMMDD-NNN — Brief Description

| Field | Value |
|---|---|
| **Requester** | (name or "user") |
| **Description** | (what was requested) |
| **Template Used** | (template name, or "none") |
| **Scripts** | (comma-separated list of script filenames) |
| **Jenkins Pipeline** | (pipeline name, e.g., dthelper-TASK-20260510-001) |
| **Execution Time** | (YYYY-MM-DD HH:MM UTC) |
| **Result** | (Success / Failed / Pending) |
| **Notes** | (optional — errors, warnings, follow-up) |
```

---

## Entries

### TASK-20260510-001 — Create host CPU >90% alert for 10 minutes

| Field | Value |
|---|---|
| **Requester** | user |
| **Description** | Create Dynatrace metric event alert: host CPU usage > 90% sustained for 10 minutes, applies to all hosts |
| **Template Used** | none |
| **Scripts** | execute.py, test.py |
| **Jenkins Pipeline** | dthelper-TASK-20260510-001 |
| **Execution Time** | 2026-05-10 10:45 UTC |
| **Result** | Success |
| **Notes** | Uses Settings API v2, schema builtin:anomaly-detection.metric-events. Mock endpoint (httpbin.org). Build #9 passed — execute and test stages both successful. |
