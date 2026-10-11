import json
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.career import JobDescription
from app.services.job_service import (
    analyze_job_description,
    extract_job_description
)


router = APIRouter(
    prefix="/api/job",
    tags=["Job Intelligence"]
)

@router.get("/list")
def list_jobs(db: Session = Depends(get_db)):
    jobs = (
        db.query(JobDescription)
        .order_by(JobDescription.created_at.desc())
        .all()
    )

    return [
        {
            "id": job.id,
            "filename": job.filename,
            "created_at": (
                job.created_at.isoformat()
                if job.created_at
                else None
            ),
        }
        for job in jobs
    ]


@router.post("/analyze")
async def analyze_job_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    allowed_extensions = [".pdf", ".txt"]

    filename = file.filename or ""

    extension = os.path.splitext(filename)[1].lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )

    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_file.write(contents)

            temp_path = temp_file.name

        if extension == ".pdf":

            job_text = extract_job_description(temp_path)

        else:

            job_text = contents.decode(
                "utf-8",
                errors="ignore"
            )

        if not job_text.strip():

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the job description."
            )

        analysis = analyze_job_description(job_text)

        if "error" in analysis:

            raise HTTPException(
                status_code=500,
                detail=analysis
            )

        job = JobDescription(
            filename=filename,
            job_text=job_text,
            analysis_json=json.dumps(analysis)
        )

        db.add(job)

        db.commit()

        db.refresh(job)

        return {
            "success": True,
            "job_id": job.id,
            "filename": job.filename,
            "analysis": analysis
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Job processing failed: {str(e)}"
        )

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)