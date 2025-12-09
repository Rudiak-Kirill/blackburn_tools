import os
import subprocess
import sys
import tempfile
from pathlib import Path


def test_cli_list_runs(tmp_path):
    # create a temp sqlite db path
    db_file = tmp_path / "test_cli.db"
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_file}"
    # run the list command
    cmd = [sys.executable, "scripts/manage_projects.py", "list"]
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    # script should exit 0 and print something (No projects found or similar)
    assert res.returncode == 0
    assert ("No projects" in res.stdout) or ("Projects" in res.stdout) or (res.stdout.strip() == "")
