import json
from datetime import datetime

from .git import CONFIG_DIR

STATE_FILE = CONFIG_DIR / "state.json"
MAX_RECENT = 20


def load_state():
    if not STATE_FILE.exists():
        return {"favorites": [], "recent": []}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if "favorites" not in data:
            data["favorites"] = []
        if "recent" not in data:
            data["recent"] = []
        return data
    except (json.JSONDecodeError, OSError):
        return {"favorites": [], "recent": []}


def save_state(state):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def add_recent(path):
    """Record that a prompt was just used."""
    state = load_state()
    state["recent"] = [r for r in state["recent"] if r.get("path") != path]
    state["recent"].insert(0, {"path": path, "ts": datetime.now().isoformat()})
    state["recent"] = state["recent"][:MAX_RECENT]
    save_state(state)


def add_favorite(path):
    state = load_state()
    if path not in state["favorites"]:
        state["favorites"].append(path)
        save_state(state)
        return True
    return False


def remove_favorite(path):
    state = load_state()
    if path in state["favorites"]:
        state["favorites"].remove(path)
        save_state(state)
        return True
    return False
