from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Backend.api.incidents import router as incidents_router
from Backend.api.memory import router as memory_router


app = FastAPI(
    title="RecallOps",
    description="AI-powered Incident Response Agent",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(incidents_router)
app.include_router(memory_router)


@app.get("/")
def root():
    return {
        "message": "RecallOps backend is running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }