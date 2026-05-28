# app.py

"""LLM Workbench – main entry point.

Run with:
    streamlit run app.py
"""

import streamlit as st

from state.session import init_session
from ui.chat_panel import render_chat_panel
from ui.chats_tab import render_chats_tab
from ui.settings_tab import render_settings_tab
from ui.workdir_tab import render_workdir_tab

# ---------------------------------------------------------------------------
# Page config  (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="LLM Workbench",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Sidebar width – fixed, no horizontal scroll */
    [data-testid="stSidebar"] {
        min-width: 360px !important;
        max-width: 360px !important;
        overflow-x: hidden !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
        padding-left: 0.6rem;
        padding-right: 0.6rem;
        overflow-x: hidden !important;
        width: 100% !important;
        box-sizing: border-box;
    }
    /* Kill any horizontal scroll inside sidebar */
    [data-testid="stSidebar"] * {
        max-width: 100% !important;
        box-sizing: border-box;
    }

    /* Tighter main area */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 100%;
    }

    /* Prompt preview box */
    .prompt-box {
        height: 260px;
        overflow-y: auto;
        background: #0e1117;
        border: 1px solid #31333f;
        border-radius: 6px;
        padding: 12px 14px;
        font-family: "JetBrains Mono", "Fira Code", monospace;
        font-size: 11.5px;
        line-height: 1.5;
        white-space: pre-wrap;
        word-break: break-all;
        color: #e0e0e0;
    }

    hr { border-color: rgba(128,128,128,0.15); }

    /* Make st.error wrap instead of overflow */
    [data-testid="stAlert"] {
        word-break: break-word !important;
        white-space: normal !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session initialisation
# ---------------------------------------------------------------------------
init_session()

# ---------------------------------------------------------------------------
# Sidebar: WorkDir / Settings / Chats tabs
# ---------------------------------------------------------------------------
with st.sidebar:
    tab_wd, tab_settings, tab_chats = st.tabs(
        ["📁 WorkDir", "⚙️ Settings", "💬 Chats"]
    )
    with tab_wd:
        render_workdir_tab()
    with tab_settings:
        render_settings_tab()
    with tab_chats:
        render_chats_tab()

# ---------------------------------------------------------------------------
# Main area: chat
# ---------------------------------------------------------------------------
render_chat_panel()