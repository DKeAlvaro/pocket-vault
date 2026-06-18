import os
import shutil
import subprocess
import sys
from pathlib import Path
from .git import VAULT_DIR, commit_and_push
from .state import add_recent, load_state


def get_editor():
    """Get the user's preferred editor."""
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if editor:
        return editor
    # Windows default: use os.startfile (opens with default app)
    # Unix default: use nano or vim
    if os.name == "nt":
        return None
    return "nano" if shutil.which("nano") else "vim"


def open_in_editor(filepath):
    """Open a file in the user's editor."""
    editor = get_editor()
    if editor is None:
        # Windows: open with notepad (always available, blocking)
        subprocess.run(["notepad", str(filepath)])
    else:
        subprocess.run([editor, str(filepath)])


def add_prompt(path, content=None):
    """Create a new prompt file. If content is provided, write it directly.
    Otherwise, open the file in the user's editor."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    # Ensure .md extension
    if not path.endswith(".md"):
        path = path + ".md"

    filepath = VAULT_DIR / path

    # Create parent directories
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if content is not None:
        # Write content directly (non-interactive mode)
        filepath.write_text(content, encoding="utf-8")
    else:
        # Create empty file and open in editor
        filepath.touch()
        open_in_editor(filepath)

    # Commit and push
    success, message = commit_and_push(f"vault: add {path}")
    if not success:
        return False, message

    return True, f"Added {path}"


def edit_prompt(path):
    """Edit an existing prompt file."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    # Ensure .md extension
    if not path.endswith(".md"):
        path = path + ".md"

    filepath = VAULT_DIR / path

    if not filepath.exists():
        return False, f"File not found: {path}"

    # Open in editor
    open_in_editor(filepath)

    # Commit and push
    success, message = commit_and_push(f"vault: edit {path}")
    if not success:
        return False, message

    return True, f"Updated {path}"


def read_prompt(path):
    """Read and output a prompt's content."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    # Ensure .md extension
    if not path.endswith(".md"):
        path = path + ".md"

    filepath = VAULT_DIR / path

    if not filepath.exists():
        return False, f"File not found: {path}"

    try:
        content = filepath.read_text(encoding="utf-8")
        add_recent(path[:-3] if path.endswith(".md") else path)
        return True, content
    except Exception as e:
        return False, f"Error reading file: {e}"


def use_prompt(path, dest_name=None):
    """Copy a prompt to the current directory.

    If dest_name is given, save under that filename instead of the source's name.
    If the destination already exists, prompt the user to overwrite, append, or cancel.
    """
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    # Ensure .md extension
    if not path.endswith(".md"):
        path = path + ".md"

    source = VAULT_DIR / path

    if not source.exists():
        return False, f"File not found: {path}"

    if dest_name is None:
        dest_name = source.name
    elif not dest_name.endswith(".md"):
        dest_name = dest_name + ".md"

    dest = Path.cwd() / dest_name

    if dest.is_file():
        print(f"'{dest.name}' already exists in the current directory.")
        try:
            choice = input("Overwrite, append, or cancel? [o/a/c]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return False, "Cancelled"
        if choice in ("o", "overwrite"):
            pass
        elif choice in ("a", "append"):
            existing = dest.read_text(encoding="utf-8")
            new_content = source.read_text(encoding="utf-8")
            dest.write_text(existing.rstrip() + "\n\n" + new_content, encoding="utf-8")
            add_recent(path[:-3] if path.endswith(".md") else path)
            return True, f"Appended to {dest}"
        else:
            return False, "Cancelled"

    try:
        shutil.copy2(source, dest)
    except FileNotFoundError:
        return False, f"Destination directory does not exist: {dest.parent}"

    add_recent(path[:-3] if path.endswith(".md") else path)
    return True, f"Copied to {dest}"


def copy_prompt(path):
    """Copy a prompt's content to the system clipboard."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    # Ensure .md extension
    if not path.endswith(".md"):
        path = path + ".md"

    filepath = VAULT_DIR / path

    if not filepath.exists():
        return False, f"File not found: {path}"

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Error reading file: {e}"

    ok, err = _copy_to_clipboard(content)
    if not ok:
        return False, err

    add_recent(path[:-3] if path.endswith(".md") else path)
    return True, f"Copied {path} to clipboard"


def copy_folder(path):
    """Copy all .md files in a folder to the clipboard, concatenated with headers."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    folder_path = VAULT_DIR / path.rstrip("/")
    if not folder_path.exists() or not folder_path.is_dir():
        return False, f"Not a folder: {path}"

    md_files = sorted(folder_path.glob("*.md"))
    if not md_files:
        return False, f"No .md files in {path}"

    parts = []
    for f in md_files:
        name = f.stem
        parts.append(f"\n# {name}\n\n")
        parts.append(f.read_text(encoding="utf-8").rstrip())
    content = "\n".join(parts).rstrip() + "\n"

    ok, err = _copy_to_clipboard(content)
    if not ok:
        return False, err

    return True, f"Copied {len(md_files)} prompt(s) from {path.rstrip('/')}/ to clipboard"


def _copy_to_clipboard(content):
    """Copy content to the system clipboard. Returns (ok, error_message)."""
    if sys.platform == "win32":
        cmd = ["clip"]
    elif sys.platform == "darwin":
        cmd = ["pbcopy"]
    else:
        if shutil.which("xclip"):
            cmd = ["xclip", "-selection", "clipboard"]
        elif shutil.which("xsel"):
            cmd = ["xsel", "--clipboard", "--input"]
        else:
            return False, "No clipboard utility found. Install xclip or xsel on Linux."

    try:
        result = subprocess.run(
            cmd,
            input=content,
            text=True,
            encoding="utf-8",
            timeout=5,
        )
        if result.returncode != 0:
            return False, "Clipboard copy failed"
    except FileNotFoundError:
        return False, f"Clipboard command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, "Clipboard command timed out"
    except Exception as e:
        return False, f"Clipboard error: {e}"
    return True, None


def delete_prompt(path):
    """Delete a prompt file or folder."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    filepath = VAULT_DIR / path

    if not filepath.exists():
        # Try with .md extension
        filepath_md = VAULT_DIR / (path + ".md")
        if not filepath_md.exists():
            return False, f"File not found: {path}"
        filepath = filepath_md

    if filepath.is_dir():
        shutil.rmtree(filepath)
        success, message = commit_and_push(f"vault: delete {path}/")
    else:
        filepath.unlink()
        success, message = commit_and_push(f"vault: delete {filepath.name}")

    if not success:
        return False, message

    return True, f"Deleted {path}"


def browse_vault():
    """Show the vault structure."""
    if not VAULT_DIR.exists():
        return "Vault not initialized. Run 'pv auth' first."

    output = ["Vault structure:\n"]

    for root, dirs, files in os.walk(VAULT_DIR):
        # Skip .git directory
        if ".git" in dirs:
            dirs.remove(".git")

        # Calculate indentation level
        level = len(Path(root).relative_to(VAULT_DIR).parts)
        indent = "  " * level

        # Print directory name
        dir_name = Path(root).name
        if level > 0:
            output.append(f"{indent}{dir_name}/")

        # Print files
        for file in sorted(files):
            if file.endswith(".md"):
                output.append(f"{indent}  {file}")

    return "\n".join(output)


def list_all_paths():
    """List all .md file paths in the vault, relative to VAULT_DIR, without .md extension."""
    if not VAULT_DIR.exists():
        return []
    paths = []
    for root, dirs, files in os.walk(VAULT_DIR):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in sorted(files):
            if f.endswith(".md"):
                full = Path(root) / f
                rel = full.relative_to(VAULT_DIR)
                paths.append(rel.with_suffix("").as_posix())
    return sorted(paths)


def get_numbered_list():
    """Return ordered list of (num_str, path, is_favorite) tuples.

    Order: favorites first (flat, stable), then hierarchical tree of the rest.
    Recents are tracked but not shown — including them would shift numbers
    after every use, breaking the "memorize pv 1 = my style guide" workflow.
    """
    state = load_state()
    favorites = state.get("favorites", [])

    all_paths = list_all_paths()
    all_set = set(all_paths)

    favorites = [p for p in favorites if p in all_set]
    rest = sorted(p for p in all_paths if p not in favorites)

    items = []
    for i, path in enumerate(favorites, 1):
        items.append((str(i), path, True))

    tree_start = len(favorites) + 1
    items.extend(_build_tree_items(rest, start_num=tree_start))

    return items


def _build_tree_items(paths, start_num=1):
    """Build hierarchical numbered items from a flat list of paths.

    Top-level entries are numbered sequentially starting at start_num.
    Children of entry N are numbered N.1, N.2, ...
    Each item's path is the full path from the vault root. Folders end with '/'.
    """
    if not paths:
        return []

    root = {"_files": []}
    for path in paths:
        node = root
        parts = path.split("/")
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                node.setdefault("_files", []).append(part)
            else:
                node = node.setdefault(part, {"_files": []})

    items = []
    top_counter = [start_num - 1]

    def walk(node, path_prefix="", num_prefix=""):
        dirs = sorted([k for k in node if k != "_files"])
        files = sorted(node.get("_files", []))
        siblings = sorted(
            [(d, "dir") for d in dirs] + [(f, "file") for f in files],
            key=lambda x: x[0],
        )
        for idx, (name, kind) in enumerate(siblings, 1):
            if num_prefix:
                num = f"{num_prefix}.{idx}"
            else:
                top_counter[0] += 1
                num = str(top_counter[0])
            if kind == "dir":
                full_path = path_prefix + name + "/"
                items.append((num, full_path, False))
                walk(node[name], full_path, num)
            else:
                full_path = path_prefix + name
                items.append((num, full_path, False))

    walk(root)
    return items


def format_numbered_list(items):
    """Format the numbered list for display."""
    if not items:
        return "No prompts in vault. Run 'pv add <path>' to create one."

    lines = []
    for num, path, is_fav in items:
        marker = "* " if is_fav else "  "
        depth = num.count(".")
        indent = "    " * depth
        if path.endswith("/"):
            display = path
        else:
            display = path.rsplit("/", 1)[-1]
        lines.append(f"{marker}{num}  {indent}{display}")
    return "\n".join(lines)


def resolve_number_or_path(arg, items):
    """Resolve an arg to a path. If numeric (incl. hierarchical like "4.1"),
    look up in items. Otherwise return arg unchanged.

    Returns (path, None) on success or (None, error_message) on failure.
    """
    import re
    if re.match(r"^\d+(\.\d+)*$", arg):
        for num, path, _ in items:
            if num == arg:
                return path, None
        return None, f"Invalid number: {arg}. Run 'pv' to see available prompts."
    return arg, None
