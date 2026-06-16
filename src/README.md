# Technical Guide

Complete reference for installing, setting up, and using Prompt Vault.

## Installation

### From PyPI (when published)

```bash
pip install prompt-vault
```

### From source (development)

```bash
git clone https://github.com/YOUR_USERNAME/prompt-vault.git
cd prompt-vault
pip install -e .
```

### Requirements

- Python 3.8+
- Git installed and configured
- GitHub account

## Setup

### First-time authentication

```bash
pv auth
```

This will:
1. Ask for your GitHub Personal Access Token
2. Create a private repo called `prompt-vault` (or use an existing one)
3. Clone it to `~/.prompt-vault/`

**Creating a GitHub token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scope: `repo` (full control of private repositories)
4. Generate and copy the token

### Re-authentication

If you run `pv auth` again, it will show your current config and ask if you want to re-authenticate:

```
Already authenticated
  Token: ****abcd
  Repo:  yourusername/prompt-vault

Re-authenticate? [y/N]:
```

## Commands

### Searching

```bash
pv <query>              # Search by keyword across all prompts
pv python style         # Find prompts about python style
pv                      # Browse the full vault structure
```

Search checks filenames, folder names, and content. Results show matching files with previews.

### Adding prompts

```bash
pv add <path>           # Create a new prompt (opens your editor)
pv add coding/python    # Creates coding/python.md in your vault
pv add ideas            # Creates ideas.md in your vault
```

Folders are created automatically. `.md` extension is added if missing.

The CLI opens your preferred editor (checks `$EDITOR` or `$VISUAL`, falls back to `notepad` on Windows, `nano` on Unix). After you save and close, it auto-commits and pushes.

### Editing prompts

```bash
pv edit <path>          # Open an existing prompt in your editor
pv edit coding/python   # Opens coding/python.md for editing
```

Auto-commits and pushes after you save.

### Reading prompts

```bash
pv read <path>          # Output prompt content to stdout
pv read coding/python   # Prints the content of coding/python.md
```

Use this to let your LLM read prompts directly without copying files.

### Using prompts

```bash
pv use <path>           # Copy a prompt to your current folder
pv use coding/python    # Copies python.md to where you are now
```

Use this to copy prompts into your current project.

### Deleting

```bash
pv rm <path>            # Delete a prompt file or entire folder
pv rm coding/python     # Deletes coding/python.md
pv rm coding            # Deletes the whole coding/ folder
```

Auto-commits and pushes the deletion.

### Syncing

```bash
pv pull                 # Pull latest changes from remote
pv push                 # Push local changes to remote
```

- Writes (`add`, `edit`, `rm`) auto-commit and push
- Reads (`search`, `browse`) are instant from local copy
- Use `pv pull` to sync if you edited files manually or from another device

### Help

```bash
pv help                 # Show complete command reference
```

This outputs instructions that both you and your LLM can read.

## LLM Integration

### Option 1: Tell your LLM to check help

```
You: "Run `pv help` and follow those instructions"
LLM: [reads help, learns commands, uses them]
```

### Option 2: Add to your agent config

Run `pv help`, copy the output, and paste it into:
- `AGENTS.md` (for OpenCode, Claude Code)
- `.cursorrules` (for Cursor)
- Your agent's system prompt

### Option 3: Create a skill file

For agents that support skills (OpenCode, Claude Code):

```bash
mkdir -p .opencode/skills/prompt-vault
pv help > .opencode/skills/prompt-vault/SKILL.md
```

Now your agent loads the skill automatically when needed.

## Architecture

### File structure

```
~/.prompt-vault/
├── .git/               # Git repository
├── coding/
│   ├── python.md
│   └── javascript.md
├── writing/
│   └── blog-template.md
└── README.md
```

Your vault is a regular git repo. You can:
- Navigate it with `ls`, `cd`, `cat`
- Edit files with any editor
- Use git commands directly
- View history with `git log`

### How sync works

**On write (add, edit, rm):**
1. Create/edit/delete the file
2. `git add -A`
3. `git commit -m "vault: <action> <path>"`
4. `git push`

**On read (search, browse, read):**
- Instant from local clone
- No network round-trip

**Manual sync:**
- `pv pull` to get latest from remote
- `pv push` to push all local changes

### Editor configuration

The CLI checks for editors in this order:
1. `$EDITOR` environment variable
2. `$VISUAL` environment variable
3. Platform default (`notepad` on Windows, `nano` on Unix)

To use VS Code:
```bash
export EDITOR="code --wait"
```

To use Vim:
```bash
export EDITOR="vim"
```

## Troubleshooting

### "Vault not initialized"

Run `pv auth` to set up your vault.

### "Git authentication failed"

Your token may be invalid or expired. Run `pv auth` to re-authenticate.

### "Repository not found"

Check that your token has `repo` scope. Create a new token at https://github.com/settings/tokens

### Editor doesn't open

Set the `$EDITOR` environment variable to your preferred editor:
```bash
export EDITOR="code --wait"  # VS Code
export EDITOR="vim"          # Vim
```

### Changes not syncing

Run `pv pull` to get latest from remote, then `pv push` to push your changes.

## Development

### Project structure

```
prompt-vault/
├── src/
│   └── prompt_vault/
│       ├── __init__.py
│       ├── cli.py          # Command routing
│       ├── auth.py         # GitHub authentication
│       ├── git.py          # Git operations
│       ├── search.py       # Search functionality
│       └── vault.py        # Add/edit/use/rm commands
├── pyproject.toml
└── README.md
```

### Running in development mode

```bash
pip install -e .
```

Changes to the code are live immediately.

### Publishing to PyPI

```bash
python -m build
twine upload dist/*
```

## License

MIT
