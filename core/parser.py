# core/parser.py

"""Parse LLM responses for file operation commands.

Supported syntax
----------------
Create / overwrite a file:
    <<<FILE:path/to/file.ext>>>
    content here
    <<<END_FILE>>>

Delete a file:
    <<<DELETE:path/to/file.ext>>>
"""

import re
from dataclasses import dataclass
from typing import Literal


@dataclass
class FilePatch:
    type: Literal["write", "delete"]
    path: str
    content: str = ""


# ===========================================================================
# Regex patterns
# ===========================================================================

# Supports:
# <<<FILE:path>>>
# content
# <<<END_FILE>>>
#
# Also supports optional markdown fences around the whole block:
#
# ```python
# <<<FILE:path>>>
# ...
# <<<END_FILE>>>
# ```
#
# which is exactly what happened in your failing test.

_FILE_RE = re.compile(
    r"(?:```[a-zA-Z0-9_-]*\n)?"
    r"<<<FILE:([^\n>]+)>>>\n?"
    r"(.*?)"
    r"<<<END_FILE>>>"
    r"(?:\n```)?",
    re.DOTALL,
)

_DELETE_RE = re.compile(
    r"<<<DELETE:([^\n>]+)>>>"
)


# ===========================================================================
# Public API
# ===========================================================================

def parse_llm_response(response: str) -> list[FilePatch]:
    """Return ordered FilePatch objects extracted from *response*."""

    patches: list[FilePatch] = []
    seen_paths: set[str] = set()

    # -------------------------------------------------------------------
    # FILE blocks
    # -------------------------------------------------------------------

    for match in _FILE_RE.finditer(response):
        path = match.group(1).strip()
        content = match.group(2)

        if content.endswith("\n"):
            content = content[:-1]

        if path not in seen_paths:
            patches.append(
                FilePatch(
                    type="write",
                    path=path,
                    content=content,
                )
            )

            seen_paths.add(path)

    # -------------------------------------------------------------------
    # DELETE blocks
    # -------------------------------------------------------------------

    for match in _DELETE_RE.finditer(response):
        path = match.group(1).strip()

        if path not in seen_paths:
            patches.append(
                FilePatch(
                    type="delete",
                    path=path,
                )
            )

            seen_paths.add(path)

    return patches