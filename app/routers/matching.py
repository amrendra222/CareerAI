import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.career import (
    Resume,
    JobDescription,
    MatchResult
)
from app.schemas.matching import MatchingRequest
from app.services.matching_service import match_resume_with_job


router = APIRouter(
    prefix="/api/matching",
    tags=["Career Intelligence"]
)


@router.post("/analyze")
def analyze_match(
    request: MatchingRequest,
    db: Session = Depends(get_db)
):

    # Find resume
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id
    ).first()

    if not resume:

        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    # Find job description
    job = db.query(JobDescription).filter(
        JobDescription.id == request.job_id
    ).first()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job description not found."
        )

    # Read stored AI analysis
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
            detail="Stored resume or job analysis contains invalid JSON."
        )

    # Generate matching analysis
    result = match_resume_with_job(
        resume_analysis=resume_analysis,
        job_analysis=job_analysis
    )

    if "error" in result:

        raise HTTPException(
            status_code=500,
            detail=result
        )

    # Save match result
    match = MatchResult(
        resume_id=request.resume_id,
        job_id=request.job_id,
        result_json=json.dumps(result)
    )

    db.add(match)

    db.commit()

    db.refresh(match)

    return {
        "success": True,
        "match_id": match.id,
        "resume_id": request.resume_id,
        "job_id": request.job_id,
        "matching": result
    }