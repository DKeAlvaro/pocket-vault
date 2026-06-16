import os
import subprocess
import requests
from pathlib import Path
from .git import CONFIG_DIR, TOKEN_FILE, REPO_FILE, VAULT_DIR, clone_repo


def save_token(token):
    """Save GitHub token to config."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token)


def save_repo(repo):
    """Save repo name to config."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    REPO_FILE.write_text(repo)


def load_token():
    """Load GitHub token from config."""
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return None


def load_repo():
    """Load repo name from config."""
    if REPO_FILE.exists():
        return REPO_FILE.read_text().strip()
    return None


def get_repo_url(token, repo_name):
    """Get authenticated repo URL."""
    return f"https://x-access-token:{token}@github.com/{repo_name}.git"


def auth_flow():
    """Run the authentication flow."""
    # Check if already authenticated
    existing_token = load_token()
    existing_repo = load_repo()

    if existing_token and existing_repo:
        print("Already authenticated")
        print(f"  Token: {'*' * (len(existing_token) - 4) + existing_token[-4:]}")
        print(f"  Repo:  {existing_repo}")
        print()

        response = input("Re-authenticate? [y/N]: ").strip().lower()
        if response != "y":
            print("Keeping existing configuration")
            return True, "Already authenticated"

        print()

    print("Pocket Vault Authentication")
    print("-" * 40)
    print()

    # Ask for token
    print("Enter your GitHub Personal Access Token")
    print("(Create one at: https://github.com/settings/tokens)")
    print("Required scope: repo")
    print()

    token = input("Token: ").strip()
    if not token:
        return False, "No token provided"

    # Verify token works
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/user", headers=headers)

    if response.status_code == 401:
        return False, "Invalid token. Check that it's copied correctly and not expired."
    elif response.status_code != 200:
        error_msg = response.json().get("message", "Unknown error")
        return False, f"Failed to authenticate: {error_msg}"

    username = response.json()["login"]
    print(f"Authenticated as: {username}")
    print()

    # Ask for repo name
    default_repo = f"{username}/pocket-vault"
    repo_name = input(f"Repo name [{default_repo}]: ").strip()
    if not repo_name:
        repo_name = default_repo

    # Check if repo exists, create if not
    repo_url = f"https://api.github.com/repos/{repo_name}"
    response = requests.get(repo_url, headers=headers)

    if response.status_code == 404:
        print(f"Repo {repo_name} not found. Creating...")

        # Create private repo
        create_url = "https://api.github.com/user/repos"
        data = {
            "name": repo_name.split("/")[-1],
            "private": True,
            "auto_init": True
        }
        response = requests.post(create_url, headers=headers, json=data)

        if response.status_code == 403:
            return False, (
                "Your token doesn't have permission to create repos.\n"
                "Create a new token at: https://github.com/settings/tokens\n"
                "Required scopes: 'repo' (full control of private repositories)"
            )
        elif response.status_code == 422:
            return False, f"Repo '{repo_name.split('/')[-1]}' already exists or name is invalid."
        elif response.status_code != 201:
            error_msg = response.json().get("message", "Unknown error")
            return False, f"Failed to create repo: {error_msg}"

        print(f"Created private repo: {repo_name}")
    elif response.status_code == 403:
        return False, (
            "Your token doesn't have permission to access this repo.\n"
            "Make sure your token has 'repo' scope."
        )
    elif response.status_code != 200 and response.status_code != 404:
        error_msg = response.json().get("message", "Unknown error")
        return False, f"Failed to check repo: {error_msg}"

    # Save config
    save_token(token)
    save_repo(repo_name)

    # Clone repo
    repo_git_url = get_repo_url(token, repo_name)
    success, message = clone_repo(repo_git_url)

    if not success:
        return False, f"Failed to clone: {message}"

    print()
    print("Authentication complete!")
    print(f"Vault location: {VAULT_DIR}")
    print()
    print("Next steps:")
    print("  pv add <path>    - Add a new prompt")
    print("  pv <query>       - Search your vault")
    print("  pv help          - Show LLM instructions")

    return True, "Success"
