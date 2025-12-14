# exam_cleaner.py
import json
import re


def _strip_code_fence(s: str) -> str:
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()


def _escape_newlines_in_strings(s: str) -> str:
    # Walk the string and replace literal newlines inside double-quoted
    # strings with escaped \n so JSON can parse them.
    out_chars = []
    in_string = False
    escape = False
    for ch in s:
        if in_string:
            if escape:
                out_chars.append(ch)
                escape = False
                continue
            if ch == "\\":
                out_chars.append(ch)
                escape = True
                continue
            if ch == '"':
                in_string = False
                out_chars.append(ch)
                continue
            if ch == "\n" or ch == "\r":
                out_chars.append("\\n")
                continue
            out_chars.append(ch)
        else:
            out_chars.append(ch)
            if ch == '"':
                in_string = True
    return ''.join(out_chars)


def _remove_trailing_commas(s: str) -> str:
    # Remove trailing commas before closing braces/brackets which break strict JSON
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s


def clean_and_validate_exam(raw_output: str) -> dict:
    # Step 1: Remove code fences
    raw_output = _strip_code_fence(raw_output)

    # Step 2: Try parsing JSON, with progressive repairs
    try:
        data = json.loads(raw_output)
    except Exception:
        # Try escaping raw newlines inside quoted strings
        repaired = _escape_newlines_in_strings(raw_output)
        repaired = _remove_trailing_commas(repaired)
        try:
            data = json.loads(repaired)
        except Exception:
            # Last resort: try ast.literal_eval on the repaired text
            import ast
            data = ast.literal_eval(repaired)

    # Step 3: Fill missing keys with defaults
    if "models" not in data:
        data["models"] = {"A": [], "B": [], "C": [], "D": []}
    else:
        for key in ["A", "B", "C", "D"]:
            if key not in data["models"]:
                data["models"][key] = []

    # Step 4: Ensure all fields exist in questions
    for model in data["models"].values():
        for q in model:
            q.setdefault("options", None)
            q.setdefault("answer", None)
    
    return data
