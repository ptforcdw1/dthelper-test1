# /status — Show Current Project State

Give the user a concise snapshot of where things stand. Read the following files and summarize.

---

## 1. Recent Tasks (activity_log.md)

Read `logs/activity_log.md` and show the last 5 task entries in a compact table:

| Task ID | Description | Template | Result |
|---|---|---|---|
| ... | ... | ... | ... |

---

## 2. Available Templates (template_records.md)

Read `config/template_records.md` and list all templates in a table:

| Template | Use Case | Approval Required |
|---|---|---|
| ... | ... | ... |

---

## 3. Next Task ID

- Check today's date from context.
- Scan `logs/activity_log.md` and `tasks/` for the highest task number used today.
- State what the next task ID will be (e.g., `TASK-20260510-004`).

---

## 4. Summary Line

End with one sentence: how many tasks have been run, how many templates exist, and whether anything needs follow-up (e.g., a pending build result, a task marked as Failed).
