
from fastapi import FastAPI
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.routers.auth import router as auth_router
from app.routers.agents import router as agents_router
from app.routers.tools import router as tools_router
from app.routers.authorization import router as authorization_router

app = FastAPI(
    title="AgentGuard API",
    description="AI Agent Security and Governance Platform",
    version="1.0.0"
)

# Register API routers
app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(tools_router)
app.include_router(authorization_router)
@app.get("/")
def home():
    return {
        "message": "Welcome to AgentGuard",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "AgentGuard Backend"
    }
