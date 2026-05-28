# ui/workdir_tab.py

"""WorkDir tab – the main left-panel section."""

import os

import streamlit as st
import streamlit.components.v1 as components

from config.defaults import ALL_KNOWN_EXTENSIONS, MAX_FILE_SIZE_KB
from core.file_manager import file_exists
from core.patch_applier import apply_all_patches, apply_single_patch, redo_to, undo_to
from core.prompt_builder import build_prompt
from core.version_history import VersionHistory


# ===========================================================================
# Public entry point
# ===========================================================================

def render_workdir_tab() -> None:
    _section_workdir()
    st.divider()
    _section_extensions()
    st.divider()
    _section_context_preview()
    st.divider()
    _section_pending_patches()
    st.divider()
    _section_version_history()


# ===========================================================================
# Section: Work Directory
# ===========================================================================

def _section_workdir() -> None:
    st.markdown("#### 📁 Work Directory")

    new_dir = st.text_input(
        "dir",
        value=st.session_state.workdir,
        label_visibility="collapsed",
        placeholder="Absolute path to project root…",
        key="workdir_input",
    )

    col_set, col_build = st.columns(2)

    with col_set:
        if st.button("✅ Set & Build", use_container_width=True, key="set_workdir"):
            _set_workdir_and_build(new_dir.strip())

    with col_build:
        if st.button("🔄 Rebuild", use_container_width=True, key="build_prompt_workdir"):
            _set_workdir_and_build(new_dir.strip())

    if st.session_state.workdir and os.path.isdir(st.session_state.workdir):
        st.caption(f"✅ `{st.session_state.workdir}`")
    elif st.session_state.workdir:
        st.caption(f"⚠️ Path not found: `{st.session_state.workdir}`")
    else:
        st.caption("No directory set.")


def _set_workdir_and_build(path: str) -> None:
    if not path:
        st.toast("Enter a path first.", icon="⚠️")
        return
    if not os.path.isdir(path):
        st.toast(f"Directory not found: {path}", icon="⚠️")
        return
    st.session_state.workdir = path
    _build_and_inject_prompt()


# ===========================================================================
# Section: Extensions
# ===========================================================================

def _section_extensions() -> None:
    st.markdown("#### 🔍 File Extensions")

    selected = st.multiselect(
        "extensions",
        options=ALL_KNOWN_EXTENSIONS,
        default=st.session_state.extensions,
        label_visibility="collapsed",
        key="ext_multiselect",
    )

    if selected != st.session_state.extensions:
        st.session_state.extensions = selected
        st.session_state.pop("cached_prompt", None)

    col_custom, col_add = st.columns([3, 1])

    with col_custom:
        custom = st.text_input(
            "custom ext",
            placeholder="e.g. .vue",
            label_visibility="collapsed",
            key="custom_ext_input",
        )

    with col_add:
        if st.button("Add", use_container_width=True, key="add_custom_ext"):
            if custom:
                ext = custom if custom.startswith(".") else f".{custom}"
                if ext not in st.session_state.extensions:
                    st.session_state.extensions.append(ext)
                    st.session_state.pop("cached_prompt", None)
                    st.rerun()


# ===========================================================================
# Section: Context Preview
# ===========================================================================

def _section_context_preview() -> None:
    st.markdown("#### 📋 Context Preview")

    prompt = st.session_state.get("cached_prompt", "")

    if not prompt:
        st.caption("Prompt not built yet. Click **✅ Set & Build** or **🔄 Rebuild** above.")
        return

    token_estimate = len(prompt) // 4
    st.caption(f"~{token_estimate:,} tokens")

    # Copy button via components.html so it's never sanitised by Streamlit
    # We pass the text through a data attribute to avoid JS string escaping issues
    components.html(
        f"""
        <textarea id="__prompt_data" style="display:none">{_html_escape(prompt)}</textarea>
        <button id="cpbtn" onclick="
            var text = document.getElementById('__prompt_data').value;
            navigator.clipboard.writeText(text)
              .then(function() {{
                document.getElementById('cpbtn').innerText = '✅ Copied!';
                setTimeout(function() {{
                  document.getElementById('cpbtn').innerText = '📋 Copy prompt';
                }}, 2000);
              }})
              .catch(function(err) {{
                document.getElementById('cpbtn').innerText = '❌ ' + err;
              }});
        " style="
            width:100%; padding:6px 10px;
            background:#262730; color:#fafafa;
            border:1px solid #555; border-radius:6px;
            cursor:pointer; font-size:0.85rem;
        ">📋 Copy prompt</button>
        """,
        height=44,
    )

    with st.expander("Prompt preview", expanded=False):
        st.text_area(
            "prompt_preview_area",
            value=prompt,
            height=400,
            label_visibility="collapsed",
            key="prompt_preview_textarea",
        )


def _html_escape(text: str) -> str:
    """Escape text for safe embedding inside an HTML tag value."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ===========================================================================
# Prompt builder
# ===========================================================================

def _build_and_inject_prompt() -> None:
    with st.spinner("Building prompt…"):
        prompt = build_prompt(
            root=st.session_state.workdir,
            extensions=st.session_state.extensions,
            system_prompt=st.session_state.system_prompt,
            max_kb=st.session_state.get("max_file_size_kb", MAX_FILE_SIZE_KB),
        )
    st.session_state.cached_prompt = prompt
    st.session_state["prefill_user_message"] = prompt
    st.toast("Prompt built and pre-filled in chat!", icon="📋")


# ===========================================================================
# Section: Pending Patches
# ===========================================================================

def _section_pending_patches() -> None:
    st.markdown("#### ⏳ Pending Patches")

    patches: list[dict] = st.session_state.pending_patches

    if not patches:
        st.caption("No pending patches.")
        return

    col_all1, col_all2, col_count = st.columns([2, 2, 2])

    with col_all1:
        if st.button("✅ Accept All", use_container_width=True, key="accept_all_patches"):
            err = apply_all_patches()
            if err:
                st.error(err)
            else:
                st.rerun()

    with col_all2:
        if st.button("❌ Reject All", use_container_width=True, key="reject_all_patches"):
            st.session_state.pending_patches = []
            st.rerun()

    with col_count:
        st.caption(f"{len(patches)} pending")

    for i, patch in enumerate(patches):
        _render_patch_card(i, patch)


def _render_patch_card(index: int, patch: dict) -> None:
    patch_type = patch.get("type", "write")
    rel_path   = patch.get("path", "")
    content    = patch.get("content", "")
    workdir    = st.session_state.workdir

    full_path = rel_path if os.path.isabs(rel_path) else os.path.join(workdir, rel_path)

    if patch_type == "delete":
        icon, action_label = "🗑️", "DELETE"
    elif file_exists(full_path):
        icon, action_label = "✏️", "MODIFY"
    else:
        icon, action_label = "🆕", "CREATE"

    with st.container(border=True):
        st.markdown(f"{icon} **{action_label}** `{rel_path}`")

        col_apply, col_reject = st.columns(2)
        with col_apply:
            if st.button("✅ Apply", key=f"apply_patch_{index}", use_container_width=True):
                err = apply_single_patch(index)
                if err:
                    st.error(err)
                else:
                    st.rerun()
        with col_reject:
            if st.button("❌ Reject", key=f"reject_patch_{index}", use_container_width=True):
                st.session_state.pending_patches.pop(index)
                st.rerun()

        if patch_type == "write" and content:
            with st.expander("Preview", expanded=False):
                lang = os.path.splitext(rel_path)[1].lstrip(".")
                st.code(content, language=lang or "text")


# ===========================================================================
# Section: Version History
# ===========================================================================

def _section_version_history() -> None:
    st.markdown("#### 🕐 Version History")

    vh: VersionHistory = st.session_state.version_history

    if not vh.entries:
        st.caption("No history yet.")
        return

    total   = len(vh.entries)
    applied = vh.head + 1
    st.caption(f"{applied}/{total} commits applied · HEAD #{vh.head + 1}")

    # Panic button
    if vh.head >= 0:
        if st.button(
            "🚨 Reset ALL to original",
            use_container_width=True,
            key="panic_reset_btn",
            type="secondary",
        ):
            undo_to(-1)
            st.rerun()

    # Render: UNDO-before-first, then entries interleaved with UNDO/REDO buttons
    # Slot -1↔0: button to undo the very first commit (go back to clean state)
    _render_between_button(-1, vh)

    for i, entry in enumerate(vh.entries):
        is_applied = vh.is_applied(i)
        tick = "✅" if is_applied else "⬜"
        st.markdown(f"{tick} **#{i + 1}** `{entry.timestamp}` — {entry.description}")

        if i < total - 1:
            _render_between_button(i, vh)


def _render_between_button(above_index: int, vh: VersionHistory) -> None:
    """Render UNDO / REDO / disabled button between slot above_index and above_index+1.

    above_index == -1  means the slot before the first entry (head → -1).
    """
    below_index   = above_index + 1   # the entry just below this button
    below_applied = vh.is_applied(below_index)
    above_is_head = above_index == vh.head

    _, col_btn, _ = st.columns([2, 3, 2])

    with col_btn:
        if below_applied:
            # Clicking undoes everything from head down to below_index,
            # leaving head == above_index
            if st.button(
                "↩ UNDO",
                key=f"undo_btn_{above_index + 1}",
                use_container_width=True,
            ):
                undo_to(above_index)
                st.rerun()

        elif above_is_head:
            if st.button(
                "↪ REDO",
                key=f"redo_btn_{above_index + 1}",
                use_container_width=True,
            ):
                redo_to(below_index)
                st.rerun()

        else:
            st.button(
                "· · ·",
                key=f"gap_btn_{above_index + 1}",
                use_container_width=True,
                disabled=True,
            )