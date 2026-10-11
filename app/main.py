from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import inspect, text

from app.config import settings
from app.database import Base, engine

from app.models import (
    User,
    Resume,
    JobDescription,
    MatchResult,
    InterviewSession,
    InterviewQuestion
)

from app.routers.auth import router as auth_router
from app.routers.interview import router as interview_router
from app.routers.resume import router as resume_router
from app.routers.job import router as job_router
from app.routers.matching import router as matching_router


def migrate_database():

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    if "resumes" in tables:

        columns = [
            column["name"]
            for column in inspector.get_columns(
                "resumes"
            )
        ]

        if "user_id" not in columns:

            with engine.begin() as connection:

                connection.execute(
                    text(
                        "ALTER TABLE resumes "
                        "ADD COLUMN user_id INTEGER"
                    )
                )

            print(
                "Database migration: resumes.user_id added."
            )


@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(
        bind=engine
    )

    migrate_database()

    print(
        "CareerAI database initialized."
    )

    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Interviewer & Career Intelligence System",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(auth_router)

app.include_router(interview_router)

app.include_router(resume_router)

app.include_router(job_router)

app.include_router(matching_router)


@app.get("/")
def root():

    return {
        "application": "CareerAI",
        "status": "running",
        "message": "AI Interviewer & Career Intelligence System"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }