"""Prompts & Skills tab – manage instructions and injected context docs."""

import streamlit as st

from config.defaults import DEFAULT_SYSTEM_PROMPT

def render_prompts_tab() -> None:
    st.markdown("#### 🧠 Prompts & Skills")
    st.caption("Manage system instructions and inject markdown documents as skills.")
    
    st.checkbox("🪨 Caveman Mode (Be extremely concise to save tokens)", key="caveman_mode")
    
    st.divider()
    
    st.markdown("**Skills (Context Documents)**")
    
    if "skills" not in st.session_state:
        st.session_state.skills = []
        
    uploaded_skill = st.file_uploader("➕ Add Skill (Markdown Document)", type=["md", "txt", "json"], key="skill_uploader")
    if uploaded_skill:
        content = uploaded_skill.read().decode("utf-8")
        # Add only if not already present by name
        if not any(s["name"] == uploaded_skill.name for s in st.session_state.skills):
            st.session_state.skills.append({"name": uploaded_skill.name, "content": content})
            st.rerun()
            
    if st.session_state.skills:
        for i, skill in enumerate(st.session_state.skills):
            with st.expander(f"📄 {skill['name']}"):
                col_view, col_del = st.columns([4, 1])
                with col_view:
                    st.text_area("Content", value=skill["content"], height=100, disabled=True, label_visibility="collapsed", key=f"skill_view_{i}")
                with col_del:
                    if st.button("🗑️ Remove", key=f"del_skill_{i}"):
                        st.session_state.skills.pop(i)
                        st.rerun()
    else:
        st.caption("No skills added yet.")
        
    st.divider()

    st.markdown("**Prompts**")
    prompt_tabs = st.tabs(["System", "Tool", "Injection", "Summarization"])
    with prompt_tabs[0]:
        st.text_area("System Prompt", value=st.session_state.get("system_prompt", DEFAULT_SYSTEM_PROMPT), height=200, key="system_prompt_textarea")
    with prompt_tabs[1]:
        st.text_area("Tool Prompt", value="", height=200, key="tool_prompt_textarea")
    with prompt_tabs[2]:
        st.text_area("Injection Prompt", value="", height=200, key="injection_prompt_textarea")
    with prompt_tabs[3]:
        st.text_area("Summarization Prompt", value="", height=200, key="summarization_prompt_textarea")
