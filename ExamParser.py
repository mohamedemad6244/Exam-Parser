import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

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

