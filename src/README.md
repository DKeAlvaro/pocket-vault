# Pocket Vault: Technical Guide

The complete reference for every Pocket Vault command, the architecture underneath, and how to set it up across machines. If you want a quick sales pitch, read the root README. This document is for using the tool.

## What you're working with

Three things, and three things only:

1. A Python CLI installed via `pip` (the `pv` command).
2. A private GitHub repo, cloned to `~/.pocket-vault/`, holding your prompts as `.md` files.
3. A small state file at `~/.config/pocket-vault/state.json` for per-device data (favorites, recents).

That's the stack. Everything below explains how to use it.

## Installation

```bash
pip install pocket-vault
```

Requirements:
- Python 3.8 or higher
- Git installed and configured
- A GitHub account

To install from source (development):

```bash
git clone https://github.com/DKeAlvaro/pocket-vault.git
cd pocket-vault
pip install -e .
```

## First-time setup: `pv auth`

`pv auth` walks you through the GitHub side of things. It will:

1. Ask for a GitHub Personal Access Token (with `repo` scope).
2. Create a private repo called `pocket-vault` under your account, or use an existing one.
3. Clone it to `~/.pocket-vault/`.

### Creating a GitHub token

If you don't have a token yet:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select the `repo` scope (full control of private repositories)
4. Generate and copy the token
5. Paste it into `pv auth` when prompted

The token is stored at `~/.config/pocket-vault/token`.

### Re-authentication

Running `pv auth` again shows your current config and asks if you want to re-authenticate. Useful when your token expires.

## The numbered list: how the UX works

`pv` with no arguments prints a numbered list of your prompts. This is the central UI. Every other command that takes a path can also take the number from this list.

The list is stable: once you memorize `pv 3` is your Python style guide, it stays `pv 3` until you add or remove prompts around it. Favorites pin to the top, the rest follows as a hierarchical tree.

```
$ pv
* 1  python-style
* 2  jupyter-handling
  3  code-review
  4  coding/
      4.1  async
      4.2  pytest
  5  data/
      5.1  analysis
```

The `*` marks favorites. Folders end with `/`. Children of folder `N` are `N.1`, `N.2`, and so on.

### Numbers in any command

Any command that takes a path also accepts the number from the list:

```bash
pv 1            # copy favorite #1 to clipboard
pv 4.1          # copy coding/async
pv edit 3       # open prompt #3 in your editor
pv fav 5.1      # pin data/analysis
pv use 2        # copy favorite #2 into the current folder
pv rm 4.2       # delete coding/pytest
```

This is the fast path. You rarely need to type full paths.

### Folders

When you point a number at a folder, `pv <N>` copies every `.md` file in that folder, concatenated with `# name` headers between them. Useful when you want to paste a whole category of instructions at once:

```
$ pv 4
Copied 2 prompt(s) from coding/ to clipboard

# async

Async patterns content

# pytest

Pytest patterns content
```

## All commands

### `pv` (no args)
Print the numbered list. See "The numbered list" above.

### `pv <number>` or `pv <path>`
Copy a prompt to your clipboard. If the number points to a folder, copies the folder's contents concatenated.

```bash
pv 1
pv coding/python-style
pv 4.1
pv 4              # folder, copies all
```

### `pv <query>`
Search. If the first argument isn't a reserved command, a number, or a help flag, it falls through to search. Search checks filenames, folder names, and file content. Results show matches with previews.

```bash
pv python
pv async patterns
```

### `pv add <path>`
Create a new prompt. Opens your editor. Folders are created automatically. `.md` is added if missing. Auto-commits and pushes on save.

```bash
pv add coding/python-style
pv add ideas
pv add projects/alpha/onboarding
```

### `pv add <path> --content "..."`
Create a new prompt with inline content, without opening an editor. Useful for programmatic use by LLMs or scripts.

```bash
pv add coding/python-style --content "Always use type hints and dataclasses."
pv add writing/email-drafting --content "You are a professional email assistant."
```

### `pv edit <path>` or `pv edit <number>`
Open an existing prompt in your editor. Auto-commits and pushes on save.

```bash
pv edit coding/python-style
pv edit 3
```

### `pv read <path>` or `pv read <number>`
Print a prompt's content to stdout. Use this when an agent can read stdout.

```bash
pv read coding/python-style
pv read 3
```

### `pv copy <path>` or `pv copy <number>`
Copy a prompt to your system clipboard. Same as `pv <number>` for a single file, but explicit.

Platform support:
- Windows: built-in `clip`
- macOS: built-in `pbcopy`
- Linux: requires `xclip` or `xsel`

```bash
pv copy coding/python-style
pv copy 3
```

### `pv use <path>` or `pv use <number>`
Copy a prompt's file into your current working directory. Useful when you want a static copy of a prompt in a project.

```bash
pv use coding/python-style
pv use 3
```

### `pv rm <path>`
Delete a prompt file or an entire folder. Auto-commits and pushes.

```bash
pv rm coding/python-style      # delete one file
pv rm coding                   # delete whole folder
```

### `pv fav <path>` and `pv unfav <path>`
Pin a prompt to the top of the list (`fav`) or unpin it (`unfav`). Numbers also work.

```bash
pv fav coding/python-style
pv fav 3
pv unfav coding/python-style
pv unfav 3
```

Favorites are stored in `~/.config/pocket-vault/state.json` and are per-device. They don't sync with git. Your favorites on your laptop can differ from your favorites on your desktop.

### `pv pull` and `pv push`
Manual sync. Writes (`add`, `edit`, `rm`) auto-commit and push, so you only need these in specific cases:
- You edited files directly (vim, VS Code, etc.)
- You cloned the vault to a new machine and need to push local changes
- The auto-push failed (network issue, expired token)

```bash
pv pull
pv push
```

### `pv auth`
First-time setup. Re-authentication. See "First-time setup" above.

### `pv help` and `pv help-full`
- `pv help`: short reference. Shows the essentials: list, copy by number, add, vault location, remote.
- `pv help-full`: every command documented.

The same content is also served on `pv -h` and `pv --help`.

## Searching

Anything that's not a reserved command and not a number becomes a search query. Search runs over:

- Filenames (e.g., `jupyter` matches `jupyter.md`)
- Folder names (e.g., `coding` matches anything inside `coding/`)
- File content (case-insensitive substring match)

Results are sorted by relevance with content previews.

```bash
pv python              # matches filenames, folder names, and content
pv "async patterns"    # multi-word search
pv jupyter notebook    # matches a file with that content
```

## Architecture

### File layout

```
~/.pocket-vault/                       # the vault itself
├── .git/                              # git repo
├── coding/
│   ├── python-style.md
│   └── async.md
├── data-analysis.md
└── README.md

~/.config/pocket-vault/                # per-device state
├── token                              # GitHub PAT
├── repo                               # repo name (e.g., username/pocket-vault)
└── state.json                         # favorites and recents
```

The vault is a regular git repo. You can:

- Navigate it with `ls`, `cd`, `cat`
- Edit files with any editor
- Use `git log`, `git diff` for history
- Run `git` commands directly

State (favorites, recents) is per-device and is **not** in the vault. It lives in `~/.config/pocket-vault/state.json`.

### How sync works

Writes (`add`, `edit`, `rm`) auto-commit and push:

1. Create, edit, or delete the file
2. `git add -A`
3. `git commit -m "vault: <action> <path>"`
4. `git push`

Reads (search, browse, read) are instant from the local clone. No network round-trip.

Use `pv pull` to get latest from another device. Use `pv push` to push local changes that weren't done through the CLI.

## Cross-device workflow

The vault is a git repo, so cross-device use is just git.

1. **On a new machine:** install Pocket Vault, run `pv auth`, and either pull an existing vault or let `pv auth` create a new one.
2. **Migrating to a new machine:** clone the existing vault over `~/.pocket-vault/`, then run `pv auth` with the same GitHub credentials.
3. **Different favorites per device:** favorites are per-device (not synced). You can have different pinned prompts on your laptop and your desktop.

## Editor configuration

The CLI checks for an editor in this order:

1. `$EDITOR` environment variable
2. `$VISUAL` environment variable
3. Platform default: `notepad` on Windows, `nano` on Unix

To use VS Code:
```bash
export EDITOR="code --wait"
```

To use Vim:
```bash
export EDITOR="vim"
```

`code --wait` is important so the CLI waits for the editor to close before committing.

## Development

### Project structure

```
pocket-vault/
├── src/
│   └── pocket_vault/
│       ├── __init__.py
│       ├── cli.py          # Command routing and dispatch
│       ├── auth.py         # GitHub authentication
│       ├── git.py          # Git operations (clone, pull, push, commit)
│       ├── vault.py        # File operations (add, edit, read, copy, use, rm)
│       ├── search.py       # Search
│       └── state.py        # Per-device state (favorites, recents)
├── pyproject.toml
└── README.md
```

### Running in development

```bash
pip install -e .
```

Changes to the code take effect immediately.

### Publishing to PyPI

```bash
python -m build
twine upload dist/*
```

## License

MIT
