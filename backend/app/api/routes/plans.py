"""
API routes for four-year plan generation and management.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.schemas import FourYearPlanRequest, FourYearPlanResponse
from app.services.four_year_plan_service import fourYearPlanService
from typing import List

router = APIRouter()


@router.post("/generate", response_model=FourYearPlanResponse)
async def generateFourYearPlan(request: FourYearPlanRequest):
    """
    Generate a four-year academic plan.
    
    Args:
        request: Plan generation request
        
    Returns:
        Generated four-year plan
    """
    try:
        preferences = request.preferences.dict() if request.preferences else {}
        
        plan = await fourYearPlanService.generatePlan(
            major=request.major,
            minor=request.minor,
            startSemester=request.startSemester,
            startYear=request.startYear,
            completedCourses=request.completedCourses or [],
            apCredits=request.apCredits or [],
            preferences=preferences
        )
        
        # Convert to response format
        return FourYearPlanResponse(
            id=1,  # Would be generated
            userId=1,  # Would be from user lookup
            planName=f"{request.major} - {request.startYear}",
            semesterPlans=plan["semesterPlans"],
            isActive=True,
            createdAt=None
        )
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/{planId}", response_model=FourYearPlanResponse)
async def getFourYearPlan(planId: int):
    """
    Get a specific four-year plan by ID.
    
    Args:
        planId: Plan identifier
        
    Returns:
        Plan details
    """
    # Would fetch from database
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/user/{userId}", response_model=List[FourYearPlanResponse])
async def getUserPlans(userId: str):
    """
    Get all plans for a specific user.
    
    Args:
        userId: User identifier
        
    Returns:
        List of user's plans
    """
    # Would fetch from database
    return []


@router.put("/{planId}", response_model=FourYearPlanResponse)
async def updateFourYearPlan(planId: int, request: FourYearPlanRequest):
    """
    Update an existing four-year plan.
    
    Args:
        planId: Plan identifier
        request: Updated plan data
        
    Returns:
        Updated plan
    """
    # Would update in database
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{planId}")
async def deleteFourYearPlan(planId: int):
    """
    Delete a four-year plan.
    
    Args:
        planId: Plan identifier
        
    Returns:
        Success message
    """
    # Would delete from database
    return {"message": "Plan deleted successfully"}

