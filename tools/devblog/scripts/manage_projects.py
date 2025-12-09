"""CLI для управления Project в БД

Поддерживаемые команды:
 - list
 - show (--id or --repo)
 - create --name --repo_full_name --telegram_chat_id [--language] [--ai_enabled]
 - update --id ...
 - toggle-ai --id
 - delete --id

Пример:
 python scripts/manage_projects.py list
 python scripts/manage_projects.py create --name "My" --repo_full_name owner/repo --telegram_chat_id 12345 --ai_enabled
"""
from __future__ import annotations
import argparse
from typing import Optional

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.models import Project


def ensure_tables():
    Base.metadata.create_all(bind=engine)


def list_projects(db):
    projects = db.query(Project).order_by(Project.id).all()
    if not projects:
        print("No projects found")
        return
    for p in projects:
        print(f"[{p.id}] {p.name} | repo={p.repo_full_name} | ai_enabled={p.ai_enabled} | chat_id={p.telegram_chat_id}")


def show_project(db, id: Optional[int], repo: Optional[str]):
    q = None
    if id is not None:
        q = db.query(Project).filter(Project.id == id).first()
    elif repo:
        q = db.query(Project).filter(Project.repo_full_name == repo).first()
    else:
        print("Provide --id or --repo to show a project")
        return

    if not q:
        print("Project not found")
        return
    print(f"ID: {q.id}")
    print(f"Name: {q.name}")
    print(f"Repo: {q.repo_full_name}")
    print(f"Language: {q.language}")
    print(f"AI enabled: {q.ai_enabled}")
    print(f"Post mode: {q.post_mode}")
    print(f"Telegram chat id: {q.telegram_chat_id}")
    print(f"Telegram bot token: {'<set>' if q.telegram_bot_token else '<not set>'}")
    print(f"Created at: {q.created_at}")
    print(f"Updated at: {q.updated_at}")


def create_project(db, name: str, repo_full_name: str, telegram_chat_id: str, language: str = "ru", ai_enabled: bool = False):
    existing = db.query(Project).filter(Project.repo_full_name == repo_full_name).first()
    if existing:
        print("Project with this repo_full_name already exists")
        return
    p = Project(
        name=name,
        repo_full_name=repo_full_name,
        telegram_chat_id=telegram_chat_id,
        language=language,
        ai_enabled=ai_enabled,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    print(f"Created project [{p.id}] {p.name}")


def update_project(db, id: int, name: Optional[str], language: Optional[str], ai_enabled: Optional[bool], post_mode: Optional[str], telegram_chat_id: Optional[str], telegram_bot_token: Optional[str]):
    p = db.query(Project).filter(Project.id == id).first()
    if not p:
        print("Project not found")
        return
    changed = False
    if name is not None:
        p.name = name; changed = True
    if language is not None:
        p.language = language; changed = True
    if ai_enabled is not None:
        p.ai_enabled = ai_enabled; changed = True
    if post_mode is not None:
        p.post_mode = post_mode; changed = True
    if telegram_chat_id is not None:
        p.telegram_chat_id = telegram_chat_id; changed = True
    if telegram_bot_token is not None:
        p.telegram_bot_token = telegram_bot_token; changed = True
    if changed:
        db.add(p)
        db.commit()
        db.refresh(p)
        print(f"Updated project [{p.id}]")
    else:
        print("No updates provided")


def toggle_ai(db, id: int):
    p = db.query(Project).filter(Project.id == id).first()
    if not p:
        print("Project not found")
        return
    p.ai_enabled = not p.ai_enabled
    db.add(p)
    db.commit()
    db.refresh(p)
    print(f"Project [{p.id}] ai_enabled set to {p.ai_enabled}")


def delete_project(db, id: int):
    p = db.query(Project).filter(Project.id == id).first()
    if not p:
        print("Project not found")
        return
    db.delete(p)
    db.commit()
    print(f"Deleted project [{id}]")


def main():
    parser = argparse.ArgumentParser(description="Manage Projects")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list", help="List all projects")

    p_show = sub.add_parser("show", help="Show project by id or repo")
    p_show.add_argument("--id", type=int, help="Project id")
    p_show.add_argument("--repo", type=str, help="Repo full name (owner/repo)")

    p_create = sub.add_parser("create", help="Create project")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--repo_full_name", required=True)
    p_create.add_argument("--telegram_chat_id", required=True)
    p_create.add_argument("--language", default="ru")
    p_create.add_argument("--ai_enabled", action="store_true")

    p_update = sub.add_parser("update", help="Update project fields")
    p_update.add_argument("--id", type=int, required=True)
    p_update.add_argument("--name")
    p_update.add_argument("--language")
    p_update.add_argument("--ai_enabled", type=lambda v: v.lower() in ("1","true","yes"), nargs="?", const=True)
    p_update.add_argument("--post_mode")
    p_update.add_argument("--telegram_chat_id")
    p_update.add_argument("--telegram_bot_token")

    p_toggle = sub.add_parser("toggle-ai", help="Toggle ai_enabled for project")
    p_toggle.add_argument("--id", type=int, required=True)

    p_delete = sub.add_parser("delete", help="Delete project")
    p_delete.add_argument("--id", type=int, required=True)

    args = parser.parse_args()

    ensure_tables()
    db = SessionLocal()
    try:
        if args.cmd == "list":
            list_projects(db)
        elif args.cmd == "show":
            show_project(db, getattr(args, "id", None), getattr(args, "repo", None))
        elif args.cmd == "create":
            create_project(db, args.name, args.repo_full_name, args.telegram_chat_id, args.language, args.ai_enabled)
        elif args.cmd == "update":
            update_project(db, args.id, args.name, args.language, args.ai_enabled, args.post_mode, args.telegram_chat_id, args.telegram_bot_token)
        elif args.cmd == "toggle-ai":
            toggle_ai(db, args.id)
        elif args.cmd == "delete":
            delete_project(db, args.id)
        else:
            parser.print_help()
    finally:
        db.close()


if __name__ == "__main__":
    main()
