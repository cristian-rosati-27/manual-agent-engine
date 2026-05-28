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

When you need to create, modify, or delete files, use these exact markers in your response:

**Create or modify a file:**
<<<FILE:path/to/file.ext>>>
full file content here
<<<END_FILE>>>

**Delete a file:**
<<<DELETE:path/to/file.ext>>>

Rules:
- Paths are relative to the project root shown in the tree.
- Always write the COMPLETE file content, never truncate.
- Include ALL necessary file operations in a single response.
- After all file operations, explain briefly what you changed and why.\
"""

CHATS_DIR: str = "data/chats"
MAX_FILE_SIZE_KB: int = 500
