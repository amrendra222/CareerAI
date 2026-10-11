from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Text

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        Text,
        nullable=False
    )

    email = Column(
        Text,
        nullable=False,
        unique=True,
        index=True
    )

    password_hash = Column(
        Text,
        nullable=False
    )

    auth_token_hash = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
clerk_id = Column(
    Text,
    nullable=True,
    unique=True,
    index=True
)

class Resume(Base):

    __tablename__ = "resumes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    filename = Column(
        Text,
        nullable=False
    )

    resume_text = Column(
        Text,
        nullable=False
    )

    analysis_json = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class JobDescription(Base):

    __tablename__ = "job_descriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        Text,
        nullable=False
    )

    job_text = Column(
        Text,
        nullable=False
    )

    analysis_json = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class MatchResult(Base):

    __tablename__ = "match_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    resume_id = Column(
        Integer,
        nullable=False
    )

    job_id = Column(
        Integer,
        nullable=False
    )

    result_json = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class InterviewSession(Base):

    __tablename__ = "interview_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    resume_id = Column(
        Integer,
        nullable=False
    )

    job_id = Column(
        Integer,
        nullable=False
    )

    difficulty = Column(
        Text,
        nullable=False,
        default="medium"
    )

    status = Column(
        Text,
        nullable=False,
        default="active"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class InterviewQuestion(Base):

    __tablename__ = "interview_questions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    session_id = Column(
        Integer,
        nullable=False
    )

    question_number = Column(
        Integer,
        nullable=False
    )

    question = Column(
        Text,
        nullable=False
    )

    answer = Column(
        Text,
        nullable=True
    )

    evaluation_json = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )