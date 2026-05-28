"""Version history with linear undo / redo.

Model
-----
* ``entries``  – ordered list of committed HistoryEntry objects (oldest first).
* ``head``     – index of the last *applied* entry; -1 means nothing applied.

Invariant: entries[0..head] are applied to disk; entries[head+1..] have been
undone and can be re-applied with redo.

Undo to index *i*: revert entries from ``head`` down to ``i+1``, set head = i.
Redo to index *i*: apply entries from ``head+1`` up to ``i``, set head = i.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PatchRecord:
    """Atomic record of one file operation, including enough info to revert."""

    type: str             # "write" | "delete"
    path: str             # absolute path on disk
    new_content: str | None = None   # content written  (write ops)
    old_content: str | None = None   # content before   (None ↔ file was absent)


@dataclass
class HistoryEntry:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%H:%M:%S")
    )
    description: str = ""
    patches: list[PatchRecord] = field(default_factory=list)


class VersionHistory:
    def __init__(self) -> None:
        self.entries: list[HistoryEntry] = []
        self.head: int = -1

    # ------------------------------------------------------------------
    # Mutation helpers (do not touch the filesystem)
    # ------------------------------------------------------------------

    def commit(self, entry: HistoryEntry) -> None:
        """Append *entry* as a new commit, discarding any redo tail."""
        self.entries = self.entries[: self.head + 1]
        self.entries.append(entry)
        self.head = len(self.entries) - 1

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    @property
    def can_undo(self) -> bool:
        return self.head >= 0

    @property
    def can_redo(self) -> bool:
        return self.head < len(self.entries) - 1

    def is_applied(self, index: int) -> bool:
        return index <= self.head

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "head": self.head,
            "entries": [
                {
                    "id": e.id,
                    "timestamp": e.timestamp,
                    "description": e.description,
                    "patches": [
                        {
                            "type": p.type,
                            "path": p.path,
                            "new_content": p.new_content,
                            "old_content": p.old_content,
                        }
                        for p in e.patches
                    ],
                }
                for e in self.entries
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VersionHistory":
        vh = cls()
        vh.head = data.get("head", -1)
        for raw in data.get("entries", []):
            entry = HistoryEntry(
                id=raw["id"],
                timestamp=raw["timestamp"],
                description=raw["description"],
                patches=[
                    PatchRecord(
                        type=p["type"],
                        path=p["path"],
                        new_content=p.get("new_content"),
                        old_content=p.get("old_content"),
                    )
                    for p in raw.get("patches", [])
                ],
            )
            vh.entries.append(entry)
        return vh
