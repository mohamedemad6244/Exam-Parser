# exam_cleaner.py
import json

def clean_and_validate_exam(raw_output: str) -> dict:
    # Step 1: Remove code blocks
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:].strip()
    elif raw_output.startswith("```"):
        raw_output = raw_output[3:].strip()
    if raw_output.endswith("```"):
        raw_output = raw_output[:-3].strip()

    # Step 2: Try parsing JSON
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        import ast
        data = ast.literal_eval(raw_output)

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
