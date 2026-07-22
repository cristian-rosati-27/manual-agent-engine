# core/patch_applier.py

"""Apply and revert file patches, maintaining version history."""

import os

import streamlit as st

from core.file_manager import delete_file, read_file, write_file
from core.version_history import HistoryEntry, PatchRecord, VersionHistory, snapshot_git


def apply_single_patch(index: int) -> str | None:
    """Apply pending patch at *index*. Returns an error string on failure."""
    patches = st.session_state.pending_patches
    if index >= len(patches):
        return "Patch index out of range."

    patch = patches[index]
    error = _execute_patch(patch, st.session_state.workdir)
    if error:
        return error

    patches.pop(index)
    return None


def apply_all_patches() -> str | None:
    """Apply every pending patch as a single history entry."""
    patches = st.session_state.pending_patches
    if not patches:
        return None

    workdir = st.session_state.workdir
    records: list[PatchRecord] = []

    for patch in patches:
        record = _build_record(patch, workdir)
        ok = _do_apply(record)
        if not ok:
            return f"Failed to apply patch for {record.path}"
        records.append(record)

    # Build a description listing all affected files
    parts = []
    for r in records:
        rel = os.path.relpath(r.path, workdir)
        if r.type == "delete":
            parts.append(f"🗑️ {rel}")
        elif r.old_content is None:
            parts.append(f"🆕 {rel}")
        else:
            parts.append(f"✏️ {rel}")
    description = "  |  ".join(parts)

    _commit_to_history(records, description)
    st.session_state.pending_patches = []
    return None


def undo_to(target_head: int) -> None:
    """Revert history entries from current head down to target_head + 1."""
    vh: VersionHistory = st.session_state.version_history
    while vh.head > target_head:
        entry = vh.entries[vh.head]
        for record in reversed(entry.patches):
            _revert_record(record)
        vh.head -= 1


def redo_to(target_head: int) -> None:
    """Re-apply history entries from head + 1 up to target_head."""
    vh: VersionHistory = st.session_state.version_history
    while vh.head < target_head:
        vh.head += 1
        entry = vh.entries[vh.head]
        for record in entry.patches:
            _do_apply(record)


def _execute_patch(patch: dict, workdir: str) -> str | None:
    record = _build_record(patch, workdir)
    ok = _do_apply(record)
    if not ok:
        return f"Failed to apply: {record.path}"
    _commit_to_history([record], _describe_record(record, workdir))
    return None


def _build_record(patch: dict, workdir: str) -> PatchRecord:
    patch_type = patch.get("type", "write")
    path = patch.get("path", "")
    content = patch.get("content", "")
    full_path = _resolve(path, workdir)
    old_content = read_file(full_path)
    return PatchRecord(
        type=patch_type,
        path=full_path,
        new_content=content if patch_type == "write" else None,
        old_content=old_content,
    )


def _do_apply(record: PatchRecord) -> bool:
    if record.type == "write":
        return write_file(record.path, record.new_content or "")
    elif record.type == "delete":
        return delete_file(record.path)
    return False


def _revert_record(record: PatchRecord) -> None:
    if record.old_content is None:
        delete_file(record.path)
    else:
        write_file(record.path, record.old_content)


def _commit_to_history(records: list[PatchRecord], description: str) -> None:
    workdir = st.session_state.workdir
    commit_hash = snapshot_git(workdir, description)
    entry = HistoryEntry(description=description, patches=records, git_commit_hash=commit_hash)
    st.session_state.version_history.commit(entry)


def _describe_record(record: PatchRecord, workdir: str) -> str:
    rel = os.path.relpath(record.path, workdir)
    if record.type == "delete":
        return f"🗑️ {rel}"
    verb = "🆕" if record.old_content is None else "✏️"
    return f"{verb} {rel}"


def _resolve(path: str, workdir: str) -> str:
    return path if os.path.isabs(path) else os.path.join(workdir, path)