from pathlib import Path
import sys
import click
from .auth import auth_flow
from .git import pull, push, VAULT_DIR, get_remote_url
from .search import search_vault, format_results
from .state import add_favorite, remove_favorite
from .vault import (
    add_prompt, edit_prompt, use_prompt, read_prompt, delete_prompt,
    browse_vault, copy_prompt, copy_folder, get_numbered_list, format_numbered_list,
    resolve_number_or_path,
)


def _format_remote():
    """Return a sanitized remote URL or 'not configured'."""
    import re
    remote = get_remote_url()
    if remote:
        remote = re.sub(r"https://[^@]+@", "https://", remote)
        return f"  Remote:   {remote}"
    return "  Remote:   not configured"


def print_help():
    """Print short help text — just the essentials."""
    print(f"""
Pocket Vault: your prompts, always with you.

Prompts are .md files in a private GitHub repo, with a local clone for fast search and clipboard copy.

  pv                 List prompts (numbered, favorites first)
  pv <number>        Copy prompt to clipboard (e.g. pv 3, pv 4.1)
  pv add <path>      Create a new prompt (opens editor)

  Vault:  {VAULT_DIR}
{_format_remote()}

First time? Run `pv auth`. More commands: `pv help-full`.
""")


def print_full_help():
    """Print full help text with all commands."""
    print(f"""
Pocket Vault: your most used prompts, always with you.

SEARCHING
  pv <query>              Search by keyword across all prompts
  pv python style         Example: finds prompts about python style
  pv                      List prompts with hierarchical numbers
  pv <number>             Copy that prompt to your clipboard
  pv 4.1                  Copy the first prompt in folder 4
  pv 4                    Copy all prompts in folder 4 (concatenated)

ADDING PROMPTS
  pv add <path>           Create a new prompt (opens editor)
  pv add coding/python    Creates coding/python.md in your vault
  pv add ideas            Creates ideas.md in your vault
  Folders are created automatically. .md is added if missing.

EDITING PROMPTS
  pv edit <path>          Open an existing prompt in your editor
  pv edit coding/python   Opens coding/python.md for editing
  pv edit <number>        Edit the prompt at that position in 'pv'

FAVORITES
  pv fav <path>           Pin a prompt to the top of the list
  pv fav jupyter          jupyter.md appears as #1 in 'pv'
  pv unfav <path>         Remove a prompt from favorites
  pv unfav jupyter

USING PROMPTS
  pv read <path>          Output prompt content to stdout
  pv read <number>        Read the prompt at that position in 'pv'
  pv copy <path>          Copy a prompt to your clipboard
  pv copy <number>        Copy the prompt at that position in 'pv'
  pv use <path>           Copy a prompt to your current folder
  pv use <number>         Copy the prompt at that position to cwd

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
{_format_remote()}
  It is a regular git repo. You can navigate it with ls, cat, etc.
  All changes are tracked in git history.
""")


import sys

@click.command(
    context_settings=dict(
        help_option_names=[],
        ignore_unknown_options=True,
    )
)
@click.argument("args", nargs=-1)
def main(args):
    """Pocket Vault - Manage your personal prompt library."""

    # Check for help flags before click processes them
    if any(flag in sys.argv for flag in ("-h", "--help")):
        print_help()
        return

    # No arguments - show numbered list
    if not args:
        items = get_numbered_list()
        print(format_numbered_list(items))
        return

    command = args[0]

    # Handle --help and -h
    if command in ("-h", "--help"):
        print_help()
        return

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

    if command == "tree":
        print(browse_vault())
        return

    if command == "help":
        print_help()
        return

    if command == "help-full":
        print_full_help()
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
        arg = args[1]
        path, err = resolve_number_or_path(arg, get_numbered_list())
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        success, message = edit_prompt(path)
        print(message)
        if not success:
            sys.exit(1)
        return

    if command == "fav":
        if len(args) < 2:
            print("Error: Usage: pv fav <path>")
            sys.exit(1)
        arg = args[1]
        path, err = resolve_number_or_path(arg, get_numbered_list())
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        vault_path = VAULT_DIR / (path if path.endswith(".md") else path + ".md")
        if not vault_path.exists():
            print(f"Error: File not found: {path}")
            sys.exit(1)
        if add_favorite(path):
            print(f"Favorited {path}")
        else:
            print(f"{path} is already a favorite")
        return

    if command == "unfav":
        if len(args) < 2:
            print("Error: Usage: pv unfav <path>")
            sys.exit(1)
        arg = args[1]
        path, err = resolve_number_or_path(arg, get_numbered_list())
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        if remove_favorite(path):
            print(f"Unfavorited {path}")
        else:
            print(f"{path} is not a favorite")
        return

    if command == "use":
        if len(args) < 2:
            print("Error: Usage: pv use <path>")
            sys.exit(1)
        arg = args[1]
        path, err = resolve_number_or_path(arg, get_numbered_list())
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        success, message = use_prompt(path)
        print(message)
        if not success:
            sys.exit(1)
        return

    if command == "copy":
        if len(args) < 2:
            print("Error: Usage: pv copy <path>")
            sys.exit(1)
        arg = args[1]
        path, err = resolve_number_or_path(arg, get_numbered_list())
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        success, message = copy_prompt(path)
        print(message)
        if not success:
            sys.exit(1)
        return

    if command == "read":
        if len(args) < 2:
            print("Error: Usage: pv read <path>")
            sys.exit(1)
        arg = args[1]
        path, err = resolve_number_or_path(arg, get_numbered_list())
        if err:
            print(f"Error: {err}")
            sys.exit(1)
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

    # Not a reserved command - check if it's a number (shortcut for copy)
    import re
    if re.match(r"^\d+(\.\d+)*$", command):
        items = get_numbered_list()
        path, err = resolve_number_or_path(command, items)
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        if path.endswith("/"):
            success, message = copy_folder(path)
        else:
            success, message = copy_prompt(path)
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
