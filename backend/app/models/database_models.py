from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.database import Base


class ProblemModel(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)


class AttemptModel(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)

    problem_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    solution = Column(Text, nullable=False)

    status = Column(
        String(50),
        nullable=False,
        default="submitted"
    )

    feedback = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )