# ui/chats_tab.py

"""Chats tab – browse, load, and delete conversations."""

from datetime import datetime

import streamlit as st

from state.session import delete_chat, list_chats, load_chat, new_chat


# ===========================================================================
# Public entry point
# ===========================================================================

def render_chats_tab() -> None:
    st.markdown("#### 💬 Chats")

    _section_actions()

    st.divider()

    _section_saved_chats()


# ===========================================================================
# Section: Actions
# ===========================================================================

def _section_actions() -> None:
    if st.button(
        "➕ New Chat",
        use_container_width=True,
        key="new_chat_sidebar_btn",
    ):
        new_chat()
        st.rerun()


# ===========================================================================
# Section: Saved Chats
# ===========================================================================

def _section_saved_chats() -> None:
    chats = list_chats()

    if not chats:
        st.caption(
            "No saved chats yet."
        )
        return

    for chat in chats:
        _render_chat_card(chat)


# ===========================================================================
# Internal helpers
# ===========================================================================

def _render_chat_card(chat: dict) -> None:
    chat_id: str = chat.get("id", "")
    current_id: str | None = st.session_state.get("current_chat_id")

    is_active = chat_id == current_id

    name: str = chat.get("name", "Untitled Chat")
    message_count: int = chat.get("message_count", 0)

    created_at = _format_created_at(chat.get("created_at", ""))

    turns = max(message_count // 2, 0)

    indicator = "🟢 " if is_active else ""

    with st.container(border=True):
        st.markdown(
            f"{indicator}**{name}**  \n"
            f"<small>{created_at} · "
            f"{turns} turn{'s' if turns != 1 else ''}</small>",
            unsafe_allow_html=True,
        )

        col_load, col_delete = st.columns([3, 1])

        with col_load:
            label = "✓ Active" if is_active else "📂 Load"

            if st.button(
                label,
                use_container_width=True,
                key=f"load_chat_{chat_id}",
                disabled=is_active,
            ):
                ok = load_chat(chat_id)

                if ok:
                    st.rerun()

                st.error("Failed to load chat.")

        with col_delete:
            if st.button(
                "🗑️",
                use_container_width=True,
                help="Delete chat",
                key=f"delete_chat_{chat_id}",
            ):
                ok = delete_chat(chat_id)

                if ok:
                    if is_active:
                        new_chat()

                    st.rerun()

                st.error("Failed to delete chat.")


def _format_created_at(value: str) -> str:
    if not value:
        return "—"

    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return value[:16]