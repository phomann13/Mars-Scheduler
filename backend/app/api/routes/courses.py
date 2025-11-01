"""
API routes for course and professor data.
"""

from fastapi import APIRouter, HTTPException, Query
from app.services.planet_terp_service import planetTerpService
from app.services.rate_my_professor_service import rateMyProfessorService
from app.services.umd_schedule_service import umdScheduleService
from typing import Optional, List, Dict, Any

router = APIRouter()


@router.get("/courses")
async def searchCourses(
    department: Optional[str] = Query(None),
    semester: Optional[str] = Query(None)
):
    """
    Search for courses.
    
    Args:
        department: Filter by department code
        semester: Filter by semester
        
    Returns:
        List of courses
    """
    try:
        courses = await umdScheduleService.getCourses(
            semester=semester,
            department=department
        )
        return {"courses": courses}
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/courses/{courseCode}")
async def getCourseDetails(courseCode: str):
    """
    Get detailed information about a course.
    
    Args:
        courseCode: Course code (e.g., "CMSC131")
        
    Returns:
        Course details with professor ratings and grade distribution
    """
    try:
        # Get course data from multiple sources
        planetTerpData = await planetTerpService.getCourseData(courseCode)
        umdData = await umdScheduleService.getCourseDetails(courseCode)
        
        return {
            "courseCode": courseCode,
            "planetTerp": planetTerpData,
            "umdData": umdData
        }
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/professors/{professorName}")
async def getProfessorDetails(professorName: str):
    """
    Get detailed information about a professor.
    
    Args:
        professorName: Professor's name
        
    Returns:
        Professor details with ratings from multiple sources
    """
    try:
        # Get professor data from multiple sources
        planetTerpData = await planetTerpService.getProfessorData(professorName)
        rmpData = await rateMyProfessorService.searchProfessor(professorName)
        
        # Calculate aggregated score
        aggregatedScore = calculateAggregatedScore(planetTerpData, rmpData)
        
        return {
            "name": professorName,
            "planetTerp": planetTerpData,
            "rateMyProfessor": rmpData,
            "aggregatedScore": aggregatedScore
        }
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/departments")
async def getDepartments():
    """
    Get list of all departments.
    
    Returns:
        List of departments
    """
    try:
        departments = await umdScheduleService.getDepartments()
        return {"departments": departments}
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


def calculateAggregatedScore(
    planetTerpData: Optional[Dict[str, Any]],
    rmpData: Optional[Dict[str, Any]]
) -> float:
    """
    Calculate aggregated professor score from multiple sources.
    
    Args:
        planetTerpData: Data from PlanetTerp
        rmpData: Data from RateMyProfessor
        
    Returns:
        Aggregated score (0-5)
    """
    scores = []
    
    if planetTerpData:
        rating = planetTerpData.get("rating")
        if rating:
            scores.append(rating)
    
    if rmpData:
        rating = rmpData.get("rating")
        if rating:
            scores.append(rating)
    
    return sum(scores) / len(scores) if scores else 3.0

