# 🛠️ LLM Workbench

A Streamlit app for **manually-driven, codebase-aware conversations** with any LLM.

You write both sides of the conversation (user + LLM).  
The app builds the codebase context for you, parses file operations from LLM responses,  
and gives you a full undo/redo history of every file change.

---

## Features

| Feature | Details |
|---|---|
| **Codebase context builder** | Generates a directory tree + full file contents, ready to paste into any LLM chat |
| **Extension filter** | Pick which file types to include; add custom extensions |
| **File patch parser** | Extracts `<<<FILE:…>>>` and `<<<DELETE:…>>>` commands from LLM responses |
| **Pending patches** | Review, accept or reject individual file operations before they touch disk |
| **Version history** | Full undo / redo with UNDO/REDO buttons between every commit |
| **Chat persistence** | Save and reload conversations as JSON; delete old ones |
| **System prompt** | Configurable global instruction injected at the top of every prompt |

---

## Quick start

```bash
pip install streamlit
streamlit run app.py
```

---

## LLM file-operation syntax

Instruct your LLM (the default system prompt already does this) to use:

**Create or modify a file**
```
<<<FILE:src/utils.py>>>
def hello():
    return "world"
<<<END_FILE>>>
```

**Delete a file**
```
<<<DELETE:src/old_module.py>>>
```

Paths are relative to the work directory.

---

## Project structure

```
llm-workbench/
├── app.py                   ← Streamlit entry point
├── requirements.txt
├── config/
│   └── defaults.py          ← Constants and default values
├── core/
│   ├── parser.py            ← Parse LLM responses for file commands
│   ├── file_manager.py      ← Low-level read/write/delete helpers
│   ├── prompt_builder.py    ← Build directory tree + prompt from codebase
│   ├── patch_applier.py     ← Apply/revert patches; advance version history
│   └── version_history.py  ← VersionHistory data model with undo/redo
├── state/
│   └── session.py           ← st.session_state init and chat persistence
├── ui/
│   ├── workdir_tab.py       ← Left panel: directory, extensions, preview, patches, history
│   ├── settings_tab.py      ← Left panel: system prompt and options
│   ├── chats_tab.py         ← Left panel: saved chat browser
│   └── chat_panel.py        ← Right panel: conversation + turn entry
└── data/
    └── chats/               ← Persisted chat JSON files (auto-created)
```

---

## Extending the app

* **New file command type** – add a regex in `core/parser.py` and handle the new type in `core/patch_applier.py`.
* **Real LLM integration** – call an API in `ui/chat_panel.py` instead of the manual text area; the rest of the pipeline stays unchanged.
* **Diff view** – swap `st.code(content)` in the patch card with a unified diff computed by `difflib`.
