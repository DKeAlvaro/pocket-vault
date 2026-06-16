import os
import shutil
import subprocess
from pathlib import Path
from .git import VAULT_DIR, commit_and_push


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


def add_prompt(path):
    """Create a new prompt file and open it in editor."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    # Ensure .md extension
    if not path.endswith(".md"):
        path = path + ".md"

    filepath = VAULT_DIR / path

    # Create parent directories
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Create empty file
    filepath.touch()

    # Open in editor
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
        return True, content
    except Exception as e:
        return False, f"Error reading file: {e}"


def use_prompt(path):
    """Copy a prompt to the current directory."""
    if not VAULT_DIR.exists():
        return False, "Vault not initialized. Run 'pv auth' first."

    # Ensure .md extension
    if not path.endswith(".md"):
        path = path + ".md"

    source = VAULT_DIR / path

    if not source.exists():
        return False, f"File not found: {path}"

    # Copy to current directory
    dest = Path.cwd() / source.name
    shutil.copy2(source, dest)

    return True, f"Copied to {dest}"


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
