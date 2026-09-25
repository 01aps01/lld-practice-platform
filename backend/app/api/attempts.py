import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database_models import (
    AttemptModel,
    ProblemModel
)
from app.schemas.attempt import (
    AttemptCreate,
    AttemptResponse
)

from app.services.evaluation_service import EvaluationService


router = APIRouter(
    prefix="/attempts",
    tags=["Attempts"]
)


@router.post(
    "/",
    response_model=AttemptResponse
)
def create_attempt(
    attempt: AttemptCreate,
    db: Session = Depends(get_db)
):
    # Check that problem exists
    problem = (
        db.query(ProblemModel)
        .filter(ProblemModel.id == attempt.problem_id)
        .first()
    )

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    # Validate solution
    if not attempt.solution.strip():
        raise HTTPException(
            status_code=400,
            detail="Solution cannot be empty"
        )

    new_attempt = AttemptModel(
        problem_id=attempt.problem_id,
        solution=attempt.solution,
        status="submitted"
    )

    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    return new_attempt


@router.get(
    "/",
    response_model=list[AttemptResponse]
)
def get_attempts(
    db: Session = Depends(get_db)
):
    attempts = (
        db.query(AttemptModel)
        .order_by(AttemptModel.created_at.desc())
        .all()
    )

    return [
        AttemptResponse(
            id=attempt.id,
            problem_id=attempt.problem_id,
            solution=attempt.solution,
            status=attempt.status,
            feedback=(
                json.loads(attempt.feedback)
                if attempt.feedback
                else None
            ),
            created_at=attempt.created_at
        )
        for attempt in attempts
    ]


@router.get(
    "/{attempt_id}",
    response_model=AttemptResponse
)
def get_attempt(
    attempt_id: int,
    db: Session = Depends(get_db)
):
    attempt = (
        db.query(AttemptModel)
        .filter(AttemptModel.id == attempt_id)
        .first()
    )

    if not attempt:
        raise HTTPException(
            status_code=404,
            detail="Attempt not found"
        )

    return AttemptResponse(
        id=attempt.id,
        problem_id=attempt.problem_id,
        solution=attempt.solution,
        status=attempt.status,
        feedback=(
            json.loads(attempt.feedback)
            if attempt.feedback
            else None
        ),
        created_at=attempt.created_at
    )

@router.post(
    "/{attempt_id}/evaluate",
    response_model=AttemptResponse
)
def evaluate_attempt(
    attempt_id: int,
    db: Session = Depends(get_db)
):
    attempt = (
        db.query(AttemptModel)
        .filter(AttemptModel.id == attempt_id)
        .first()
    )

    if not attempt:
        raise HTTPException(
            status_code=404,
            detail="Attempt not found"
        )

    problem = (
        db.query(ProblemModel)
        .filter(ProblemModel.id == attempt.problem_id)
        .first()
    )

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    # Mark as evaluating
    attempt.status = "evaluating"
    db.commit()

    try:

        requirements = json.loads(
            problem.requirements
        )

        problem_context = f"""
Problem:
{problem.description}

Requirements:
{chr(10).join(
    "- " + requirement
    for requirement in requirements
)}
"""

        evaluator = EvaluationService()

        result = evaluator.evaluate(
            problem=problem_context,
            solution=attempt.solution
        )

        feedback = {
            "strengths": result.strengths,
            "issues": result.issues,
            "suggestions": result.suggestions,
            "tradeoffs": result.tradeoffs
        }

        attempt.feedback = json.dumps(feedback)

        attempt.status = "evaluated"

        db.commit()
        db.refresh(attempt)

        return AttemptResponse(
            id=attempt.id,
            problem_id=attempt.problem_id,
            solution=attempt.solution,
            status=attempt.status,
            feedback=feedback,
            created_at=attempt.created_at
        )

    except Exception as error:

        print(
            f"Evaluation failed: {error}"
        )

        attempt.status = "evaluation_failed"

        db.commit()
        db.refresh(attempt)

        raise HTTPException(
            status_code=503,
            detail=(
                "Evaluation temporarily failed. "
                "Your submission has been saved."
            )
        )
@router.post(
    "/{attempt_id}/retry-evaluation",
    response_model=AttemptResponse
)
def retry_evaluation(
    attempt_id: int,
    db: Session = Depends(get_db)
):
    attempt = (
        db.query(AttemptModel)
        .filter(AttemptModel.id == attempt_id)
        .first()
    )

    if not attempt:
        raise HTTPException(
            status_code=404,
            detail="Attempt not found"
        )

    if attempt.status not in [
        "evaluation_failed",
        "submitted"
    ]:
        raise HTTPException(
            status_code=400,
            detail="This attempt cannot be retried"
        )

    problem = (
        db.query(ProblemModel)
        .filter(
            ProblemModel.id == attempt.problem_id
        )
        .first()
    )

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    attempt.status = "evaluating"
    db.commit()

    try:

        requirements = json.loads(
            problem.requirements
        )

        problem_context = f"""
Problem:
{problem.description}

Requirements:
{chr(10).join(
    "- " + requirement
    for requirement in requirements
)}
"""

        evaluator = EvaluationService()

        result = evaluator.evaluate(
            problem=problem_context,
            solution=attempt.solution
        )

        feedback = {
            "strengths": result.strengths,
            "issues": result.issues,
            "suggestions": result.suggestions,
            "tradeoffs": result.tradeoffs
        }

        attempt.feedback = json.dumps(
            feedback
        )

        attempt.status = "evaluated"

        db.commit()
        db.refresh(attempt)

        return AttemptResponse(
            id=attempt.id,
            problem_id=attempt.problem_id,
            solution=attempt.solution,
            status=attempt.status,
            feedback=feedback,
            created_at=attempt.created_at
        )

    except Exception as error:

        print(
            f"Retry evaluation failed: {error}"
        )

        attempt.status = "evaluation_failed"

        db.commit()
        db.refresh(attempt)

        raise HTTPException(
            status_code=503,
            detail="Evaluation failed again. Please retry later."
        )