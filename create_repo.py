import requests
from pathlib import Path

token_file = Path.home() / ".config" / "prompt-vault" / "token"
token = token_file.read_text().strip()

headers = {"Authorization": f"token {token}"}

data = {
    "name": "prompt-vault-tool",
    "description": "CLI to manage your prompt library in a private git repo",
    "private": False,
    "auto_init": False,
}

r = requests.post("https://api.github.com/user/repos", headers=headers, json=data)
print(f"Status: {r.status_code}")
if r.status_code == 201:
    print(f"Created: {r.json()['html_url']}")
else:
    print(f"Error: {r.json().get('message', r.text)}")
