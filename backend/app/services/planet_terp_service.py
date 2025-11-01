"""
Service for interacting with PlanetTerp API.
"""

import httpx
from typing import Optional, Dict, Any, List
from app.core.config import settings


class PlanetTerpService:
    """Service for fetching data from PlanetTerp API."""
    
    def __init__(self):
        self.baseUrl = settings.PLANET_TERP_API_URL
        
    async def getProfessorData(self, professorName: str) -> Optional[Dict[str, Any]]:
        """
        Fetch professor data from PlanetTerp.
        
        Args:
            professorName: Name of the professor
            
        Returns:
            Dictionary containing professor data or None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.baseUrl}/professors",
                    params={"name": professorName}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data if data else None
                    
                return None
                
        except Exception as error:
            print(f"Error fetching PlanetTerp data: {error}")
            return None
    
    async def getCourseData(self, courseCode: str) -> Optional[Dict[str, Any]]:
        """
        Fetch course data from PlanetTerp.
        
        Args:
            courseCode: Course code (e.g., "CMSC131")
            
        Returns:
            Dictionary containing course data or None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.baseUrl}/courses",
                    params={"name": courseCode}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data if data else None
                    
                return None
                
        except Exception as error:
            print(f"Error fetching course data: {error}")
            return None
    
    async def getGradeDistribution(self, 
                                   courseCode: str, 
                                   professorName: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch grade distribution for a course.
        
        Args:
            courseCode: Course code
            professorName: Optional professor name filter
            
        Returns:
            Dictionary containing grade distribution data or None
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {"course": courseCode}
                if professorName:
                    params["professor"] = professorName
                    
                response = await client.get(
                    f"{self.baseUrl}/grades",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data if data else None
                    
                return None
                
        except Exception as error:
            print(f"Error fetching grade distribution: {error}")
            return None
    
    async def calculateAverageGPA(self, grades: Dict[str, Any]) -> float:
        """
        Calculate average GPA from grade distribution.
        
        Args:
            grades: Grade distribution data
            
        Returns:
            Average GPA as float
        """
        gradePoints = {
            "A+": 4.0, "A": 4.0, "A-": 3.7,
            "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7,
            "D+": 1.3, "D": 1.0, "D-": 0.7,
            "F": 0.0
        }
        
        totalPoints = 0.0
        totalStudents = 0
        
        for grade, count in grades.items():
            if grade in gradePoints:
                totalPoints += gradePoints[grade] * count
                totalStudents += count
        
        return totalPoints / totalStudents if totalStudents > 0 else 0.0


planetTerpService = PlanetTerpService()

