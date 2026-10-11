import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.career import (
    Resume,
    JobDescription,
    MatchResult,
    InterviewSession,
    InterviewQuestion
)

from app.schemas.interview import (
    PersonalizedInterviewRequest,
    InterviewSessionRequest,
    InterviewAnswerRequest,
    FinishInterviewRequest
)

from app.services.interview_service import (
    generate_personalized_question,
    evaluate_interview_answer,
    generate_next_question,
    generate_final_interview_report
)


router = APIRouter(
    prefix="/api/interview",
    tags=["Interview"]
)


# ============================================================
# PERSONALIZED QUESTION
# ============================================================

@router.post("/question")
def personalized_question(
    request: PersonalizedInterviewRequest,
    db: Session = Depends(get_db)
):

    resume = db.query(Resume).filter(
        Resume.id == request.resume_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    job = db.query(JobDescription).filter(
        JobDescription.id == request.job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job description not found."
        )

    match = db.query(MatchResult).filter(
        MatchResult.resume_id == request.resume_id,
        MatchResult.job_id == request.job_id
    ).order_by(
        MatchResult.id.desc()
    ).first()

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Matching result not found. Run matching first."
        )

    try:

        resume_analysis = json.loads(
            resume.analysis_json
        )

        job_analysis = json.loads(
            job.analysis_json
        )

        match_result = json.loads(
            match.result_json
        )

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail="Stored analysis contains invalid JSON."
        )

    question = generate_personalized_question(
        resume_analysis=resume_analysis,
        job_analysis=job_analysis,
        match_result=match_result,
        difficulty=request.difficulty
    )

    return {
        "success": True,
        "resume_id": request.resume_id,
        "job_id": request.job_id,
        "match_id": match.id,
        "difficulty": request.difficulty,
        "question": question
    }


# ============================================================
# START INTERVIEW
# ============================================================

@router.post("/start")
def start_interview(
    request: InterviewSessionRequest,
    db: Session = Depends(get_db)
):

    resume = db.query(Resume).filter(
        Resume.id == request.resume_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    job = db.query(JobDescription).filter(
        JobDescription.id == request.job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job description not found."
        )

    match = db.query(MatchResult).filter(
        MatchResult.resume_id == request.resume_id,
        MatchResult.job_id == request.job_id
    ).order_by(
        MatchResult.id.desc()
    ).first()

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Matching result not found. Run matching first."
        )

    try:

        resume_analysis = json.loads(
            resume.analysis_json
        )

        job_analysis = json.loads(
            job.analysis_json
        )

        match_result = json.loads(
            match.result_json
        )

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail="Stored analysis contains invalid JSON."
        )

    question_text = generate_personalized_question(
        resume_analysis=resume_analysis,
        job_analysis=job_analysis,
        match_result=match_result,
        difficulty=request.difficulty
    )

    if not question_text:

        raise HTTPException(
            status_code=500,
            detail="Could not generate interview question."
        )

    session = InterviewSession(
        resume_id=request.resume_id,
        job_id=request.job_id,
        difficulty=request.difficulty,
        status="active"
    )

    db.add(session)

    db.commit()

    db.refresh(session)

    question = InterviewQuestion(
        session_id=session.id,
        question_number=1,
        question=question_text
    )

    db.add(question)

    db.commit()

    db.refresh(question)

    return {
        "success": True,
        "session_id": session.id,
        "question_id": question.id,
        "question_number": 1,
        "difficulty": request.difficulty,
        "question": question.question
    }


# ============================================================
# SUBMIT ANSWER
# ============================================================

@router.post("/answer")
def submit_answer(
    request: InterviewAnswerRequest,
    db: Session = Depends(get_db)
):

    session = db.query(InterviewSession).filter(
        InterviewSession.id == request.session_id
    ).first()

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Interview session not found."
        )

    if session.status != "active":

        raise HTTPException(
            status_code=400,
            detail="Interview session is not active."
        )

    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == request.question_id,
        InterviewQuestion.session_id == request.session_id
    ).first()

    if not question:

        raise HTTPException(
            status_code=404,
            detail="Interview question not found."
        )

    if question.answer is not None:

        raise HTTPException(
            status_code=400,
            detail="This question has already been answered."
        )

    if not request.answer.strip():

        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty."
        )

    resume = db.query(Resume).filter(
        Resume.id == session.resume_id
    ).first()

    if not resume:

        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    job = db.query(JobDescription).filter(
        JobDescription.id == session.job_id
    ).first()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job description not found."
        )

    try:

        resume_analysis = json.loads(
            resume.analysis_json
        )

        job_analysis = json.loads(
            job.analysis_json
        )

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail="Stored analysis contains invalid JSON."
        )

    # Evaluate current answer

    evaluation = evaluate_interview_answer(
        question=question.question,
        answer=request.answer,
        resume_analysis=resume_analysis,
        job_analysis=job_analysis
    )

    if "error" in evaluation:

        raise HTTPException(
            status_code=500,
            detail=evaluation
        )

    # Save answer and evaluation

    question.answer = request.answer

    question.evaluation_json = json.dumps(
        evaluation
    )

    db.commit()

    # Generate adaptive next question

    next_question_text = generate_next_question(
        previous_question=question.question,
        candidate_answer=request.answer,
        evaluation=evaluation,
        resume_analysis=resume_analysis,
        job_analysis=job_analysis,
        difficulty=session.difficulty
    )

    if not next_question_text:

        return {
            "success": True,
            "session_id": session.id,
            "question_id": question.id,
            "evaluation": evaluation,
            "next_question": None
        }

    next_question_number = question.question_number + 1

    next_question = InterviewQuestion(
        session_id=session.id,
        question_number=next_question_number,
        question=next_question_text
    )

    db.add(next_question)

    db.commit()

    db.refresh(next_question)

    return {
        "success": True,
        "session_id": session.id,
        "question_id": question.id,
        "evaluation": evaluation,
        "next_question_id": next_question.id,
        "next_question_number": next_question_number,
        "next_question": next_question.question
    }


# ============================================================
# FINISH INTERVIEW
# ============================================================

@router.post("/finish")
def finish_interview(
    request: FinishInterviewRequest,
    db: Session = Depends(get_db)
):

    session = db.query(InterviewSession).filter(
        InterviewSession.id == request.session_id
    ).first()

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Interview session not found."
        )

    if session.status == "completed":

        raise HTTPException(
            status_code=400,
            detail="Interview is already completed."
        )

    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id
    ).order_by(
        InterviewQuestion.question_number.asc()
    ).all()

    answered_questions = [
        question
        for question in questions
        if question.answer is not None
    ]

    if not answered_questions:

        raise HTTPException(
            status_code=400,
            detail="Answer at least one question before finishing."
        )

    resume = db.query(Resume).filter(
        Resume.id == session.resume_id
    ).first()

    if not resume:

        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    job = db.query(JobDescription).filter(
        JobDescription.id == session.job_id
    ).first()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job description not found."
        )

    try:

        resume_analysis = json.loads(
            resume.analysis_json
        )

        job_analysis = json.loads(
            job.analysis_json
        )

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail="Stored analysis contains invalid JSON."
        )

    interview_results = []

    for question in answered_questions:

        evaluation = {}

        if question.evaluation_json:

            try:

                evaluation = json.loads(
                    question.evaluation_json
                )

            except json.JSONDecodeError:

                evaluation = {
                    "error": "Invalid evaluation JSON"
                }

        interview_results.append(
            {
                "question_number": question.question_number,
                "question": question.question,
                "answer": question.answer,
                "evaluation": evaluation
            }
        )

    report = generate_final_interview_report(
        interview_results=interview_results,
        resume_analysis=resume_analysis,
        job_analysis=job_analysis
    )

    if "error" in report:

        raise HTTPException(
            status_code=500,
            detail=report
        )

    session.status = "completed"

    db.commit()

    return {
        "success": True,
        "session_id": session.id,
        "status": session.status,
        "questions_answered": len(answered_questions),
        "report": report
    }