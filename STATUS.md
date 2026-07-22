# Agentic Coding Studio - Status Document

## Current Status
- Renamed application to "Agentic Coding Studio".
- Updated `ui/settings_tab.py` with complete Settings:
  - Model settings (Provider, Model, API Key, Advanced options)
  - Mode Selection (Manual Mode, Automatic Mode)
  - API Endpoint is placed below Provider and auto-fills based on the selected Provider.
- Extracted Prompts & Skills to a dedicated tab `🧠 Prompts` in the sidebar.
  - Users can now upload and inject external Markdown files as Skills.
- Added `GitPython` and `pydantic` to `requirements.txt`.
- Re-implemented `ui/workdir_tab.py`:
  - Context Injection widget with token size preview.
  - Tree Preview recursively displaying files/folders without ugly markdown dashes, cleanly indented via column weights.
  - Work Directory section now stores and presents a dropdown of up to 10 Recently Used Paths.
- Overhauled `ui/chat_panel.py`:
  - Copy button automatically aggregates System, Tool, Injection, Caveman prompts, and injected Skills.
  - Added token summary (estimation) under each message and at the bottom of the conversation.
- Modified `core/parser.py` and `config/defaults.py` for robust JSON parsing.
- Added `ui/mcp_tab.py` to manage MCP servers.

## Missing Features / To-Do
File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 129, in exec_func_with_error_handling
      result = func()
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 807, in code_to_exec
      exec(code, module.__dict__)  # noqa: S102
    File "/home/crist/REPOS/manual-agent-engine/app.py", line 104, in <module>
      render_workdir_tab()
    File "/home/crist/REPOS/manual-agent-engine/ui/workdir_tab.py", line 24, in render_workdir_tab
      _section_tree_preview()
    File "/home/crist/REPOS/manual-agent-engine/ui/workdir_tab.py", line 191, in _section_tree_preview
      render_tree(st.session_state.workdir)
    File "/home/crist/REPOS/manual-agent-engine/ui/workdir_tab.py", line 180, in render_tree
      changed = st.checkbox("", value=node_state, key=f"chk_{entry.path}", label_visibility="collapsed")
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 568, in wrapped_func
      result = non_optional_func(*args, **kwargs)
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/elements/widgets/checkbox.py", line 218, in checkbox
      return self._checkbox(
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/elements/widgets/checkbox.py", line 431, in _checkbox
      maybe_raise_label_warnings(label, label_visibility)
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/elements/lib/policies.py", line 150, in maybe_raise_label_warnings
      _LOGGER.warning(
  2026-07-22 21:25:36.828 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility
  if needed.
  Stack (most recent call last):
    File "/home/crist/anaconda3/lib/python3.13/threading.py", line 1014, in _bootstrap
      self._bootstrap_inner()
    File "/home/crist/anaconda3/lib/python3.13/threading.py", line 1043, in _bootstrap_inner
      self.run()
    File "/home/crist/anaconda3/lib/python3.13/threading.py", line 994, in run
      self._target(*self._args, **self._kwargs)
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 418, in _run_script_thread
      self._run_script(request.rerun_data)
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 832, in _run_script
      ) = exec_func_with_error_handling(code_to_exec, ctx)
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 129, in exec_func_with_error_handling
      result = func()
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 807, in code_to_exec
      exec(code, module.__dict__)  # noqa: S102
    File "/home/crist/REPOS/manual-agent-engine/app.py", line 104, in <module>
      render_workdir_tab()
    File "/home/crist/REPOS/manual-agent-engine/ui/workdir_tab.py", line 24, in render_workdir_tab
      _section_tree_preview()
    File "/home/crist/REPOS/manual-agent-engine/ui/workdir_tab.py", line 191, in _section_tree_preview
      render_tree(st.session_state.workdir)
    File "/home/crist/REPOS/manual-agent-engine/ui/workdir_tab.py", line 180, in render_tree
      changed = st.checkbox("", value=node_state, key=f"chk_{entry.path}", label_visibility="collapsed")
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 568, in wrapped_func
      result = non_optional_func(*args, **kwargs)
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/elements/widgets/checkbox.py", line 218, in checkbox
      return self._checkbox(
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/elements/widgets/checkbox.py", line 431, in _checkbox
      maybe_raise_label_warnings(label, label_visibility)
    File "/home/crist/anaconda3/lib/python3.13/site-packages/streamlit/elements/lib/policies.py", line 150, in maybe_raise_label_warnings
      _LOGGER.warning(
  2026-07-22 21:25:36.830 Please replace `st.components.v1.html` with `st.iframe`.
  
  `st.components.v1.html` will be removed after 2026-06-01.
  2026-07-22 21:25:36.860 Please replace `st.components.v1.html` with `st.iframe`.

  `st.components.v1.html` will be removed after 2026-06-01.
  2026-07-22 21:25:36.865 Please replace `st.components.v1.html` with `st.iframe`.

  ti mando un po di log poi i seguenti punti

  andrebbero indentati un po di piu i file nelle cartelle, inoltre ancora non si disattivano i file nelle cartelle se disattivo la cartella
  poi farebbero comodo dei pulsanti attiva e disattiva tutto

  in modalita automatic mi permette ancora di scrivere nel turno dell'ai, invece dovrebbe chiamare ollama o chi per lui e in caso di errori mostrarli

## Next Steps
- Continue verifying edge cases with LLM outputs (JSON malformations).
- Implement actual automatic tool-calling loop for Automatic Mode (currently it just sets the endpoint).

