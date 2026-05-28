"""Session state management and chat persistence.

All `st.session_state` keys used by the app are initialised here and only here.
Chat data is persisted to JSON files in ``data/chats/``.
"""

import json
import os
import uuid
from datetime import datetime

import streamlit as st

from config.defaults import (
    CHATS_DIR,
    DEFAULT_EXTENSIONS,
    DEFAULT_SYSTEM_PROMPT,
    MAX_FILE_SIZE_KB,
)
from core.version_history import VersionHistory


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_session() -> None:
    """Idempotent – safe to call on every rerun."""
    _default("workdir", "")                   # empty = not yet chosen
    _default("extensions", list(DEFAULT_EXTENSIONS))
    _default("system_prompt", DEFAULT_SYSTEM_PROMPT)
    _default("max_file_size_kb", MAX_FILE_SIZE_KB)
    _default("messages", [])                  # list[dict[role, content]]
    _default("pending_patches", [])           # list[dict] from parser
    _default("version_history", VersionHistory())
    _default("current_chat_id", str(uuid.uuid4()))
    _default("current_chat_name", f"Chat {datetime.now().strftime('%d/%m %H:%M')}")
    _default("waiting_for_llm", False)        # True when LLM response is pending

    os.makedirs(CHATS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Chat lifecycle
# ---------------------------------------------------------------------------

def new_chat() -> None:
    """Reset the workspace for a fresh conversation."""
    st.session_state.messages = []
    st.session_state.pending_patches = []
    st.session_state.version_history = VersionHistory()
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.current_chat_name = (
        f"Chat {datetime.now().strftime('%d/%m %H:%M')}"
    )
    st.session_state.waiting_for_llm = False
    st.session_state.pop("cached_prompt", None)


def save_chat() -> bool:
    """Persist the current chat to disk. Returns False if there's nothing to save."""
    if not st.session_state.messages:
        return False

    os.makedirs(CHATS_DIR, exist_ok=True)

    if not st.session_state.current_chat_id:
        st.session_state.current_chat_id = str(uuid.uuid4())

    payload = {
        "id": st.session_state.current_chat_id,
        "name": st.session_state.current_chat_name,
        "created_at": datetime.now().isoformat(),
        "workdir": st.session_state.workdir,
        "messages": st.session_state.messages,
        "version_history": st.session_state.version_history.to_dict(),
    }

    path = _chat_path(st.session_state.current_chat_id)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return True


def load_chat(chat_id: str) -> bool:
    """Load a persisted chat into session state. Returns False on error."""
    path = _chat_path(chat_id)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return False

    st.session_state.messages = data.get("messages", [])
    st.session_state.current_chat_id = data.get("id")
    st.session_state.current_chat_name = data.get("name", "Untitled")
    st.session_state.workdir = data.get("workdir", st.session_state.workdir)
    st.session_state.version_history = VersionHistory.from_dict(
        data.get("version_history", {})
    )
    st.session_state.pending_patches = []
    st.session_state.waiting_for_llm = False
    st.session_state.pop("cached_prompt", None)
    return True


def delete_chat(chat_id: str) -> bool:
    try:
        os.remove(_chat_path(chat_id))
        return True
    except Exception:
        return False


def list_chats() -> list[dict]:
    """Return chat metadata sorted newest-first."""
    os.makedirs(CHATS_DIR, exist_ok=True)
    chats = []
    for filename in sorted(os.listdir(CHATS_DIR), reverse=True):
        if not filename.endswith(".json"):
            continue
        try:
            with open(os.path.join(CHATS_DIR, filename), encoding="utf-8") as fh:
                data = json.load(fh)
            chats.append(
                {
                    "id": data.get("id", filename[:-5]),
                    "name": data.get("name", "Untitled"),
                    "created_at": data.get("created_at", ""),
                    "message_count": len(data.get("messages", [])),
                }
            )
        except Exception:
            pass
    return chats


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _default(key: str, value) -> None:
    if key not in st.session_state:
        st.session_state[key] = value


def _chat_path(chat_id: str) -> str:
    return os.path.join(CHATS_DIR, f"{chat_id}.json")