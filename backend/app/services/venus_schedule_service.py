"""
Service for interacting with the Venus UMD Schedule API.
"""

import httpx
from typing import List, Dict, Any, Optional


class VenusScheduleService:
    """Service for generating schedules using the Venus UMD API."""
    
    def __init__(self):
        self.baseUrl = "https://venus.umd.edu/api/schedule"
        self.timeout = 30.0
    
    async def generateSchedules(self,
                                termId: str,
                                requiredCourses: List[str],
                                optionalCourses: Optional[List[str]] = None,
                                minCredits: int = 1,
                                maxCredits: int = 20,
                                waitlistLimit: int = -1) -> List[Dict[str, Any]]:
        """
        Generate schedules using the Venus UMD API.
        
        Args:
            termId: Semester term ID (e.g., "202601" for Spring 2026)
            requiredCourses: List of required course codes (e.g., ["CMSC131", "MATH140"])
            optionalCourses: List of optional course codes
            minCredits: Minimum credits
            maxCredits: Maximum credits
            waitlistLimit: Waitlist limit (-1 for unlimited)
            
        Returns:
            List of schedule dictionaries
        """
        try:
            # Build required sections (All for each course)
            requiredSections = ["All"] * len(requiredCourses)
            
            # Prepare query parameters
            params = {
                "termId": termId,
                "requiredCourses": ",".join(requiredCourses),
                "optionalCourses": ",".join(optionalCourses or []),
                "requiredSections": ",".join(requiredSections),
                "optionalSections": "",
                "exclusions": "",
                "minCredits": minCredits,
                "maxCredits": maxCredits,
                "waitlistLimit": waitlistLimit,
                "dsstate": "",
                "teachingCenter": "*",
                "delivery": ""
            }
            
            # Make API request (don't follow redirects to detect auth issues)
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
                response = await client.get(self.baseUrl, params=params)
                
                # Check for authentication redirect
                if response.status_code in [301, 302, 303, 307, 308]:
                    print(f"⚠️  Venus API requires authentication (redirect to: {response.headers.get('Location')})")
                    return []
                
                response.raise_for_status()
                
                schedules = response.json()
                
                # Transform schedules to include metadata
                for schedule in schedules:
                    schedule["termId"] = termId
                    schedule["courses"] = requiredCourses
                
                return schedules
                
        except httpx.HTTPStatusError as error:
            print(f"❌ HTTP error calling Venus API: {error}")
            return []
        except httpx.HTTPError as error:
            print(f"❌ Network error calling Venus API: {error}")
            return []
        except Exception as error:
            print(f"❌ Error generating schedules: {error}")
            return []
    
    def convertTimeToString(self, timeInMinutes: int) -> str:
        """
        Convert time in minutes from midnight to readable format.
        
        Args:
            timeInMinutes: Time in minutes (e.g., 540 = 9:00 AM)
            
        Returns:
            Formatted time string (e.g., "9:00 AM")
        """
        hours = timeInMinutes // 60
        minutes = timeInMinutes % 60
        
        period = "AM" if hours < 12 else "PM"
        displayHours = hours if hours <= 12 else hours - 12
        if displayHours == 0:
            displayHours = 12
        
        return f"{displayHours}:{minutes:02d} {period}"
    
    def getSemesterTermId(self, semester: str, year: int) -> str:
        """
        Convert semester name and year to term ID.
        
        Args:
            semester: Semester name (Fall, Spring, Summer)
            year: Year (e.g., 2025)
            
        Returns:
            Term ID (e.g., "202601")
        """
        semesterCodes = {
            "Spring": "01",
            "Summer": "05",
            "Fall": "08",
            "Winter": "12"
        }
        
        code = semesterCodes.get(semester, "01")
        return f"{year}{code}"


venusScheduleService = VenusScheduleService()

