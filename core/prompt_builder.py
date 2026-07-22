"""Build the context prompt from a working directory based on selected paths.

The assembled prompt has three parts (in order):
1. The system prompt (if non-empty).
2. A textual directory tree filtered to the selected files.
3. The full content of each matching file.
"""

import os
from pathlib import Path

from config.defaults import SKIP_DIRS


def build_tree(root: str, selected_paths: dict[str, bool], prefix: str = "") -> str:
    """Return an ASCII directory tree, filtering to *selected_paths*."""
    try:
        raw = list(os.scandir(root))
    except PermissionError:
        return ""

    entries = sorted(raw, key=lambda e: (not e.is_dir(), e.name.lower()))

    visible = []
    for entry in entries:
        if entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue
            
        # If it's a directory, we need to check if any children are selected
        if entry.is_dir():
            subtree = build_tree(entry.path, selected_paths)
            if subtree or selected_paths.get(entry.path, True): 
                visible.append((entry, subtree))
        else:
            # If it's a file, check if it's selected
            if selected_paths.get(entry.path, True):
                visible.append((entry, None))

    lines: list[str] = []
    for i, (entry, subtree) in enumerate(visible):
        is_last = i == len(visible) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if subtree:
            child_prefix = "    " if is_last else "│   "
            lines.append(build_tree(entry.path, selected_paths, prefix + child_prefix))

    return "\n".join(filter(None, lines))


def collect_files(
    root: str, selected_paths: dict[str, bool], max_kb: int = 500
) -> list[tuple[str, str]]:
    """Return ``[(relative_path, content), ...]`` for all selected files."""
    results: list[tuple[str, str]] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS
        )

        for filename in sorted(filenames):
            full = os.path.join(dirpath, filename)
            
            # Skip if file is explicitly unselected
            if not selected_paths.get(full, True):
                continue
                
            rel = os.path.relpath(full, root)

            try:
                size_kb = os.path.getsize(full) / 1024
            except OSError:
                continue

            if size_kb > max_kb:
                results.append((rel, f"[Skipped – file too large: {size_kb:.0f} KB]"))
                continue

            content = _read(full)
            results.append((rel, content))

    return results


def build_prompt(
    root: str,
    selected_paths: dict[str, bool] = None,
    system_prompt: str = "",
    max_kb: int = 500,
) -> str:
    """Assemble the full prompt string ready to hand to an LLM."""
    if selected_paths is None:
        selected_paths = {}
        
    parts: list[str] = []

    # 1 – system prompt
    if system_prompt.strip():
        parts.append(system_prompt.strip())
        parts.append("")

    # 2 – directory tree
    root_name = os.path.basename(os.path.abspath(root))
    tree = build_tree(root, selected_paths)
    parts += [
        "## Codebase Structure",
        f"```\n{root_name}/\n{tree}\n```",
        "",
    ]

    # 3 – file contents
    parts.append("## Files")
    files = collect_files(root, selected_paths, max_kb)

    if not files:
        parts.append("_No files selected or found._")
    else:
        for rel_path, content in files:
            lang = Path(rel_path).suffix.lstrip(".")
            parts += [
                f"### `{rel_path}`",
                f"```{lang}",
                content,
                "```",
                "",
            ]

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except Exception as exc:
        return f"[Error reading file: {exc}]"
