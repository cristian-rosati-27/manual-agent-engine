"""Build the context prompt from a working directory.

The assembled prompt has three parts (in order):
1. The system prompt (if non-empty).
2. A textual directory tree filtered to the selected extensions.
3. The full content of each matching file.
"""

import os
from pathlib import Path

from config.defaults import SKIP_DIRS


def build_tree(root: str, extensions: list[str], prefix: str = "") -> str:
    """Return an ASCII directory tree, filtering to *extensions*."""
    try:
        raw = list(os.scandir(root))
    except PermissionError:
        return ""

    entries = sorted(raw, key=lambda e: (not e.is_dir(), e.name.lower()))

    # Keep dirs that (recursively) contain matching files; keep matching files.
    visible = []
    for entry in entries:
        if entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue
        if entry.is_dir():
            subtree = build_tree(entry.path, extensions)
            if subtree:  # only include non-empty dirs
                visible.append((entry, subtree))
        elif any(entry.name.endswith(ext) for ext in extensions):
            visible.append((entry, None))

    lines: list[str] = []
    for i, (entry, subtree) in enumerate(visible):
        is_last = i == len(visible) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if subtree is not None:
            child_prefix = "    " if is_last else "│   "
            lines.append(build_tree(entry.path, extensions, prefix + child_prefix))

    return "\n".join(filter(None, lines))


def collect_files(
    root: str, extensions: list[str], max_kb: int = 500
) -> list[tuple[str, str]]:
    """Return ``[(relative_path, content), ...]`` for all matching files."""
    results: list[tuple[str, str]] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune in-place so os.walk won't recurse into ignored dirs.
        dirnames[:] = sorted(
            d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS
        )

        for filename in sorted(filenames):
            if not any(filename.endswith(ext) for ext in extensions):
                continue

            full = os.path.join(dirpath, filename)
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
    extensions: list[str],
    system_prompt: str = "",
    max_kb: int = 500,
) -> str:
    """Assemble the full prompt string ready to hand to an LLM."""
    parts: list[str] = []

    # 1 – system prompt
    if system_prompt.strip():
        parts.append(system_prompt.strip())
        parts.append("")

    # 2 – directory tree
    root_name = os.path.basename(os.path.abspath(root))
    tree = build_tree(root, extensions)
    parts += [
        "## Codebase Structure",
        f"```\n{root_name}/\n{tree}\n```",
        "",
    ]

    # 3 – file contents
    parts.append("## Files")
    files = collect_files(root, extensions, max_kb)

    if not files:
        parts.append("_No files found with the selected extensions._")
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
