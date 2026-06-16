from pathlib import Path
import sys
import click
from .auth import auth_flow
from .git import pull, push, VAULT_DIR
from .search import search_vault, format_results
from .vault import add_prompt, edit_prompt, use_prompt, read_prompt, delete_prompt, browse_vault


HELP_TEXT = f"""
POCKET VAULT
============

Your most used prompts, always with you.

SEARCHING
  pv <query>              Search by keyword across all prompts
  pv python style         Example: finds prompts about python style
  pv                      Browse the full vault structure

ADDING PROMPTS
  pv add <path>           Create a new prompt (opens your editor)
  pv add coding/python    Creates coding/python.md in your vault
  pv add ideas            Creates ideas.md in your vault
  Folders are created automatically. .md is added if missing.

EDITING PROMPTS
  pv edit <path>          Open an existing prompt in your editor
  pv edit coding/python   Opens coding/python.md for editing

USING PROMPTS
  pv read <path>          Output prompt content to stdout
  pv read coding/python   Prints the content of coding/python.md
  pv use <path>           Copy a prompt to your current folder
  pv use coding/python    Copies python.md to where you are now

DELETING
  pv rm <path>            Delete a prompt file or entire folder
  pv rm coding/python     Deletes coding/python.md
  pv rm coding            Deletes the whole coding/ folder

SYNCING
  pv pull                 Pull latest changes from remote
  pv push                 Push local changes to remote
  Writes (add, edit, rm) auto-commit and push.
  Reads (search, browse) are instant from local copy.

SETUP
  pv auth                 Authenticate with GitHub (one time)

YOUR VAULT
  Location: {VAULT_DIR}
  It is a regular git repo. You can navigate it with ls, cat, etc.
  All changes are tracked in git history.
"""


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("args", nargs=-1)
def main(args):
    """Pocket Vault - Manage your personal prompt library."""

    # No arguments - browse vault
    if not args:
        print(browse_vault())
        return

    command = args[0]

    # Reserved commands
    if command == "auth":
        success, message = auth_flow()
        if not success:
            print(f"Error: {message}")
            sys.exit(1)
        return

    if command == "pull":
        success, message = pull()
        print(message)
        if not success:
            sys.exit(1)
        return

    if command == "push":
        success, message = push()
        print(message)
        if not success:
            sys.exit(1)
        return

    if command == "help":
        print(HELP_TEXT)
        return

    if command == "add":
        if len(args) < 2:
            print("Error: Usage: pv add <path>")
            sys.exit(1)
        path = args[1]
        success, message = add_prompt(path)
        print(message)
        if not success:
            sys.exit(1)
        return

    if command == "edit":
        if len(args) < 2:
            print("Error: Usage: pv edit <path>")
            sys.exit(1)
        path = args[1]
        success, message = edit_prompt(path)
        print(message)
        if not success:
            sys.exit(1)
        return

    if command == "use":
        if len(args) < 2:
            print("Error: Usage: pv use <path>")
            sys.exit(1)
        path = args[1]
        success, message = use_prompt(path)
        print(message)
        if not success:
            sys.exit(1)
        return

    if command == "read":
        if len(args) < 2:
            print("Error: Usage: pv read <path>")
            sys.exit(1)
        path = args[1]
        success, content = read_prompt(path)
        if not success:
            print(f"Error: {content}")
            sys.exit(1)
        print(content)
        return

    if command == "rm":
        if len(args) < 2:
            print("Error: Usage: pv rm <path>")
            sys.exit(1)
        path = args[1]
        success, message = delete_prompt(path)
        print(message)
        if not success:
            sys.exit(1)
        return

    # Not a reserved command - treat as search query
    query = " ".join(args)
    results = search_vault(query)
    print(format_results(results, query))


if __name__ == "__main__":
    main()
