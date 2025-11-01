"""
API routes for schedule generation and management.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.schemas import ScheduleRequest, ScheduleResponse
from app.services.scheduling_engine import schedulingEngine
from app.services.umd_schedule_service import umdScheduleService
from typing import List

router = APIRouter()


@router.post("/generate", response_model=List[ScheduleResponse])
async def generateSchedules(request: ScheduleRequest):
    """
    Generate optimized schedules based on requirements and preferences.
    
    Args:
        request: Schedule generation request
        
    Returns:
        List of generated schedules
    """
    try:
        # Get available sections for required courses
        availableSections = {}
        
        if request.requiredCourses:
            for courseCode in request.requiredCourses:
                sections = await umdScheduleService.getSections(
                    courseId=courseCode,
                    semester=f"{request.year}{getSemesterCode(request.semester)}"
                )
                
                # Parse sections
                parsedSections = [
                    await umdScheduleService.parseSectionData(section)
                    for section in sections
                ]
                
                availableSections[courseCode] = parsedSections
        
        # Generate schedules
        preferences = request.preferences.dict() if request.preferences else {}
        
        schedules = await schedulingEngine.generateSchedules(
            requiredCourses=request.requiredCourses or [],
            availableSections=availableSections,
            preferences=preferences,
            maxSchedules=5
        )
        
        # Convert to response format (simplified)
        return [
            ScheduleResponse(
                id=idx + 1,
                userId=1,  # Would be from user lookup
                semester=request.semester,
                year=request.year,
                sections=[],  # Would extract section IDs
                score=schedule["score"],
                isActive=False,
                createdAt=None
            )
            for idx, schedule in enumerate(schedules)
        ]
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/{scheduleId}", response_model=ScheduleResponse)
async def getSchedule(scheduleId: int):
    """
    Get a specific schedule by ID.
    
    Args:
        scheduleId: Schedule identifier
        
    Returns:
        Schedule details
    """
    # Would fetch from database
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{scheduleId}")
async def deleteSchedule(scheduleId: int):
    """
    Delete a schedule.
    
    Args:
        scheduleId: Schedule identifier
        
    Returns:
        Success message
    """
    # Would delete from database
    return {"message": "Schedule deleted successfully"}


def getSemesterCode(semester: str) -> str:
    """Convert semester name to code."""
    mapping = {
        "Spring": "01",
        "Summer": "05",
        "Fall": "08",
        "Winter": "12"
    }
    return mapping.get(semester, "01")

