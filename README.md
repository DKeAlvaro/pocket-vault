# Pocket

A home for your most used prompts, synced across devices.

```bash
pip install pocket
pk auth                          # One-time GitHub setup
pk add coding/python-style       # Save a prompt (opens editor)
pk python style                  # Search your vault
pk read coding/python-style      # Read it (for you or your LLM)
```

You tell your LLM:

```
Use my python style prompt
```

It runs `pk read coding/python-style` and applies your instructions. Same prompt, any device, any project.

Full docs: [Technical Guide](src/README.md)
