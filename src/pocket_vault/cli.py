from pathlib import Path
import sys
import click
from .auth import auth_flow
from .git import pull, push, background_pull, VAULT_DIR, CONFIG_DIR, get_remote_url
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
Pocket Vault

Numbers from `pv` are the fast path. Paths also work everywhere a number does.

BROWSE
  pv                       List prompts (favorites first)
  pv <query>               Search

USE
  pv <N>                   Copy prompt #N to clipboard
                           pv 4.1 = first prompt in folder #4
                           pv <N> on a folder copies every prompt concatenated

WRITE
  pv add <path>            Create a new prompt (opens $EDITOR)
  pv add <path> --content "..."  Inline, no editor

VAULT
  Location: {VAULT_DIR}
{_format_remote()}

First time? `pv auth`. More: `pv help-full`.
""")


def print_full_help():
    """Print full help text with all commands."""
    print(f"""
Pocket Vault

Numbers from `pv` are the fast path. Paths also work everywhere a number does.

BROWSE
  pv                       List prompts (favorites first, hierarchical)
  pv <query>               Search names, folder names, and file content (multi-word ok)

USE
  pv <N>                   Copy prompt #N to clipboard
                           pv 4.1 = first prompt in folder #4
                           pv <N> on a folder copies every prompt concatenated
  pv read <N|path>         Print to stdout
  pv copy <N|path>         Same as pv <N>, but explicit (use in scripts)
  pv use <N|path>          Copy the .md file into your current directory
  pv use <N> as <name>     Save under a different filename (e.g. AGENTS.md, CLAUDE.md)
                           If destination exists: overwrite, append, or cancel.

WRITE
  pv add <path>                  Create a new prompt (opens $EDITOR)
  pv add <path> --content "..."  Inline, no editor
                                 AI agents: single-quote --content so backslashes stay literal.
                                 Use / in paths, not \\.
  pv edit <N|path>         Open an existing prompt in $EDITOR
  pv rm <N|path>           Delete a file or folder (folders delete recursively)
  pv rm coding             deletes the whole coding/ folder
  pv fav <N|path>          Pin to top (favorites become #1, #2, ...)
  pv unfav <N|path>        Unpin

SYNC
  pv pull / pv push        Manual git sync (writes auto-commit and push, rarely needed)
  pv auth                  One-time GitHub setup

VAULT
  Location: {VAULT_DIR}
{_format_remote()}
  Plain git repo -- ls, cat, git log all work.

STATE  (per device, not synced)
  Location: {CONFIG_DIR}
  Token, repo name, favorites, recents.
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
        background_pull()
        return

    # No arguments - show numbered list
    if not args:
        items = get_numbered_list()
        print(format_numbered_list(items))
        background_pull()
        return

    command = args[0]

    # Handle --help and -h
    if command in ("-h", "--help"):
        print_help()
        background_pull()
        return

    # Reserved commands
    if command == "auth":
        success, message = auth_flow()
        if not success:
            print(f"Error: {message}")
            sys.exit(1)
        background_pull()
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
        background_pull()
        return

    if command == "help":
        print_help()
        background_pull()
        return

    if command == "help-full":
        print_full_help()
        background_pull()
        return

    if command == "add":
        if len(args) < 2:
            print("Error: Usage: pv add <path> [--content \"...\"]")
            sys.exit(1)
        path = args[1]
        # Parse --content flag
        content = None
        if "--content" in args:
            content_idx = args.index("--content")
            if content_idx + 1 < len(args):
                content = args[content_idx + 1]
            else:
                print("Error: --content requires a value")
                sys.exit(1)
        success, message = add_prompt(path, content=content)
        print(message)
        if not success:
            sys.exit(1)
        background_pull()
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
        background_pull()
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
        background_pull()
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
        background_pull()
        return

    if command == "use":
        if len(args) < 2:
            print("Error: Usage: pv use <path> [as <name>]")
            sys.exit(1)
        arg = args[1]
        path, err = resolve_number_or_path(arg, get_numbered_list())
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        dest_name = None
        if len(args) >= 3 and args[2] == "as":
            if len(args) < 4:
                print("Error: 'as' requires a destination name")
                sys.exit(1)
            dest_name = args[3]
        success, message = use_prompt(path, dest_name=dest_name)
        print(message)
        if not success:
            sys.exit(1)
        background_pull()
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
        background_pull()
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
        background_pull()
        return

    if command == "rm":
        if len(args) < 2:
            print("Error: Usage: pv rm <path>")
            sys.exit(1)
        arg = args[1]
        path, err = resolve_number_or_path(arg, get_numbered_list())
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        success, message = delete_prompt(path)
        print(message)
        if not success:
            sys.exit(1)
        background_pull()
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
        background_pull()
        return

    # Not a reserved command - treat as search query
    query = " ".join(args)
    results = search_vault(query)
    print(format_results(results, query))
    background_pull()


if __name__ == "__main__":
    main()
