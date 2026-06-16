# Prompt Vault

A Python CLI to keep track of your prompts across devices by saving them in a private GitHub repository.

## Use Case

You're working on a Python project and you've developed a prompt that helps you write better code:

```
Always follow PEP 8 style guidelines. Use type hints for all function signatures.
Prefer dataclasses over dicts for structured data. Write docstrings for public functions.
```

You've been copying this into every new chat session. Instead, you save it once:

```bash
pv add coding/python-style
```

Your editor opens. You paste the prompt, save, and close. It's now in your vault and pushed to GitHub.

Next week, you're on a different machine working on a Django project. You tell your LLM:

```
Use my python style prompt
```

The LLM runs:

```bash
pv read coding/python-style
```

And applies your instructions. Same prompt, any device, any project.

## Installation

```bash
pip install prompt-vault
pv auth                          # One-time GitHub setup
pv add coding/python-style       # Save a prompt (opens editor)
pv python style                  # Search your vault
pv read coding/python-style      # Read it (for you or your LLM)
```

Full docs: [Technical Guide](src/README.md)
