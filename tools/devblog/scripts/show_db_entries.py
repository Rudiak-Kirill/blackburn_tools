"""
Show last posts and commit_events from SQLite DB for quick inspection
"""
from app.db.session import SessionLocal
from app.models import Post, CommitEvent


def show_entries(limit=10):
    db = SessionLocal()
    try:
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()
        commits = db.query(CommitEvent).order_by(CommitEvent.created_at.desc()).limit(limit).all()

        print("Posts:")
        for p in posts:
            print(f"id={p.id} project_id={p.project_id} status={p.status} msgid={p.telegram_message_id} created={p.created_at}")
            print(p.content[:300])
            print("---")

        print("Commits:")
        for c in commits:
            print(f"id={c.id} project_id={c.project_id} hash={c.commit_hash} author={c.author} pushed_at={c.pushed_at}")
            print(c.message[:200])
            print("---")
    finally:
        db.close()


if __name__ == "__main__":
    show_entries()
