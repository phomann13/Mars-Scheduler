"""
API routes initialization.
"""

from fastapi import APIRouter
from app.api.routes import chat, schedules, plans, courses, users, campus, insights

apiRouter = APIRouter()

# Include all route modules
apiRouter.include_router(chat.router, prefix="/chat", tags=["Chat"])
apiRouter.include_router(schedules.router, prefix="/schedules", tags=["Schedules"])
apiRouter.include_router(plans.router, prefix="/plans", tags=["Four-Year Plans"])
apiRouter.include_router(courses.router, prefix="/courses", tags=["Courses"])
apiRouter.include_router(users.router, prefix="/users", tags=["Users"])
apiRouter.include_router(campus.router, prefix="/campus", tags=["Campus & Buildings"])
apiRouter.include_router(insights.router, prefix="/insights", tags=["Course Insights & RAG"])
