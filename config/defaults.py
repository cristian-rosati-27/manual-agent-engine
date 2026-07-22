"""Application-wide defaults and constants."""

DEFAULT_EXTENSIONS: list[str] = [
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".html", ".css", ".scss",
    ".md", ".json", ".yaml", ".yml", ".toml", ".txt",
    ".sh", ".env",
]

ALL_KNOWN_EXTENSIONS: list[str] = [
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".html", ".css", ".scss", ".sass", ".less",
    ".md", ".mdx", ".rst", ".txt",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".sh", ".bash", ".zsh", ".fish",
    ".env", ".env.example",
    ".rs", ".go", ".java", ".c", ".cpp", ".h", ".hpp",
    ".rb", ".php", ".swift", ".kt", ".scala",
    ".sql", ".graphql", ".proto",
    ".xml", ".svg", ".csv",
    ".dockerfile", ".tf", ".hcl",
    ".vue", ".svelte",
    ".r", ".jl",
]

SKIP_DIRS: set[str] = {
    ".git", ".hg", ".svn",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".yarn", ".pnpm",
    "venv", ".venv", "env", ".env",
    "dist", "build", ".next", ".nuxt", "out",
    ".idea", ".vscode",
    "coverage", ".coverage",
}

DEFAULT_SYSTEM_PROMPT: str = """\
You are an expert software engineer. Analyze the codebase provided and respond to the user's request.

When you need to create, modify, or delete files, use robust JSON tool calls formatted exactly like this inside a markdown JSON block. You can return an array of these operations.

```json
[
  {
    "tool": "write_file",
    "path": "path/to/file.ext",
    "content": "full file content here"
  },
  {
    "tool": "delete_file",
    "path": "path/to/file_to_delete.ext"
  }
]
```

Rules:
- Paths are relative to the project root shown in the tree.
- Always write the COMPLETE file content, never truncate or use placeholders.
- Include ALL necessary file operations in a single JSON array block.
- You can add normal text explanation outside the JSON block.\
"""

CHATS_DIR: str = "data/chats"
MAX_FILE_SIZE_KB: int = 500
