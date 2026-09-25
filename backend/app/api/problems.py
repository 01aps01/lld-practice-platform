import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database_models import ProblemModel
from app.schemas.problem import ProblemResponse

router = APIRouter(
    prefix="/problems",
    tags=["Problems"]
)


@router.get("/", response_model=list[ProblemResponse])
def get_problems(db: Session = Depends(get_db)):
    problems = db.query(ProblemModel).all()

    return [
        ProblemResponse(
            id=problem.id,
            title=problem.title,
            description=problem.description,
            requirements=json.loads(problem.requirements)
        )
        for problem in problems
    ]


@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem(
    problem_id: int,
    db: Session = Depends(get_db)
):
    problem = (
        db.query(ProblemModel)
        .filter(ProblemModel.id == problem_id)
        .first()
    )

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    return ProblemResponse(
        id=problem.id,
        title=problem.title,
        description=problem.description,
        requirements=json.loads(problem.requirements)
    )