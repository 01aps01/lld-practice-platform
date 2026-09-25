from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="LLD Practice Platform",
    description="A platform for practicing Low-Level Design",
    version="1.0.0"
)

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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