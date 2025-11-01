"""
Service for interacting with UMD Schedule of Classes API.
"""

import httpx
from typing import Optional, Dict, Any, List
from app.core.config import settings


class UMDScheduleService:
    """Service for fetching UMD course schedule data."""
    
    def __init__(self):
        self.baseUrl = settings.UMD_SCHEDULE_API_URL
        
    async def getCourses(self, 
                        semester: Optional[str] = None,
                        department: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch courses from UMD Schedule API.
        
        Args:
            semester: Semester code (e.g., "202501" for Spring 2025)
            department: Department code (e.g., "CMSC")
            
        Returns:
            List of course dictionaries
        """
        try:
            params = {}
            if semester:
                params["semester"] = semester
            if department:
                params["dept_id"] = department
                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.baseUrl}/courses",
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json()
                    
                return []
                
        except Exception as error:
            print(f"Error fetching UMD courses: {error}")
            return []
    
    async def getCourseDetails(self, courseId: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information for a specific course.
        
        Args:
            courseId: Course identifier
            
        Returns:
            Dictionary containing course details or None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.baseUrl}/courses/{courseId}"
                )
                
                if response.status_code == 200:
                    return response.json()
                    
                return None
                
        except Exception as error:
            print(f"Error fetching course details: {error}")
            return None
    
    async def getSections(self, 
                         courseId: str,
                         semester: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch sections for a specific course.
        
        Args:
            courseId: Course identifier
            semester: Semester code
            
        Returns:
            List of section dictionaries
        """
        try:
            params = {}
            if semester:
                params["semester"] = semester
                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.baseUrl}/courses/{courseId}/sections",
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json()
                    
                return []
                
        except Exception as error:
            print(f"Error fetching sections: {error}")
            return []
    
    async def getDepartments(self) -> List[Dict[str, Any]]:
        """
        Fetch list of all departments.
        
        Returns:
            List of department dictionaries
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.baseUrl}/departments")
                
                if response.status_code == 200:
                    return response.json()
                    
                return []
                
        except Exception as error:
            print(f"Error fetching departments: {error}")
            return []
    
    async def parseSectionData(self, rawSection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw section data into standardized format.
        
        Args:
            rawSection: Raw section data from API
            
        Returns:
            Parsed section data
        """
        # Parse meeting times
        meetings = rawSection.get("meetings", [])
        days = []
        startTime = None
        endTime = None
        building = None
        room = None
        
        if meetings:
            meeting = meetings[0]  # Take first meeting
            days = meeting.get("days", [])
            startTime = meeting.get("start_time")
            endTime = meeting.get("end_time")
            building = meeting.get("building")
            room = meeting.get("room")
        
        return {
            "sectionNumber": rawSection.get("section"),
            "semester": rawSection.get("semester"),
            "year": self._extractYearFromSemester(rawSection.get("semester")),
            "days": days,
            "startTime": startTime,
            "endTime": endTime,
            "building": building,
            "room": room,
            "availableSeats": rawSection.get("open_seats"),
            "totalSeats": rawSection.get("seats"),
            "instructors": rawSection.get("instructors", [])
        }
    
    def _extractYearFromSemester(self, semester: Optional[str]) -> int:
        """
        Extract year from semester code.
        
        Args:
            semester: Semester code (e.g., "202501")
            
        Returns:
            Year as integer
        """
        if semester and len(semester) >= 4:
            return int(semester[:4])
        return 2025  # Default year


umdScheduleService = UMDScheduleService()

