# ui/chat_panel.py

"""Chat panel – manual conversational workflow."""

import streamlit as st
import streamlit.components.v1 as components

from core.parser import parse_llm_response
from state.session import save_chat
from config.defaults import DEFAULT_SYSTEM_PROMPT


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
            save_chat()

    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_chat_btn"):
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
            "1. Set the work directory and click **🚀 Inject Context**.\n"
            "2. Your message is pre-filled — add your request and send.\n"
            "3. Copy the full message, paste it to your LLM, paste the response back.\n"
            "4. Patches are extracted automatically → review in **Tool Changes**."
        )
        return

    if "edit_message_index" not in st.session_state:
        st.session_state.edit_message_index = None

    for i, msg in enumerate(messages):
        role = msg["role"]
        
        with st.chat_message(role):
            if st.session_state.edit_message_index == i:
                new_content = st.text_area("Edit Message", value=msg["content"], height=200, key=f"edit_area_{i}")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("Save", key=f"save_edit_{i}"):
                        st.session_state.messages[i]["content"] = new_content
                        st.session_state.messages = st.session_state.messages[:i+1]
                        st.session_state.edit_message_index = None
                        save_chat()
                        st.rerun()
                with col_cancel:
                    if st.button("Cancel", key=f"cancel_edit_{i}"):
                        st.session_state.edit_message_index = None
                        st.rerun()
            else:
                st.markdown(msg["content"])
                
                if "attachments" in msg and msg["attachments"]:
                    for att in msg["attachments"]:
                        st.caption(f"📎 {att['name']} ({att['size']} bytes)")
                
                msg_tokens = len(msg["content"]) // 4
                
                # Format text for copy
                copy_text = msg["content"]
                
                # If first message, prepend all prompts
                if i == 0 and role == "user":
                    sys_prompt = st.session_state.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
                    tool_prompt = st.session_state.get("tool_prompt_textarea", "")
                    inj_prompt = st.session_state.get("injection_prompt_textarea", "")
                    caveman = st.session_state.get("caveman_mode", False)
                    skills = st.session_state.get("skills", [])
                    
                    full_prompt_parts = []
                    if sys_prompt: full_prompt_parts.append(f"System Prompt:\n{sys_prompt}")
                    if tool_prompt: full_prompt_parts.append(f"Tool Guidelines:\n{tool_prompt}")
                    
                    for skill in skills:
                        full_prompt_parts.append(f"Skill: {skill['name']}\n{skill['content']}")
                        
                    if inj_prompt: full_prompt_parts.append(f"Injection Prompt:\n{inj_prompt}")
                    if caveman: full_prompt_parts.append("Caveman Mode: Speak like a caveman, be extremely concise, omit pleasantries, use as few words as possible to save tokens.")
                    
                    if full_prompt_parts:
                        prompts_combined = "\n\n".join(full_prompt_parts)
                        copy_text = f"{prompts_combined}\n\n---\n\n{copy_text}"
                
                col1, col2, col3, col_space = st.columns([1, 1, 3, 9])
                with col1:
                    _copy_button(copy_text, uid=f"msg_{i}")
                with col2:
                    if st.button("✏️", key=f"edit_btn_{i}", help="Edit message"):
                        st.session_state.edit_message_index = i
                        st.rerun()
                with col3:
                    st.caption(f"_{msg_tokens:,} tokens_")

    total_tokens = sum(len(m["content"]) // 4 for m in messages)
    st.caption(f"**Total conversation:** ~{total_tokens:,} tokens")


# ===========================================================================
# Copy button  (via components.html to avoid Streamlit HTML sanitisation)
# ===========================================================================

def _copy_button(text: str, uid: str) -> None:
    safe = _html_escape(text)
    components.html(
        f"""
        <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            height: 100%;
        }}
        button {{
            padding: 4px 8px;
            background: transparent;
            color: #888;
            border: 1px solid #444;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            margin-top: 10px;
        }}
        </style>
        <textarea id="d_{uid}" style="display:none">{safe}</textarea>
        <button id="b_{uid}" onclick="
            var t = document.getElementById('d_{uid}').value;
            navigator.clipboard.writeText(t)
              .then(function() {{
                document.getElementById('b_{uid}').innerText = '✅';
                setTimeout(function() {{
                  document.getElementById('b_{uid}').innerText = '📋';
                }}, 2000);
              }})
              .catch(function(e) {{ alert('Copy failed: ' + e); }});
        ">📋</button>
        """,
        height=45,
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
    uploaded_files = st.file_uploader("Attach files", accept_multiple_files=True, key="file_uploader")
    attachments = []
    if uploaded_files:
        for f in uploaded_files:
            size_mb = f.size / (1024 * 1024)
            attachments.append({"name": f.name, "size": f.size})
            if size_mb > 100:
                st.warning(f"This file is {size_mb:.1f} MB. It may consume a large amount of context.")
            if f.name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.zip', '.tar', '.gz', '.pdf')):
                st.info(f"Binary file detected ({f.name}). It won't be injected into context unless explicitly requested.")
    
    st.session_state.current_attachments = attachments

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
                    msg = {"role": "user", "content": edited.strip()}
                    if st.session_state.current_attachments:
                        msg["attachments"] = st.session_state.current_attachments
                    st.session_state.messages.append(msg)
                    st.session_state.pop("prefill_user_message", None)
                    save_chat()
                    st.rerun()
        with col_discard:
            if st.button("✕ Discard", use_container_width=True, key="discard_prefill_btn"):
                st.session_state.pop("prefill_user_message", None)
                st.rerun()
    else:
        prompt = st.chat_input("Write your message…")
        if prompt and prompt.strip():
            msg = {"role": "user", "content": prompt.strip()}
            if st.session_state.current_attachments:
                msg["attachments"] = st.session_state.current_attachments
            st.session_state.messages.append(msg)
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
        msg = {"role": "assistant", "content": clean}
        if st.session_state.current_attachments:
            msg["attachments"] = st.session_state.current_attachments
        st.session_state.messages.append(msg)
        
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