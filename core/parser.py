# core/parser.py

"""Parse LLM responses for file operation commands using JSON schemas and Pydantic."""

import json
import re
from typing import Literal, Optional, List, Any
from pydantic import BaseModel, Field, ValidationError

class ToolCall(BaseModel):
    tool: Literal["write_file", "delete_file"]
    path: str
    content: Optional[str] = ""

class FilePatch:
    def __init__(self, type: str, path: str, content: str = ""):
        # map pydantic tools to old UI types
        self.type = "write" if type == "write_file" else "delete"
        self.path = path
        self.content = content


def extract_json_arrays(text: str) -> list[str]:
    """Find JSON arrays in the text, handling markdown fences or bare arrays."""
    arrays = []
    
    # Try finding markdown fenced blocks first
    for match in re.finditer(r"```(?:json)?\n(.*?)\n```", text, re.DOTALL):
        arrays.append(match.group(1).strip())
        
    # If no fences, try finding raw JSON arrays [ ... ]
    if not arrays:
        for match in re.finditer(r"\[\s*\{.*?\}\s*\]", text, re.DOTALL):
            arrays.append(match.group(0).strip())
            
    return arrays


def parse_llm_response(response: str) -> list[FilePatch]:
    """Return ordered FilePatch objects extracted from JSON blocks in *response*."""
    patches: list[FilePatch] = []
    seen_paths: set[str] = set()
    
    json_strings = extract_json_arrays(response)
    
    # If extraction failed, try parsing the whole response as JSON just in case
    if not json_strings:
        json_strings = [response.strip()]

    for json_str in json_strings:
        try:
            data = json.loads(json_str)
            # handle both single object and array of objects
            if isinstance(data, dict):
                data = [data]
                
            if isinstance(data, list):
                for item in data:
                    try:
                        # Validate with Pydantic
                        call = ToolCall(**item)
                        if call.path not in seen_paths:
                            patches.append(
                                FilePatch(
                                    type=call.tool,
                                    path=call.path,
                                    content=call.content or ""
                                )
                            )
                            seen_paths.add(call.path)
                    except ValidationError:
                        # Ignore items that don't match our tool schema
                        continue
        except json.JSONDecodeError:
            continue

    return patches