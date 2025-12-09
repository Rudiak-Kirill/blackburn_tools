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