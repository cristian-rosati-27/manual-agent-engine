# ui/chat_panel.py

"""Chat panel – manual conversational workflow."""

import streamlit as st
import streamlit.components.v1 as components

from core.parser import parse_llm_response
from state.session import save_chat


# ===========================================================================
# Public entry point
# ===========================================================================

def render_chat_panel() -> None:
    _section_header()
    st.divider()
    _section_messages()
    st.divider()
    _section_turn_input()

    # Auto-scroll to bottom after every render
    components.html(
        """
        <script>
        (function() {
            var main = window.parent.document.querySelector('section.main');
            if (main) main.scrollTo({top: main.scrollHeight, behavior: 'smooth'});
        })();
        </script>
        """,
        height=0,
    )


# ===========================================================================
# Header
# ===========================================================================

def _section_header() -> None:
    col_name, col_clear = st.columns([8, 1])

    with col_name:
        name: str = st.text_input(
            "chat_name",
            value=st.session_state.get("current_chat_name", "Untitled Chat"),
            label_visibility="collapsed",
            placeholder="Chat name…",
            key="chat_name_input",
        )
        if name != st.session_state.current_chat_name:
            st.session_state.current_chat_name = name

    with col_clear:
        if st.button("🗑️", use_container_width=True, key="clear_chat_btn"):
            st.session_state.messages = []
            st.session_state.pending_patches = []
            st.rerun()


# ===========================================================================
# Messages
# ===========================================================================

def _section_messages() -> None:
    messages: list[dict] = st.session_state.messages

    if not messages:
        st.info(
            "No conversation yet.\n\n"
            "**Workflow**\n"
            "1. Set the work directory and click **✅ Set & Build**.\n"
            "2. Your message is pre-filled — add your request and send.\n"
            "3. Copy the full message, paste it to your LLM, paste the response back.\n"
            "4. Patches are extracted automatically → review in **Pending Patches**."
        )
        return

    for i, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "user":
                _copy_button(msg["content"], uid=f"user_{i}")


# ===========================================================================
# Copy button  (via components.html to avoid Streamlit HTML sanitisation)
# ===========================================================================

def _copy_button(text: str, uid: str) -> None:
    safe = _html_escape(text)
    components.html(
        f"""
        <textarea id="d_{uid}" style="display:none">{safe}</textarea>
        <button id="b_{uid}" onclick="
            var t = document.getElementById('d_{uid}').value;
            navigator.clipboard.writeText(t)
              .then(function() {{
                document.getElementById('b_{uid}').innerText = '✅ Copied!';
                setTimeout(function() {{
                  document.getElementById('b_{uid}').innerText = '📋 Copy message';
                }}, 2000);
              }})
              .catch(function(e) {{ alert('Copy failed: ' + e); }});
        " style="
            padding:2px 10px;
            background:transparent; color:#888;
            border:1px solid #444; border-radius:4px;
            cursor:pointer; font-size:0.75rem;
        ">📋 Copy message</button>
        """,
        height=32,
    )


def _html_escape(text: str) -> str:
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ===========================================================================
# Input routing
# ===========================================================================

def _section_turn_input() -> None:
    messages: list[dict] = st.session_state.messages
    expecting_assistant = len(messages) > 0 and messages[-1]["role"] == "user"

    if expecting_assistant:
        _assistant_input()
    else:
        _user_input()


# ===========================================================================
# User input
# ===========================================================================

def _user_input() -> None:
    prefill: str = st.session_state.get("prefill_user_message", "")

    if prefill:
        st.markdown("**👤 User Message** — edit then send")

        # Key includes a hash of the prefill so it re-mounts when a new
        # prompt is injected (avoids Streamlit ignoring the new value)
        area_key = f"prefill_textarea_{abs(hash(prefill)) % 10_000}"

        edited = st.text_area(
            "Message",
            value=prefill,
            height=220,
            label_visibility="collapsed",
            key=area_key,
        )

        col_send, col_discard = st.columns([3, 1])
        with col_send:
            if st.button("➤ Send", type="primary", use_container_width=True, key="send_prefill_btn"):
                if edited.strip():
                    st.session_state.messages.append({"role": "user", "content": edited.strip()})
                    st.session_state.pop("prefill_user_message", None)
                    save_chat()
                    st.rerun()
        with col_discard:
            if st.button("✕ Discard", use_container_width=True, key="discard_prefill_btn"):
                st.session_state.pop("prefill_user_message", None)
                st.rerun()
    else:
        # st.chat_input: Enter sends, Shift+Enter = newline — native browser behaviour
        prompt = st.chat_input("Write your message…")
        if prompt and prompt.strip():
            st.session_state.messages.append({"role": "user", "content": prompt.strip()})
            save_chat()
            st.rerun()


# ===========================================================================
# Assistant input
# ===========================================================================

def _assistant_input() -> None:
    st.markdown("**🤖 LLM Response** — paste and press Enter to send")
    response = st.chat_input("Paste the LLM response…")

    if response and response.strip():
        clean = response.strip()
        st.session_state.messages.append({"role": "assistant", "content": clean})
        _extract_patches(clean)
        save_chat()
        st.rerun()


# ===========================================================================
# Patch extraction
# ===========================================================================

def _extract_patches(response: str) -> None:
    patches = parse_llm_response(response)

    if not patches:
        st.toast("No file operations found in response.", icon="ℹ️")
        return

    new_patches = [
        {"type": p.type, "path": p.path, "content": p.content}
        for p in patches
    ]
    st.session_state.pending_patches.extend(new_patches)
    st.toast(f"Extracted {len(new_patches)} patch(es) → check Pending Patches.", icon="📦")