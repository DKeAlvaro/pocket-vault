import subprocess
import os
from pathlib import Path

VAULT_DIR = Path.home() / ".pocket-vault"
CONFIG_DIR = Path.home() / ".config" / "pocket-vault"
TOKEN_FILE = CONFIG_DIR / "token"
REPO_FILE = CONFIG_DIR / "repo"


def get_remote_url():
    """Get the remote URL of the vault repo."""
    if not VAULT_DIR.exists():
        return None
    result = run_git("remote", "get-url", "origin")
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def run_git(*args, cwd=None):
    """Run a git command and return output."""
    cwd = cwd or VAULT_DIR
    result = subprocess.run(
        ["git"] + list(args),
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result


def clone_repo(repo_url):
    """Clone a git repo to the vault directory."""
    if VAULT_DIR.exists():
        return True, "Vault already exists"

    result = run_git("clone", repo_url, str(VAULT_DIR), cwd=Path.home())
    if result.returncode != 0:
        stderr = result.stderr.lower()
        if "authentication failed" in stderr or "could not read username" in stderr:
            return False, "Git authentication failed. Your token may be invalid or expired."
        elif "repository not found" in stderr:
            return False, "Repository not found. Check that it exists and your token has 'repo' scope."
        else:
            return False, f"Git clone failed: {result.stderr.strip()}"
    return True, "Cloned successfully"


def pull():
    """Pull latest changes from remote."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    result = run_git("pull")
    if result.returncode != 0:
        return False, result.stderr
    return True, "Pulled successfully"


def push():
    """Push local changes to remote."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    # Add all changes
    run_git("add", "-A")

    # Check if there are changes to commit
    status = run_git("status", "--porcelain")
    if not status.stdout.strip():
        return True, "No changes to push"

    # Commit
    commit_result = run_git("commit", "-m", "vault: update prompts")
    if commit_result.returncode != 0:
        return False, commit_result.stderr

    # Push
    push_result = run_git("push")
    if push_result.returncode != 0:
        return False, push_result.stderr

    return True, "Pushed successfully"


def commit_and_push(message):
    """Commit changes with a message and push."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized"

    # Add all changes
    run_git("add", "-A")

    # Commit
    commit_result = run_git("commit", "-m", message)
    if commit_result.returncode != 0:
        return False, commit_result.stderr

    # Push
    push_result = run_git("push")
    if push_result.returncode != 0:
        return False, push_result.stderr

    return True, "Committed and pushed"
