import os
from pathlib import Path
from .git import VAULT_DIR


def search_vault(query):
    """Search the vault for prompts matching the query."""
    if not VAULT_DIR.exists():
        return []

    query_lower = query.lower()
    query_terms = query_lower.split()
    results = []

    # Walk through all .md files
    for root, dirs, files in os.walk(VAULT_DIR):
        # Skip .git directory
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            if not file.endswith(".md"):
                continue

            filepath = Path(root) / file
            rel_path = filepath.relative_to(VAULT_DIR)

            # Check filename match
            filename_match = any(term in file.lower() for term in query_terms)

            # Check path match
            path_match = any(term in str(rel_path).lower() for term in query_terms)

            # Check content match
            content_match = False
            preview = ""
            try:
                content = filepath.read_text(encoding="utf-8")
                content_lower = content.lower()

                # Check if any query term is in content
                if any(term in content_lower for term in query_terms):
                    content_match = True
                    # Get first few lines as preview
                    lines = content.strip().split("\n")
                    preview = "\n".join(lines[:3])
            except Exception:
                pass

            # If any match, add to results
            if filename_match or path_match or content_match:
                results.append({
                    "path": str(rel_path),
                    "preview": preview
                })

    return results


def format_results(results, query):
    """Format search results for display."""
    if not results:
        return f"No prompts found matching '{query}'"

    output = [f"Found {len(results)} prompt(s) matching '{query}':\n"]

    for result in results:
        output.append(f"{result['path']}")
        if result['preview']:
            # Indent preview
            for line in result['preview'].split("\n"):
                output.append(f"  {line}")
        output.append("")

    return "\n".join(output)
