"""
Simulate GitHub push webhook to local /webhook/github endpoint.
Computes X-Hub-Signature-256 header using project's secret.
"""
import hmac
import hashlib
import json
import requests
from app.core.config import settings

# Configuration
URL = "http://localhost:8000/webhook/github"
REPO_FULL_NAME = "test_owner/test_repo"
SECRET = settings.GITHUB_WEBHOOK_SECRET_DEFAULT or "test-secret"

# Example payload (simplified)
payload = {
    "ref": "refs/heads/main",
    "repository": {"full_name": REPO_FULL_NAME},
    "commits": [
        {
            "id": "abc123def456",
            "message": "feat: Add simulated webhook test",
            "timestamp": "2025-12-09T10:00:00Z",
            "author": {"name": "Tester"},
            "url": "https://github.com/test_owner/test_repo/commit/abc123"
        },
        {
            "id": "def789ghi012",
            "message": "fix: Correct minor bug",
            "timestamp": "2025-12-09T10:05:00Z",
            "author": {"name": "Tester"},
            "url": "https://github.com/test_owner/test_repo/commit/def789"
        }
    ],
    "pusher": {"name": "tester"}
}

body = json.dumps(payload).encode("utf-8")

# Compute signature
sig = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
headers = {
    "X-GitHub-Event": "push",
    "X-Hub-Signature-256": f"sha256={sig}",
    "Content-Type": "application/json"
}

print(f"Posting to {URL} with repo {REPO_FULL_NAME} using secret={SECRET}")
resp = requests.post(URL, headers=headers, data=body, timeout=10)
print("Status:", resp.status_code)
try:
    print("Response:", resp.json())
except Exception:
    print("Response text:", resp.text)
