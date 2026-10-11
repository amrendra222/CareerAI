import json

from PyPDF2 import PdfReader

from app.services.llm_service import generate_response


def extract_job_description(file_path: str) -> str:

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def analyze_job_description(job_text: str):

    prompt = f"""
You are CareerAI, an expert job description analysis system.

Analyze the following job description.

JOB DESCRIPTION
-------------------------
{job_text}
-------------------------

Return ONLY a valid JSON object using exactly this structure:

{{
    "job_title": "",
    "company": "",
    "location": "",
    "experience_required": "",
    "education_required": "",
    "required_skills": [],
    "preferred_skills": [],
    "programming_languages": [],
    "frameworks": [],
    "databases": [],
    "ai_ml_skills": [],
    "cloud_skills": [],
    "tools": [],
    "responsibilities": [],
    "qualifications": [],
    "important_keywords": [],
    "summary": ""
}}

Rules:

1. Extract information only from the job description.
2. Do not invent skills or requirements.
3. If information is missing, use an empty string or empty array.
4. Separate required skills from preferred skills.
5. Extract technologies individually.
6. Keep responsibilities concise.
7. Return ONLY valid JSON.
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