from datetime import datetime

from pydantic import BaseModel


class AttemptCreate(BaseModel):
    problem_id: int
    solution: str


class AttemptResponse(BaseModel):
    id: int
    problem_id: int
    solution: str
    status: str
    feedback: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True