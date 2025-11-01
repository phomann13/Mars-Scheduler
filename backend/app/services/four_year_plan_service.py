"""
Service for generating four-year academic plans.
"""

from typing import List, Dict, Any, Optional


class FourYearPlanService:
    """Service for generating personalized four-year academic plans."""
    
    def __init__(self):
        self.curriculumData = self._loadCurriculumData()
    
    async def generatePlan(self,
                          major: str,
                          minor: Optional[str],
                          startSemester: str,
                          startYear: int,
                          completedCourses: List[str],
                          apCredits: List[str],
                          preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a four-year academic plan.
        
        Args:
            major: Student's major
            minor: Optional minor
            startSemester: Starting semester (Fall/Spring)
            startYear: Starting year
            completedCourses: List of completed course codes
            apCredits: List of AP credits
            preferences: Student preferences
            
        Returns:
            Four-year plan dictionary
        """
        # Get curriculum requirements
        majorRequirements = self._getMajorRequirements(major)
        minorRequirements = self._getMinorRequirements(minor) if minor else []
        genEdRequirements = self._getGenEdRequirements()
        
        # Calculate remaining requirements
        remainingCourses = self._calculateRemainingCourses(
            majorRequirements,
            minorRequirements,
            genEdRequirements,
            completedCourses,
            apCredits
        )
        
        # Generate semester-by-semester plan
        semesterPlans = self._distributeCourses(
            remainingCourses,
            startSemester,
            startYear,
            preferences
        )
        
        return {
            "major": major,
            "minor": minor,
            "semesterPlans": semesterPlans,
            "totalCredits": sum(plan["totalCredits"] for plan in semesterPlans)
        }
    
    def _getMajorRequirements(self, major: str) -> List[Dict[str, Any]]:
        """Get major requirements from curriculum data."""
        majorData = self.curriculumData.get(major, {})
        
        return [
            {
                "courseCode": course["code"],
                "courseName": course["name"],
                "credits": course["credits"],
                "prerequisites": course.get("prerequisites", []),
                "category": course.get("category", "major")
            }
            for course in majorData.get("required", [])
        ]
    
    def _getMinorRequirements(self, minor: str) -> List[Dict[str, Any]]:
        """Get minor requirements."""
        minorData = self.curriculumData.get(f"{minor}_minor", {})
        
        return [
            {
                "courseCode": course["code"],
                "courseName": course["name"],
                "credits": course["credits"],
                "prerequisites": course.get("prerequisites", []),
                "category": "minor"
            }
            for course in minorData.get("required", [])
        ]
    
    def _getGenEdRequirements(self) -> List[Dict[str, Any]]:
        """Get general education requirements."""
        return [
            {
                "category": "genEd",
                "requirement": "FSAR",
                "credits": 3,
                "description": "Fundamental Studies: Arts"
            },
            {
                "category": "genEd",
                "requirement": "FSMA",
                "credits": 3,
                "description": "Fundamental Studies: Math"
            },
            {
                "category": "genEd",
                "requirement": "FSOC",
                "credits": 3,
                "description": "Fundamental Studies: Social Science"
            },
            {
                "category": "genEd",
                "requirement": "FSPW",
                "credits": 3,
                "description": "Professional Writing"
            }
        ]
    
    def _calculateRemainingCourses(self,
                                  majorReqs: List[Dict[str, Any]],
                                  minorReqs: List[Dict[str, Any]],
                                  genEdReqs: List[Dict[str, Any]],
                                  completedCourses: List[str],
                                  apCredits: List[str]) -> List[Dict[str, Any]]:
        """Calculate which courses still need to be taken."""
        completed = set(completedCourses + apCredits)
        
        remaining = []
        
        # Filter major requirements
        for req in majorReqs:
            if req["courseCode"] not in completed:
                remaining.append(req)
        
        # Filter minor requirements
        for req in minorReqs:
            if req["courseCode"] not in completed:
                remaining.append(req)
        
        # Gen ed requirements (simplified)
        remaining.extend(genEdReqs)
        
        return remaining
    
    def _distributeCourses(self,
                          courses: List[Dict[str, Any]],
                          startSemester: str,
                          startYear: int,
                          preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Distribute courses across semesters."""
        semesterPlans = []
        currentSemester = startSemester
        currentYear = startYear
        
        maxCredits = preferences.get("maxCreditsPerSemester", 15)
        minCredits = preferences.get("minCreditsPerSemester", 12)
        
        remainingCourses = courses.copy()
        completedCodes = set()
        
        # Generate 8 semesters (4 years)
        for semesterNum in range(8):
            semesterCourses = []
            semesterCredits = 0
            
            # Select courses for this semester
            availableCourses = self._getAvailableCourses(
                remainingCourses,
                completedCodes
            )
            
            for course in availableCourses:
                courseCredits = course.get("credits", 3)
                
                if semesterCredits + courseCredits <= maxCredits:
                    semesterCourses.append(course["courseCode"])
                    semesterCredits += courseCredits
                    completedCodes.add(course["courseCode"])
                    remainingCourses.remove(course)
                
                if semesterCredits >= minCredits:
                    break
            
            semesterPlans.append({
                "semester": currentSemester,
                "year": currentYear,
                "courses": semesterCourses,
                "totalCredits": semesterCredits
            })
            
            # Move to next semester
            if currentSemester == "Fall":
                currentSemester = "Spring"
                currentYear += 1
            else:
                currentSemester = "Fall"
        
        return semesterPlans
    
    def _getAvailableCourses(self,
                            courses: List[Dict[str, Any]],
                            completedCodes: set) -> List[Dict[str, Any]]:
        """Get courses that have prerequisites satisfied."""
        available = []
        
        for course in courses:
            prerequisites = course.get("prerequisites", [])
            
            if all(prereq in completedCodes for prereq in prerequisites):
                available.append(course)
        
        return available
    
    def _loadCurriculumData(self) -> Dict[str, Any]:
        """Load curriculum data for different majors."""
        # This would typically load from a database or file
        # For now, return sample data for Computer Science
        return {
            "Computer Science": {
                "required": [
                    {"code": "CMSC131", "name": "Object-Oriented Programming I", "credits": 4, "prerequisites": []},
                    {"code": "CMSC132", "name": "Object-Oriented Programming II", "credits": 4, "prerequisites": ["CMSC131"]},
                    {"code": "CMSC216", "name": "Introduction to Computer Systems", "credits": 4, "prerequisites": ["CMSC132"]},
                    {"code": "CMSC250", "name": "Discrete Structures", "credits": 4, "prerequisites": ["CMSC131"]},
                    {"code": "CMSC330", "name": "Programming Languages", "credits": 3, "prerequisites": ["CMSC216", "CMSC250"]},
                    {"code": "CMSC351", "name": "Algorithms", "credits": 3, "prerequisites": ["CMSC250"]},
                    {"code": "CMSC411", "name": "Computer Systems Architecture", "credits": 3, "prerequisites": ["CMSC216"]},
                    {"code": "CMSC420", "name": "Data Structures", "credits": 3, "prerequisites": ["CMSC351"]},
                    {"code": "MATH140", "name": "Calculus I", "credits": 4, "prerequisites": []},
                    {"code": "MATH141", "name": "Calculus II", "credits": 4, "prerequisites": ["MATH140"]},
                    {"code": "STAT400", "name": "Applied Probability and Statistics", "credits": 3, "prerequisites": ["MATH141"]}
                ],
                "electives": 15  # 15 credits of CS electives
            }
        }


fourYearPlanService = FourYearPlanService()

