import json

from PyPDF2 import PdfReader

from app.services.llm_service import generate_response


def extract_text_from_pdf(file_path: str) -> str:

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def analyze_resume(resume_text: str):

    prompt = f"""
Analyze the following resume.

RESUME:
--------------------
{resume_text}
--------------------

Return a JSON object containing:

{{
    "name": "",
    "email": "",
    "phone": "",
    "education": [],
    "skills": [],
    "programming_languages": [],
    "frameworks": [],
    "databases": [],
    "projects": [],
    "experience": [],
    "certifications": [],
    "achievements": [],
    "summary": "",
    "strengths": [],
    "possible_skill_gaps": []
}}

Rules:

1. Extract only information present in the resume.
2. Do not invent information.
3. Use an empty string if a single value is unavailable.
4. Use an empty array if multiple values are unavailable.
5. Keep project descriptions concise.
6. Return ONLY a valid JSON object.
"""

    response = generate_response(prompt)

    if not response:
        return {
            "error": "AI returned an empty response"
        }

    response = response.strip()

    if response.startswith("```json"):
        response = response[7:]

    elif response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    response = response.strip()

    try:

        return json.loads(response)

    except json.JSONDecodeError:

        return {
            "error": "AI returned an invalid JSON response",
            "raw_response": response
        }