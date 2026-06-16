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

**Stop repeating yourself.** You have a Python style prompt you use in every chat session. Save it once with `pv add coding/python-style`. Next week, on a different machine, tell your LLM "Use my python style prompt" — it reads it from your vault. Same prompt, any device.

**Your LLM remembers your preferences.** Save your coding style, debugging approach, and writing tone. When you start a new session, say "Check my prompt vault for my preferences." No more repeating yourself.

**Organize by topic.** Create folders for web, data, writing — whatever makes sense to you. Search by keyword to find what you need.

**Your LLM saves new patterns.** During a session, your LLM discovers something useful. Tell it "Add this to my prompt vault as coding/async-patterns." Next time, it's there.

## How It Works

Your prompts are `.md` files in a private git repo. The CLI keeps a local clone for instant search. Writes auto-commit and push. Everything is tracked in git history.

Full docs: [Technical Guide](src/README.md)
