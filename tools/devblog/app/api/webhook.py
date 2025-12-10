"""
GitHub Webhook endpoint
"""
import hmac
import hashlib
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Project, CommitEvent, Post
from app.core.logger import get_logger
from app.services.commit_processor import CommitProcessor
from app.core.config import settings

logger = get_logger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])


def validate_github_signature(request_body: bytes, signature: str, secret: str) -> bool:
    """
    Validate GitHub webhook signature
    X-Hub-Signature-256: sha256=<hmac>
    """
    expected_signature = hmac.new(
        secret.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    
    provided_signature = signature.split("=")[-1] if "=" in signature else ""
    
    return hmac.compare_digest(expected_signature, provided_signature)


@router.post("/github")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    GitHub push webhook handler
    Receives push events and processes commits
    """
    # Get headers
    github_event = request.headers.get("X-GitHub-Event")
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    # Only handle push events
    if github_event != "push":
        logger.info(f"Ignoring GitHub event: {github_event}")
        return {"status": "ignored"}
    
    # Get raw body for signature validation
    body = await request.body()
    
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Get repository info
    repo_full_name = payload.get("repository", {}).get("full_name")
    if not repo_full_name:
        logger.error("Missing repository full_name in payload")
        raise HTTPException(status_code=400, detail="Missing repository info")
    
    # Find project
    project = db.query(Project).filter(
        Project.repo_full_name == repo_full_name
    ).first()
    
    if not project:
        logger.warning(f"Project not found for repo: {repo_full_name}")
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Determine secret (project-level or global default)
    webhook_secret = project.github_webhook_secret or settings.GITHUB_WEBHOOK_SECRET_DEFAULT

    # Signature header must exist
    if not signature:
        logger.error(f"Missing signature header for project {project.id}")
        raise HTTPException(status_code=401, detail="Missing signature")

    # Validate signature
    # DEBUG: log signature info
    logger.info(f"DEBUG: Signature header: {signature[:20]}...")
    logger.info(f"DEBUG: Webhook secret (first 16): {webhook_secret[:16]}...")
    logger.info(f"DEBUG: Request body length: {len(body)}")
    
    if not validate_github_signature(body, signature, webhook_secret):
        # DEBUG: compute what we expect
        import hmac as hmac_module
        import hashlib
        expected_sig = hmac_module.new(webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        logger.error(f"Invalid signature. Expected: sha256={expected_sig}, Got: {signature}")
        logger.error(f"Invalid signature for project {project.id}")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    logger.info(f"Valid webhook received for project {project.id} ({repo_full_name})")
    
    # Process commits
    commits = payload.get("commits", [])
    branch = payload.get("ref", "").split("/")[-1]  # refs/heads/main -> main
    
    if not commits:
        logger.info(f"No commits in webhook for project {project.id}")
        return {"status": "no commits"}
    
    # Process using CommitProcessor
    processor = CommitProcessor(db, project)
    result = processor.process_webhook_commits(commits, branch)
    
    logger.info(f"Webhook processed for project {project.id}: {result}")
    
    return {
        "status": "success",
        "commits_received": len(commits),
        "commits_processed": result.get("processed", 0),
        "message_sent": result.get("message_sent", False)
    }
