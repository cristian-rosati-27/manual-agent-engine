"""MCP (Model Context Protocol) tab – manage external tool servers."""

import json
import os
import streamlit as st

MCP_CONFIG_FILE = "data/mcp_servers.json"

def load_mcp_servers() -> list[dict]:
    if not os.path.exists(MCP_CONFIG_FILE):
        return []
    try:
        with open(MCP_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_mcp_servers(servers: list[dict]) -> None:
    os.makedirs(os.path.dirname(MCP_CONFIG_FILE), exist_ok=True)
    with open(MCP_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(servers, f, indent=2)

def render_mcp_tab() -> None:
    st.markdown("#### 🔌 MCP Servers")
    st.caption("Model Context Protocol servers provide additional tools and context.")

    if "mcp_servers" not in st.session_state:
        st.session_state.mcp_servers = load_mcp_servers()

    # Add new server
    with st.expander("➕ Add MCP Server", expanded=False):
        new_name = st.text_input("Server Name", placeholder="e.g. Postgres DB")
        new_command = st.text_input("Command", placeholder="e.g. npx")
        new_args = st.text_input("Arguments (space separated)", placeholder="-y @modelcontextprotocol/server-postgres postgres://...")
        
        if st.button("Save Server", use_container_width=True):
            if new_name and new_command:
                st.session_state.mcp_servers.append({
                    "name": new_name,
                    "command": new_command,
                    "args": new_args.split() if new_args else []
                })
                save_mcp_servers(st.session_state.mcp_servers)
                st.rerun()
            else:
                st.error("Name and Command are required.")

    st.divider()

    # List existing servers
    st.markdown("**Configured Servers**")
    if not st.session_state.mcp_servers:
        st.caption("No MCP servers configured.")
    else:
        for i, server in enumerate(st.session_state.mcp_servers):
            with st.container(border=True):
                st.markdown(f"**{server['name']}**")
                st.code(f"{server['command']} {' '.join(server['args'])}", language="bash")
                
                col_status, col_del = st.columns([3, 1])
                with col_status:
                    # In a real implementation, this would show connection status
                    st.caption("🔴 Disconnected (Manual connection not yet implemented)")
                with col_del:
                    if st.button("🗑️", key=f"del_mcp_{i}", use_container_width=True):
                        st.session_state.mcp_servers.pop(i)
                        save_mcp_servers(st.session_state.mcp_servers)
                        st.rerun()
