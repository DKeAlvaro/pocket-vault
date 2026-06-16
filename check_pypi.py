import requests

r = requests.get("https://pypi.org/pypi/prompt-vault/json")
if r.status_code == 404:
    print("Available")
else:
    print(f"Taken by: {r.json()['info']['name']} {r.json()['info']['version']}")
