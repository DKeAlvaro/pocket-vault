# Pocket Vault

A home for your most used prompts, synced across devices.

```bash
pip install pocket-vault
pv auth                          # One-time GitHub setup
pv add coding/python-style       # Save a prompt (opens editor)
pv python style                  # Search your vault
pv read coding/python-style      # Read it (for you or your LLM)
```

You tell your LLM:

```
Use my python style prompt
```

It runs `pv read coding/python-style` and applies your instructions. Same prompt, any device, any project.

Full docs: [Technical Guide](src/README.md)
