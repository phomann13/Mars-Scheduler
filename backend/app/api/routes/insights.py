"""
API routes for course insights and career recommendations using RAG.
"""

from fastapi import APIRouter, HTTPException, Query
from app.services.vector_store_service import vectorStoreService
from typing import Optional, List, Dict, Any

router = APIRouter()


@router.get("/career-courses")
async def getCoursesForCareer(
    career: str = Query(..., description="Career interest or path"),
    limit: int = Query(15, ge=1, le=50, description="Number of courses to return")
):
    """
    Get course recommendations for a specific career path.
    
    Args:
        career: Career interest (e.g., "AI research", "software engineering")
        limit: Number of courses to return
        
    Returns:
        List of recommended courses
    """
    try:
        courses = await vectorStoreService.getCoursesForCareerPath(
            career, topK=limit
        )
        
        return {
            "career": career,
            "courses": courses,
            "count": len(courses)
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/similar-courses/{courseCode}")
async def getSimilarCourses(
    courseCode: str,
    limit: int = Query(5, ge=1, le=20, description="Number of similar courses")
):
    """
    Find courses similar to a given course.
    
    Args:
        courseCode: Course code to find similar courses for
        limit: Number of results
        
    Returns:
        List of similar courses
    """
    try:
        courses = await vectorStoreService.findCourseSimilarTo(
            courseCode, topK=limit
        )
        
        return {
            "baseCourse": courseCode,
            "similarCourses": courses,
            "count": len(courses)
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/search-courses")
async def semanticSearchCourses(request: Dict[str, Any]):
    """
    Semantic search for courses based on natural language query.
    
    Args:
        request: Dictionary with 'query' and optional 'filters', 'limit'
        
    Returns:
        List of relevant courses
    """
    try:
        query = request.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        filters = request.get("filters")
        limit = request.get("limit", 10)
        
        courses = await vectorStoreService.searchSimilarCourses(
            query=query,
            topK=limit,
            filters=filters
        )
        
        return {
            "query": query,
            "courses": courses,
            "count": len(courses)
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/index-course")
async def indexCourse(courseData: Dict[str, Any]):
    """
    Index a course into the vector store.
    
    Args:
        courseData: Course information
        
    Returns:
        Success status
    """
    try:
        success = await vectorStoreService.indexCourse(courseData)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to index course. Check vector store configuration."
            )
        
        return {
            "success": True,
            "courseCode": courseData.get("courseCode"),
            "message": "Course indexed successfully"
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/index-courses")
async def indexCourses(request: Dict[str, Any]):
    """
    Index multiple courses in batch.
    
    Args:
        request: Dictionary with 'courses' list
        
    Returns:
        Indexing statistics
    """
    try:
        courses = request.get("courses", [])
        
        if not courses:
            raise HTTPException(status_code=400, detail="Courses list is required")
        
        stats = await vectorStoreService.indexCourses(courses)
        
        return {
            "success": True,
            "totalCourses": len(courses),
            **stats
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/vector-store/stats")
async def getVectorStoreStats():
    """
    Get statistics about the vector store.
    
    Returns:
        Vector store statistics
    """
    try:
        stats = vectorStoreService.getStats()
        return stats
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/recommendations")
async def getRecommendations(
    interest: str = Query(..., description="Area of interest"),
    department: Optional[str] = Query(None, description="Filter by department"),
    level: Optional[str] = Query(None, description="Course level (100, 200, 300, 400)")
):
    """
    Get personalized course recommendations based on interests.
    
    Args:
        interest: Area of interest or career goal
        department: Optional department filter
        level: Optional course level filter
        
    Returns:
        Recommended courses
    """
    try:
        filters = {}
        
        if department:
            filters["department"] = department
        
        if level:
            filters["level"] = level
        
        courses = await vectorStoreService.searchSimilarCourses(
            query=f"Courses about {interest}",
            topK=15,
            filters=filters if filters else None
        )
        
        return {
            "interest": interest,
            "filters": filters,
            "recommendations": courses,
            "count": len(courses)
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

