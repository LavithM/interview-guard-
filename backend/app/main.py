from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.interview import router as interview_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.candidate import router as candidate_router
from app.api.live import router as live_router
from app.api.admin_live_routes import router as admin_live_router
from app.api.live import router as live_router

app = FastAPI(
    title="InterviewGuard Backend",
    description="AI-powered interview analysis backend",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(interview_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(candidate_router)
app.include_router(admin_live_router)
app.include_router(live_router)


@app.get("/")
def root():
    return {
        "message": "InterviewGuard backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }