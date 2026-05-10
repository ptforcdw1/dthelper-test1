# Templates

Templates are reusable, fully parameterized script pairs that cover common Dynatrace operations. Use a template instead of writing from scratch whenever the operation pattern matches.

---

## Directory Structure

Each template lives in its own subdirectory:

```
templates/
└── <template-name>/
    ├── execute.py      ← Performs the Dynatrace API operation
    ├── verify.py       ← Verifies the operation completed successfully
    └── guideline.md    ← Usage, inputs, limitations, warnings
```

---

## Using a Template

1. Check `config/template_records.md` to find the right template
2. Read the template's `guideline.md` before using it
3. Copy `execute.py` and `verify.py` into the new task directory (`tasks/task_<id>/`)
4. Rename `verify.py` → `test.py` for the task copy
5. Pass all required inputs as command-line arguments (see `guideline.md` for the argument list)
6. Record `template_used` in the task's `metadata.json`

**Do not modify the original template files.** The task directory holds the task-specific copy.

---

## Creating a New Template

A template is worth creating when:
- The same type of operation is likely to be requested again
- The API call pattern is well-defined and can be fully parameterized
- No hardcoded values are needed (all values come from arguments or environment variables)

Follow the Template Workflow defined in `CLAUDE.md`:
1. Create `templates/<template-name>/`
2. Write `execute.py` and `verify.py` (fully parameterized via `argparse`)
3. Write `guideline.md`
4. Add an entry to `config/template_records.md`

---

## Script Requirements for Templates

- All inputs via `argparse` — no hardcoded entity names, IDs, or values
- Secrets via environment variables only (see `config/naming_conventions.md`)
- Load `config/environment.json` at runtime for base URLs
- Print JSON output to stdout
- Exit `0` on success, non-zero on failure
- Include `--dry-run` flag where meaningful (prints payload without submitting)
