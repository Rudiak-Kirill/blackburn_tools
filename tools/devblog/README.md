# Blackburn DevBlog

This tool turns Git commits into human-friendly devlog posts and can publish them to Telegram.

Quick start (from the tool folder):

```powershell
cd tools/devblog
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Notes:
- API endpoints are available under `app/api` (FastAPI).
- Admin HTML UI is at `/admin/projects` (protected by `ADMIN_API_KEY` if set).
- CLI helper: `scripts/manage_projects.py` for local project management.

If you keep private enterprise modules, add them as submodules under `tools/devblog/enterprise/` or install from private PyPI. See `PRIVATE_MODULES.md` in the repo root.
