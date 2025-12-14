import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are an expert academic exam analyzer. "
    "Extract structured exam information from raw text. "
    "Identify subject name, instructor name, and all questions. "
    "Classify questions into MCQ or Essay. "
    "Extract options and correct answers if present. "
    "Generate four different exam models (A, B, C, D) by reordering questions. "
    "Output ONLY valid JSON in the following structure:\n"
    "{"
    "  subject: string,"
    "  instructor: string,"
    "  models: {"
    "    A: [ { question_number, type, question, options?, answer? } ],"
    "    B: [...],"
    "    C: [...],"
    "    D: [...]"
    "  }"
    "}"
)


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")
    return genai.Client(api_key=api_key)


def parse_exam(text: str, model_id: str = "gemini-2.5-flash") -> str:
    client = get_client()

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.2,
        max_output_tokens=4096,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )

    response = client.models.generate_content(
        model=model_id,
        contents=text,
        config=config
    )

    return response.text

def parse_exam_test(text: str = "Test exam content") -> str:
    """
    Simulate parse_exam without calling Gemini API.
    Returns a dummy JSON string matching the real output format.
    """
    dummy_response = {
        "subject": "Dummy Subject",
        "instructor": "Dummy Instructor",
        "models": {
            "A": [{"question_number": 1, "type": "MCQ", "question": "Sample question?", "options": ["A","B","C"], "answer": "A"}],
            "B": [{"question_number": 1, "type": "MCQ", "question": "Sample question?", "options": ["A","B","C"], "answer": "A"}],
            "C": [{"question_number": 1, "type": "MCQ", "question": "Sample question?", "options": ["A","B","C"], "answer": "A"}],
            "D": [{"question_number": 1, "type": "MCQ", "question": "Sample question?", "options": ["A","B","C"], "answer": "A"}]
        }
    }
    return json.dumps(dummy_response)

def check_gemini_api(model_id: str = "gemini-2.5-flash") -> dict:
    """
    Test if Gemini API client is working by sending a minimal prompt.
    Returns status dict: {success: bool, message: str}
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"success": False, "message": "GEMINI_API_KEY not found in .env"}

        client = genai.Client(api_key=api_key)

        # Minimal test content
        test_content = "Hello, please respond with a short test message."

        config = types.GenerateContentConfig(
            system_instruction="You are a test assistant.",
            temperature=0.0,
            max_output_tokens=32
        )

        response = client.models.generate_content(
            model=model_id,
            contents=test_content,
            config=config
        )

        if response.text.strip():
            return {"success": True, "message": "Gemini API client works!"}
        else:
            return {"success": False, "message": "Gemini responded empty text"}

    except Exception as e:
        return {"success": False, "message": str(e)}

