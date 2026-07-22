# ui/workdir_tab.py

"""WorkDir tab – the main left-panel section."""

import os

import streamlit as st
import streamlit.components.v1 as components

from config.defaults import MAX_FILE_SIZE_KB, SKIP_DIRS
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
    _section_tree_preview()
    st.divider()
    _section_context_preview()
    st.divider()
    _section_pending_patches()
    st.divider()
    _section_version_history()


# ===========================================================================
# Section: Work Directory
# ===========================================================================

import json

def _load_recent_paths() -> list[str]:
    path = "data/recent_paths.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def _save_recent_paths(paths: list[str]) -> None:
    os.makedirs("data", exist_ok=True)
    with open("data/recent_paths.json", "w", encoding="utf-8") as f:
        json.dump(paths, f)

def _section_workdir() -> None:
    st.markdown("#### 📁 Work Directory")
    
    if "recent_paths" not in st.session_state:
        st.session_state.recent_paths = _load_recent_paths()

    col_dir, col_btn = st.columns([3, 1])
    with col_dir:
        new_dir = st.text_input(
            "dir",
            value=st.session_state.workdir,
            label_visibility="collapsed",
            placeholder="Absolute path to project root…",
            key="workdir_input",
        )
    with col_btn:
        if st.button("Choose", use_container_width=True, key="choose_dir_btn"):
            st.toast("File picker not natively supported. Please paste the path.", icon="ℹ️")

    col_set = st.columns(1)[0]
    if col_set.button("✅ Set Workspace", use_container_width=True, key="set_workdir"):
        _set_workdir(new_dir.strip())
        
    if st.session_state.recent_paths:
        selected_recent = st.selectbox("Recent Paths", ["Select a recent path..."] + st.session_state.recent_paths)
        if selected_recent and selected_recent != "Select a recent path..." and selected_recent != st.session_state.workdir:
            st.session_state.workdir_input = selected_recent
            _set_workdir(selected_recent)

    if st.session_state.workdir and os.path.isdir(st.session_state.workdir):
        st.caption(f"✅ `{st.session_state.workdir}`")
    elif st.session_state.workdir:
        st.caption(f"⚠️ Path not found: `{st.session_state.workdir}`")
    else:
        st.caption("No directory set.")


def _set_workdir(path: str) -> None:
    if not path:
        st.toast("Enter a path first.", icon="⚠️")
        return
    if not os.path.isdir(path):
        st.toast(f"Directory not found: {path}", icon="⚠️")
        return
    st.session_state.workdir = path
    
    if path not in st.session_state.recent_paths:
        st.session_state.recent_paths.insert(0, path)
        if len(st.session_state.recent_paths) > 10:
            st.session_state.recent_paths.pop()
        _save_recent_paths(st.session_state.recent_paths)
        
    # Reset tree selection on new dir
    st.session_state.tree_selection = {}
    st.session_state.pop("cached_prompt", None)
    st.rerun()


# ===========================================================================
# Section: Tree Preview
# ===========================================================================

def _section_tree_preview() -> None:
    st.markdown("#### 🌳 Tree Preview")
    
    if not st.session_state.workdir or not os.path.isdir(st.session_state.workdir):
        st.caption("Set a valid working directory to view the tree.")
        return
        
    if "tree_selection" not in st.session_state:
        st.session_state.tree_selection = {}
        
    if "expanded_nodes" not in st.session_state:
        st.session_state.expanded_nodes = {st.session_state.workdir}
        
    def get_all_children(root_path):
        children = []
        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
                for f in filenames:
                    if not f.startswith("."):
                        children.append(os.path.join(dirpath, f))
                for d in dirnames:
                    children.append(os.path.join(dirpath, d))
        except:
            pass
        return children

    def toggle_node(node_path, is_dir):
        current_state = st.session_state.tree_selection.get(node_path, True)
        new_state = not current_state
        st.session_state.tree_selection[node_path] = new_state
        if is_dir:
            for child in get_all_children(node_path):
                st.session_state.tree_selection[child] = new_state

    def render_tree(current_path, level=0):
        try:
            entries = sorted(list(os.scandir(current_path)), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return

        for entry in entries:
            if entry.name.startswith(".") or entry.name in SKIP_DIRS:
                continue
                
            is_dir = entry.is_dir()
            icon = "📁" if is_dir else "📄"
            
            node_state = st.session_state.tree_selection.get(entry.path, True)
            
            indent_weight = max(level * 0.7, 0.01)
            cols = st.columns([indent_weight, 1, 1, 10])
            
            with cols[1]:
                if is_dir:
                    is_expanded = entry.path in st.session_state.expanded_nodes
                    btn_label = "🔽" if is_expanded else "▶️"
                    if st.button(btn_label, key=f"exp_{entry.path}", help="Expand/Collapse"):
                        if is_expanded:
                            st.session_state.expanded_nodes.discard(entry.path)
                        else:
                            st.session_state.expanded_nodes.add(entry.path)
                        st.rerun()
            with cols[2]:
                changed = st.checkbox("", value=node_state, key=f"chk_{entry.path}", label_visibility="collapsed")
                if changed != node_state:
                    toggle_node(entry.path, is_dir)
                    st.rerun()
            with cols[3]:
                st.markdown(f"{icon} {entry.name}")
                
            if is_dir and entry.path in st.session_state.expanded_nodes:
                render_tree(entry.path, level + 1)
                
    with st.container(height=400):
        render_tree(st.session_state.workdir)


# ===========================================================================
# Section: Context Preview (Injection)
# ===========================================================================

def _section_context_preview() -> None:
    st.markdown("#### 💉 Context Injection")

    if st.button("🚀 Inject Context", use_container_width=True, type="primary"):
        _build_and_inject_prompt()

    prompt = st.session_state.get("cached_prompt", "")

    if not prompt:
        st.caption("Context not injected yet.")
        return

    # Assuming a max context size of 1,000,000 tokens for demonstration (e.g. Gemini 1.5 Pro)
    max_tokens = 1000000
    token_estimate = len(prompt) // 4
    percentage = min(token_estimate / max_tokens, 1.0)
    
    st.markdown(f"**Context Size:** `{token_estimate:,} tokens` ({percentage*100:.1f}%)")
    st.progress(percentage)

    # Copy button via components.html so it's never sanitised by Streamlit
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
# Prompt builder wrapper
# ===========================================================================

def _build_and_inject_prompt() -> None:
    if not st.session_state.workdir or not os.path.isdir(st.session_state.workdir):
        st.error("Please set a valid work directory first.")
        return
        
    with st.spinner("Injecting context…"):
        prompt = build_prompt(
            root=st.session_state.workdir,
            selected_paths=st.session_state.get("tree_selection", {}),
            system_prompt=st.session_state.get("system_prompt", ""),
            max_kb=st.session_state.get("max_file_size_kb", MAX_FILE_SIZE_KB),
        )
    st.session_state.cached_prompt = prompt
    st.session_state["prefill_user_message"] = prompt
    st.toast("Context injected and pre-filled in chat!", icon="📋")


# ===========================================================================
# Section: Pending Patches
# ===========================================================================

def _section_pending_patches() -> None:
    st.markdown("#### ⏳ Tool Changes")

    patches: list[dict] = st.session_state.pending_patches

    if not patches:
        st.caption("No pending changes.")
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

    _render_between_button(-1, vh)

    for i, entry in enumerate(vh.entries):
        is_applied = vh.is_applied(i)
        tick = "✅" if is_applied else "⬜"
        st.markdown(f"{tick} **#{i + 1}** `{entry.timestamp}` — {entry.description}")

        if i < total - 1:
            _render_between_button(i, vh)


def _render_between_button(above_index: int, vh: VersionHistory) -> None:
    below_index   = above_index + 1
    below_applied = vh.is_applied(below_index)
    above_is_head = above_index == vh.head

    _, col_btn, _ = st.columns([2, 3, 2])

    with col_btn:
        if below_applied:
            if st.button("↩ Restore", key=f"undo_btn_{above_index + 1}", use_container_width=True):
                undo_to(above_index)
                st.rerun()
        elif above_is_head:
            if st.button("↪ REDO", key=f"redo_btn_{above_index + 1}", use_container_width=True):
                redo_to(below_index)
                st.rerun()
        else:
            st.button("· · ·", key=f"gap_btn_{above_index + 1}", use_container_width=True, disabled=True)
