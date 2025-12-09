# Blackburn DevBlog

Этот инструмент превращает Git-коммиты в удобочитаемые посты для devlog и может публиковать их в Telegram.

Быстрый старт (из папки инструмента):

```powershell
cd tools/devblog
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Примечания:
- API доступен в `app/api` (FastAPI).
- HTML-админка доступна по `/admin/projects` (защищается `ADMIN_API_KEY`, если задан).
- Для управления проектами локально можно использовать CLI-утилиту: `scripts/manage_projects.py`.

Если вы используете приватные enterprise-модули, добавляйте их как submodule в `tools/devblog/enterprise/` или устанавливайте из приватного PyPI. См. `PRIVATE_MODULES.md` в корне репозитория.
