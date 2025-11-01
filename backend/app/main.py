"""
Main FastAPI application for UMD AI Scheduling Assistant.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import chat, schedules, plans, users, courses

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    chat.router,
    prefix=f"{settings.API_V1_STR}/chat",
    tags=["chat"]
)

app.include_router(
    schedules.router,
    prefix=f"{settings.API_V1_STR}/schedules",
    tags=["schedules"]
)

app.include_router(
    plans.router,
    prefix=f"{settings.API_V1_STR}/plans",
    tags=["plans"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)

app.include_router(
    courses.router,
    prefix=f"{settings.API_V1_STR}",
    tags=["courses"]
)


@app.get("/")
async def readRoot():
    """Root endpoint."""
    return {
        "message": "Welcome to UMD AI Scheduling Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def healthCheck():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

