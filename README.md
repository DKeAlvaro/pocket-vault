# Pocket Vault

A home for your most used prompts, synced across devices.

**Ask your LLM:** "How does Pocket Vault work?" — it'll read the docs and explain everything.

## Quick Start

```bash
pip install pocket-vault
pv auth                          # One-time GitHub setup
pv add coding/python-style       # Save a prompt (opens editor)
pv python style                  # Search your vault
pv read coding/python-style      # Read it (for you or your LLM)
```

## Use Cases

### 1. You have a Python style prompt you use everywhere

You've written a prompt that helps you write better Python code. Save it once:

```bash
pv add coding/python-style
```

Your editor opens. You paste the prompt, save, and close. It's now in your vault and pushed to GitHub.

Next week, you're on a different machine working on a Django project. You tell your LLM:

```
Use my python style prompt
```

It runs `pv read coding/python-style` and applies your instructions. Same prompt, any device, any project.

### 2. You want your LLM to remember your preferences

You're tired of explaining your coding style, debugging approach, and preferences to every new chat session. Save them:

```bash
pv add personal/coding-style
pv add personal/debugging-approach
pv add personal/writing-tone
```

Now when you start a new session, just say:

```
Check my prompt vault for my preferences
```

Your LLM searches and reads your prompts. No more repeating yourself.

### 3. You want to organize prompts by project or topic

Create folders for different contexts:

```bash
pv add web/react-patterns
pv add web/api-design
pv add data/pandas-tips
pv add writing/blog-template
```

Search by keyword:

```bash
pv react                    # Finds web/react-patterns.md
pv pandas                   # Finds data/pandas-tips.md
```

Your vault is a regular git repo — organize it however you want.

### 4. You want to share prompts with your team

Your team has standard prompts for code review, PR descriptions, and documentation. Create a shared vault:

```bash
pv add team/code-review
pv add team/pr-description
pv add team/doc-standards
```

Push to GitHub. Your team clones the same vault. Everyone uses the same prompts.

```bash
pv pull                     # Get latest from team
pv push                     # Share your updates
```

### 5. You want your LLM to learn and save new patterns

During a coding session, your LLM discovers a useful pattern. Tell it to save it:

```
Add this to my prompt vault as coding/async-patterns
```

Your LLM runs `pv add coding/async-patterns`, opens your editor, and saves the prompt. Next time you need it, it's there.

## How It Works

- **Your prompts live in a private git repo** — version controlled, synced across devices
- **The CLI maintains a local clone** at `~/.pocket-vault/` — instant search, no network round-trips
- **Writes auto-commit and push** — every change is tracked in git history
- **Reads are instant** — local search, no cloud dependency
- **Works with any LLM** — the CLI outputs plain text, any agent can use it

## Commands

```bash
pv <query>              # Search by keyword across all prompts
pv add <path>           # Create a new prompt (opens editor)
pv edit <path>          # Edit an existing prompt
pv read <path>          # Output prompt content (for LLMs)
pv use <path>           # Copy prompt to current folder
pv rm <path>            # Delete a prompt or folder
pv pull                 # Pull latest from remote
pv push                 # Push local changes
pv help                 # Show full command reference
```

## Full Documentation

See the [Technical Guide](src/README.md) for detailed setup, architecture, and troubleshooting.
