import json

from app.services.llm_service import generate_response


def clean_json_response(response: str):

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


# ============================================================
# 1. GENERATE PERSONALIZED FIRST QUESTION
# ============================================================

def generate_personalized_question(
    resume_analysis: dict,
    job_analysis: dict,
    match_result: dict,
    difficulty: str = "medium"
):

    prompt = f"""
You are CareerAI, an expert technical interviewer.

Generate ONE personalized interview question for the candidate.

CANDIDATE RESUME:
-------------------------
{json.dumps(resume_analysis, indent=2)}
-------------------------

TARGET JOB:
-------------------------
{json.dumps(job_analysis, indent=2)}
-------------------------

JOB MATCH ANALYSIS:
-------------------------
{json.dumps(match_result, indent=2)}
-------------------------

DIFFICULTY:
{difficulty}

Rules:

1. Generate exactly ONE question.
2. The question must be relevant to the target job.
3. Use the candidate's actual skills and projects where appropriate.
4. Consider missing skills and weak areas.
5. Do not invent candidate experience.
6. Do not provide the answer.
7. Do not ask multiple questions.
8. Make it realistic for an actual technical interview.

Return ONLY the interview question.
"""

    return generate_response(prompt).strip()


# ============================================================
# 2. EVALUATE ANSWER
# ============================================================

def evaluate_interview_answer(
    question: str,
    answer: str,
    resume_analysis: dict,
    job_analysis: dict
):

    prompt = f"""
You are CareerAI, an expert technical interviewer.

Evaluate the candidate's answer.

QUESTION:
-------------------------
{question}
-------------------------

CANDIDATE ANSWER:
-------------------------
{answer}
-------------------------

CANDIDATE RESUME:
-------------------------
{json.dumps(resume_analysis, indent=2)}
-------------------------

TARGET JOB:
-------------------------
{json.dumps(job_analysis, indent=2)}
-------------------------

Return ONLY valid JSON:

{{
    "score": 0,
    "technical_accuracy": 0,
    "relevance": 0,
    "clarity": 0,
    "completeness": 0,
    "strengths": [],
    "weaknesses": [],
    "feedback": "",
    "ideal_answer_points": [],
    "improvement_tips": []
}}

Rules:

1. All scores must be between 0 and 100.
2. Evaluate only what the candidate actually answered.
3. Do not invent candidate knowledge.
4. Consider the target job.
5. Be fair and realistic.
6. Identify strengths and weaknesses.
7. Give practical feedback.
8. Return ONLY valid JSON.
"""

    response = generate_response(prompt)

    return clean_json_response(response)


# ============================================================
# 3. GENERATE NEXT ADAPTIVE QUESTION
# ============================================================

def generate_next_question(
    previous_question: str,
    candidate_answer: str,
    evaluation: dict,
    resume_analysis: dict,
    job_analysis: dict,
    difficulty: str = "medium"
):

    prompt = f"""
You are CareerAI, an expert adaptive technical interviewer.

Generate the NEXT interview question.

PREVIOUS QUESTION:
-------------------------
{previous_question}
-------------------------

CANDIDATE ANSWER:
-------------------------
{candidate_answer}
-------------------------

PREVIOUS EVALUATION:
-------------------------
{json.dumps(evaluation, indent=2)}
-------------------------

CANDIDATE RESUME:
-------------------------
{json.dumps(resume_analysis, indent=2)}
-------------------------

TARGET JOB:
-------------------------
{json.dumps(job_analysis, indent=2)}
-------------------------

DIFFICULTY:
{difficulty}

Rules:

1. Generate exactly ONE question.
2. Make it relevant to the target job.
3. Adapt it based on the previous answer.
4. If the candidate performed strongly, increase depth.
5. If the candidate performed poorly, test the missing concept.
6. Do not repeat the previous question.
7. Do not invent candidate experience.
8. Do not provide the answer.
9. Do not ask multiple questions.
10. Make it realistic for an actual technical interview.

Return ONLY the interview question.
"""

    return generate_response(prompt).strip()


# ============================================================
# 4. FINAL INTERVIEW REPORT
# ============================================================

def generate_final_interview_report(
    interview_results: list,
    resume_analysis: dict,
    job_analysis: dict
):

    prompt = f"""
You are CareerAI, an expert technical interview assessment system.

Generate a final interview performance report.

CANDIDATE RESUME:
-------------------------
{json.dumps(resume_analysis, indent=2)}
-------------------------

TARGET JOB:
-------------------------
{json.dumps(job_analysis, indent=2)}
-------------------------

INTERVIEW RESULTS:
-------------------------
{json.dumps(interview_results, indent=2)}
-------------------------

Return ONLY valid JSON:

{{
    "overall_score": 0,
    "technical_score": 0,
    "communication_score": 0,
    "problem_solving_score": 0,
    "questions_answered": 0,
    "strong_areas": [],
    "weak_areas": [],
    "key_strengths": [],
    "improvement_areas": [],
    "recommended_topics": [],
    "overall_feedback": "",
    "hiring_recommendation": ""
}}

Rules:

1. All scores must be between 0 and 100.
2. Base the report only on actual interview answers.
3. Do not invent information.
4. Consider the target job requirements.
5. Consider the candidate's actual resume.
6. Identify repeated weaknesses.
7. Identify demonstrated strengths.
8. Give practical recommended topics.
9. Give a realistic hiring recommendation.
10. Return ONLY valid JSON.
"""

    response = generate_response(prompt)

    return clean_json_response(response)