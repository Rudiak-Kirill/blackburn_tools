"""
Simulate GitHub webhook POST without importing app modules.
"""
import hmac
import hashlib
import json
import requests
import os

URL = "http://127.0.0.1:8000/webhook/github"
REPO_FULL_NAME = "test_owner/test_repo"
SECRET = "test-secret"

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
        }
    ],
    "pusher": {"name": "tester"}
}

body = json.dumps(payload).encode("utf-8")
sig = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
headers = {
    "X-GitHub-Event": "push",
    "X-Hub-Signature-256": f"sha256={sig}",
    "Content-Type": "application/json"
}

print(f"Posting to {URL}")
resp = requests.post(URL, headers=headers, data=body, timeout=10)
print('Status:', resp.status_code)
try:
    print('JSON:', resp.json())
except Exception:
    print('Text:', resp.text)
