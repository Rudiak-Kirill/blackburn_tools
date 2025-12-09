# AGENTS / TOOLS GUIDELINES

This document describes how to create and structure new tools/agents inside the `blackburn_tools` monorepo.

General principles
- Each tool lives under `tools/<tool_name>/` and should be as self-contained as possible.
- Minimum for each tool:
  - `README.md` — what it does and how to run it
  - `requirements.txt` — Python deps for that tool
  - `app/` or `src/` — codebase (FastAPI app, scripts, etc.)
  - `scripts/` — helper scripts (CLI, init, migrations)
  - `tests/` — unit / integration tests
  - `main.py` — optional entrypoint to run the tool directly

Shared utilities
- Common utilities (logging, shared config, helpers) may be extracted to `blackburn_core/` in the future.

# AGENTS / TOOLS GUIDELINES

This document describes how to create and structure new tools/agents inside the `blackburn_tools` monorepo.

General principles
- Each tool lives under `tools/<tool_name>/` and should be as self-contained as possible.
- Minimum for each tool:
  - `README.md` — what it does and how to run it
  - `requirements.txt` — Python deps for that tool
  - `app/` or `src/` — codebase (FastAPI app, scripts, etc.)
  - `scripts/` — helper scripts (CLI, init, migrations)
  - `tests/` — unit / integration tests
  - `main.py` — optional entrypoint to run the tool directly

Shared utilities
- Common utilities (logging, shared config, helpers) may be extracted to `blackburn_core/` in the future.

Tool lifecycle
- Use `docs/tool_template.md` when creating a new tool to fill in required README sections.
- Keep the public repo free from private enterprise code — use `PRIVATE_MODULES.md` patterns for private extensions.

CI / test requirements
- Each tool should provide tests and, when possible, a lightweight `pytest` suite so root CI can validate it.

Security and secrets
- Never store secrets in a tool's repository. Use environment variables, secret managers, or private modules.

Example layout

```
tools/my_tool/
├─ README.md
├─ requirements.txt
├─ app/
├─ scripts/
├─ tests/
└─ main.py
```

If you need help creating a new tool scaffold, follow `docs/tool_template.md` and copy `tools/devblog/` as a working example.

Cursor / Agent file-editing rules
---------------------------------

These rules describe how the interactive agent named "Cursor" (an editing assistant) is allowed to create, modify, and remove files inside this repository. They are designed to enable fast iteration while keeping safety and traceability.

- Scope: Cursor may create, edit, and delete files anywhere under the repository root while working on tasks assigned by a human maintainer. Typical targets include code under `tools/`, documentation, scripts, tests, and CI config. Cursor should avoid modifying files outside of code and docs (e.g., `LICENSE`, `SECURITY.md`, or legal/ownership files) unless explicitly requested.
- Idempotence: Changes should be as minimal as possible and idempotent. Prefer small, focused edits and avoid large-scale unrelated refactors.
- Auditing: Every change must be accompanied by a concise commit message and (when applicable) an entry in the task tracking / TODO list. Cursor will use the repository's git history for traceability.
- Safety checks: Before editing files that affect secrets, CI, or deployment (e.g., `.github/workflows/*`, `.env.example`, deployment scripts), Cursor will:
  - Prefer to add tests or validation steps for the change.
  - Never insert real secrets into repository files; use placeholders and document required env vars.
- Backups: For destructive edits (history rewrite, deleting large folders), Cursor will create a backup (bundle or branch) and notify the maintainer prior to pushing.
- Human-in-the-loop: For changes that are potentially disruptive (database migrations, major API changes, history rewrite, license changes), Cursor will ask for explicit approval before pushing to `main`.
- Testing: When adding or changing runtime code, Cursor will run local tests or a quick verification command where possible, and report results. If tests do not exist, Cursor will add minimal smoke tests if reasonable.
- Communication: Cursor will include a brief preamble before making edits explaining what will be changed and why; after edits it will summarize what changed and next steps.

Examples
--------

- Adding a bootstrap script: allowed. Cursor will create the script under `tools/<tool>/scripts/`, add a small README note, and optionally add a smoke test.
- Updating content generation template: allowed. Cursor will edit only the generator file and README examples, then run a quick local simulation if possible.
- Rewriting git history: disallowed without explicit approval. Cursor will instead propose the steps and ask the maintainer to run them or approve the operation.

These rules allow Cursor to operate efficiently while preserving repository safety and maintainers' control.