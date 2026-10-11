import json

from app.services.llm_service import generate_response


def match_resume_with_job(
    resume_analysis: dict,
    job_analysis: dict
):

    prompt = f"""
You are CareerAI, an expert career intelligence system.

Compare the candidate resume against the target job description.

CANDIDATE RESUME ANALYSIS:
-------------------------
{json.dumps(resume_analysis, indent=2)}
-------------------------

JOB DESCRIPTION ANALYSIS:
-------------------------
{json.dumps(job_analysis, indent=2)}
-------------------------

Calculate a realistic job-fit assessment.

Return ONLY a valid JSON object using exactly this structure:

{{
    "match_score": 0,
    "matched_skills": [],
    "missing_required_skills": [],
    "missing_preferred_skills": [],
    "strong_areas": [],
    "weak_areas": [],
    "experience_match": "",
    "education_match": "",
    "recommendation": "",
    "interview_priorities": [],
    "learning_priorities": []
}}

Rules:

1. match_score must be between 0 and 100.
2. Compare skills based on the actual resume and job description.
3. Do not invent candidate skills.
4. Required skill gaps are more important than preferred skill gaps.
5. Consider programming languages, frameworks, databases and AI/ML skills.
6. Consider education and experience requirements when available.
7. Keep recommendations practical.
8. interview_priorities should contain topics the candidate should prepare first.
9. learning_priorities should contain skills that should be learned or improved.
10. Return ONLY valid JSON.
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