# json_utils.py

import json
from typing import Any

def normalize_json(json_text: str) -> str:
    """
    A simplified version of the Delphi NormalizeJson function.
    In Python, we typically just load and dump to handle most formatting
    and commentary issues (if the input is valid JSON with comments).
    A robust solution would use a JSON parser that supports comments (like 'json5' or 'hjson').
    For this example, we assume standard JSON, or use a basic replacement for comments.
    """
    # Simple attempt to remove C-style comments before parsing
    # This is a dangerous simplification, but mirrors the need from the original code
    lines = json_text.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith('//'):
            continue
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)
