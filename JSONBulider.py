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
    # Walk the text and replace literal newlines inside double-quoted
    # JSON strings with escaped \n so `json.loads` can parse them.
    out = []
    in_string = False
    escape = False
    i = 0
    while i < len(s):
        ch = s[i]
        if in_string:
            if escape:
                out.append(ch)
                escape = False
            elif ch == "\\":
                out.append(ch)
                escape = True
            elif ch == '"':
                in_string = False
                out.append(ch)
            elif ch == '\r':
                # convert CR or CRLF to a single \n
                if i + 1 < len(s) and s[i + 1] == '\n':
                    i += 1
                out.append('\\n')
            elif ch == '\n':
                out.append('\\n')
            else:
                out.append(ch)
        else:
            out.append(ch)
            if ch == '"':
                in_string = True
        i += 1
    return ''.join(out)


def _close_unterminated_strings(s: str) -> str:
    # If the text ends while still inside a double-quoted string,
    # append a closing quote before the next structural character
    # or at the end. Also, if number of unescaped quotes is odd,
    # append a closing quote at the end.
    in_string = False
    escape = False
    for ch in s:
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True

    if not in_string:
        return s

    # If we ended inside a string, try to close it before a nearby
    # structural character (comma, brace, bracket). If not found,
    # just append a closing quote at the end.
    for i in range(len(s) - 1, -1, -1):
        if s[i] in ',}]\n':
            return s[:i] + '"' + s[i:]
    return s + '"'


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
        # 1) Escape raw newlines that appear inside JSON strings
        repaired = _escape_newlines_in_strings(raw_output)
        # 2) Remove trailing commas like {"a": 1,}
        repaired = _remove_trailing_commas(repaired)
        # 3) Close any unterminated double-quoted strings
        repaired = _close_unterminated_strings(repaired)
        # Try parsing the repaired text
        try:
            data = json.loads(repaired)
        except Exception as e:
            # As a last resort, raise a clear error with the original
            # decode error message and the attempted repaired snippet.
            raise ValueError(f"Failed to parse JSON after repairs: {e}\n---Repaired snippet---\n{repaired[:2000]}") from e

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
