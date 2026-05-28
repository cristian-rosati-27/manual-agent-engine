"""Settings tab – global configuration."""

import streamlit as st

from config.defaults import DEFAULT_SYSTEM_PROMPT, MAX_FILE_SIZE_KB


def render_settings_tab() -> None:
    st.markdown("#### ⚙️ Settings")

    # -----------------------------------------------------------------------
    # System prompt
    # -----------------------------------------------------------------------
    st.markdown("**System Prompt**")
    st.caption(
        "Prepended to the codebase context in the prompt.  "
        "Instructs the LLM on the file-operation syntax and general behaviour."
    )

    new_prompt: str = st.text_area(
        "system_prompt_area",
        value=st.session_state.get("system_prompt", DEFAULT_SYSTEM_PROMPT),
        height=380,
        label_visibility="collapsed",
        key="system_prompt_textarea",
    )

    col_save, col_reset = st.columns(2)
    with col_save:
        if st.button("💾 Save", use_container_width=True, key="save_system_prompt"):
            st.session_state.system_prompt = new_prompt
            st.session_state.pop("cached_prompt", None)
            st.success("System prompt saved.")
    with col_reset:
        if st.button("↩️ Reset", use_container_width=True, key="reset_system_prompt"):
            st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
            st.session_state.pop("cached_prompt", None)
            st.rerun()

    st.divider()

    # -----------------------------------------------------------------------
    # Prompt settings
    # -----------------------------------------------------------------------
    st.markdown("**Prompt Settings**")

    max_kb: int = st.number_input(
        "Max file size included in prompt (KB)",
        min_value=10,
        max_value=10_000,
        value=int(st.session_state.get("max_file_size_kb", MAX_FILE_SIZE_KB)),
        step=50,
        help="Files larger than this threshold are listed but their content is omitted.",
        key="max_kb_input",
    )
    if max_kb != st.session_state.get("max_file_size_kb", MAX_FILE_SIZE_KB):
        st.session_state.max_file_size_kb = max_kb
        st.session_state.pop("cached_prompt", None)
