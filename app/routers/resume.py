import json
import os
import tempfile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.career import Resume, User
from app.routers.auth import get_current_user

from app.services.resume_service import (
    analyze_resume,
    extract_text_from_pdf
)


router = APIRouter(
    prefix="/api/resume",
    tags=["Resume Intelligence"]
)


@router.get("/list")
def list_resumes(
    db: Session = Depends(get_db)
):
    resumes = (
        db.query(Resume)
        .order_by(
            Resume.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": resume.id,
            "filename": resume.filename,
            "created_at": (
                resume.created_at.isoformat()
                if resume.created_at
                else None
            ),
        }
        for resume in resumes
    ]


@router.post("/analyze")
async def analyze_resume_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
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
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(contents)
            temp_path = temp_file.name

        resume_text = extract_text_from_pdf(
            temp_path
        )

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text "
                    "from the PDF."
                )
            )

        analysis = analyze_resume(
            resume_text
        )

        if "error" in analysis:
            raise HTTPException(
                status_code=500,
                detail=analysis
            )

        resume = Resume(
            user_id=current_user.id,
            filename=file.filename,
            resume_text=resume_text,
            analysis_json=json.dumps(
                analysis
            )
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return {
            "success": True,
            "resume_id": resume.id,
            "filename": resume.filename,
            "analysis": analysis
        }

    except HTTPException:
        raise

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Resume processing failed: "
                f"{str(error)}"
            )
        )

    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)


@router.get("/my-resumes")
def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    resumes = (
        db.query(Resume)
        .filter(
            Resume.user_id == current_user.id
        )
        .order_by(
            Resume.id.desc()
        )
        .all()
    )

    return {
        "success": True,
        "resumes": [
            {
                "id": resume.id,
                "filename": resume.filename,
                "created_at": (
                    resume.created_at.isoformat()
                    if resume.created_at
                    else None
                )
            }
            for resume in resumes
        ]
    }


@router.delete("/duplicates/cleanup")
def cleanup_duplicate_resumes(
    db: Session = Depends(get_db)
):

    resumes = (
        db.query(Resume)
        .order_by(
            Resume.created_at.desc(),
            Resume.id.desc()
        )
        .all()
    )

    seen = set()
    duplicates = []

    for resume in resumes:

        resume_text = (
            resume.resume_text or ""
        ).strip()

        if not resume_text:
            continue

        if resume_text in seen:
            duplicates.append(resume)
        else:
            seen.add(resume_text)

    deleted_count = 0

    for resume in duplicates:
        db.delete(resume)
        deleted_count += 1

    db.commit()

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": (
            f"Removed {deleted_count} "
            "duplicate resume(s)."
        )
    }

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    db.delete(resume)
    db.commit()

    return {
        "success": True,
        "message": "Resume deleted successfully.",
        "id": resume_id
    }