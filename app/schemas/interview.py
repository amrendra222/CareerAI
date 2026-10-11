from pydantic import BaseModel


class PersonalizedInterviewRequest(BaseModel):

    resume_id: int

    job_id: int

    difficulty: str = "medium"


class InterviewSessionRequest(BaseModel):

    resume_id: int

    job_id: int

    difficulty: str = "medium"


class InterviewAnswerRequest(BaseModel):

    session_id: int

    question_id: int

    answer: str


class FinishInterviewRequest(BaseModel):

    session_id: int