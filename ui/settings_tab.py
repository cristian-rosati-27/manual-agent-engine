"""Settings tab – global configuration."""

import streamlit as st

from config.defaults import MAX_FILE_SIZE_KB

def render_settings_tab() -> None:
    st.markdown("#### ⚙️ Settings")

    # -----------------------------------------------------------------------
    # Modes
    # -----------------------------------------------------------------------
    st.markdown("**Mode**")
    mode = st.radio(
        "Application Mode",
        ["Manual Mode", "Automatic Mode"],
        label_visibility="collapsed",
        key="app_mode",
    )
        
    st.divider()

    # -----------------------------------------------------------------------
    # Model Settings
    # -----------------------------------------------------------------------
    st.markdown("**Model Settings**")
    
    provider = st.selectbox(
        "Provider",
        ["OpenAI", "Anthropic", "OpenRouter", "Ollama", "LM Studio", "Custom OpenAI Compatible"],
        key="model_provider"
    )
    
    model = st.text_input("Model", value="gpt-4o", key="model_name")
    
    # Auto-fill endpoint logic
    default_endpoint = ""
    if provider == "Ollama":
        default_endpoint = "http://localhost:11434/api/generate"
    elif provider == "LM Studio":
        default_endpoint = "http://localhost:1234/v1"
    elif provider == "OpenRouter":
        default_endpoint = "https://openrouter.ai/api/v1"
    elif provider == "OpenAI":
        default_endpoint = "https://api.openai.com/v1"
    elif provider == "Anthropic":
        default_endpoint = "https://api.anthropic.com/v1"
        
    st.text_input(
        "API Endpoint", 
        value=default_endpoint if st.session_state.get("app_mode") == "Automatic Mode" else "",
        placeholder=default_endpoint, 
        key="api_endpoint"
    )
    
    api_key = st.text_input("API Key", type="password", key="api_key")
    
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1, key="temperature")
        top_p = st.slider("Top P", 0.0, 1.0, 1.0, 0.05, key="top_p")
        streaming = st.checkbox("Streaming", value=True, key="streaming")
    with col2:
        max_tokens = st.number_input("Max Tokens", min_value=1, max_value=128000, value=4096, key="max_tokens")
        seed = st.number_input("Seed (optional)", value=0, key="seed")
        reasoning = st.selectbox("Reasoning Effort", ["none", "low", "medium", "high"], key="reasoning")

    st.divider()

    # -----------------------------------------------------------------------
    # Tool Settings
    # -----------------------------------------------------------------------
    st.markdown("**Tool Settings**")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.checkbox("Read File", value=True, key="tool_read")
        st.checkbox("Write File", value=True, key="tool_write")
        st.checkbox("Apply Patch", value=True, key="tool_patch")
        st.checkbox("Search", value=True, key="tool_search")
        st.checkbox("Run Command", value=True, key="tool_command")
    with col_t2:
        st.checkbox("Git Commit", value=True, key="tool_git")
        st.checkbox("Rollback", value=True, key="tool_rollback")
        st.checkbox("Python", value=False, key="tool_python")
        st.checkbox("Bash", value=False, key="tool_bash")

    st.divider()

    # -----------------------------------------------------------------------
    # Context Settings
    # -----------------------------------------------------------------------
    st.markdown("**Context Settings**")

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
