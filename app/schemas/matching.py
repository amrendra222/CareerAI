from pydantic import BaseModel


class MatchingRequest(BaseModel):

    resume_id: int

    job_id: int