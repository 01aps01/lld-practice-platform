from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.api.problems import router as problems_router

from app.models.database_models import ProblemModel

from app.api.attempts import router as attempts_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="LLD Practice Platform",
    description="A platform for practicing Low-Level Design",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(problems_router)
app.include_router(attempts_router)


@app.get("/")
def root():
    return {
        "message": "LLD Practice Platform API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }