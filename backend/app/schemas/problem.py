from pydantic import BaseModel


class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    requirements: list[str]

    class Config:
        from_attributes = True