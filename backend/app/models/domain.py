from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AttemptStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    EVALUATING = "evaluating"
    EVALUATED = "evaluated"
    FAILED = "failed"


@dataclass
class Problem:
    id: int
    title: str
    description: str
    requirements: list[str]


@dataclass
class Attempt:
    id: int
    problem_id: int
    solution: str
    status: AttemptStatus = AttemptStatus.DRAFT
    feedback: Optional[dict] = None
    created_at: datetime = field(default_factory=datetime.utcnow)