"""
Scheduling engine for generating optimized course schedules.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, time
from itertools import combinations


class SchedulingEngine:
    """Engine for generating and optimizing course schedules."""
    
    def __init__(self):
        self.dayMapping = {
            "M": "Monday",
            "Tu": "Tuesday",
            "W": "Wednesday",
            "Th": "Thursday",
            "F": "Friday"
        }
    
    async def generateSchedules(self,
                               requiredCourses: List[str],
                               availableSections: Dict[str, List[Dict[str, Any]]],
                               preferences: Dict[str, Any],
                               maxSchedules: int = 5) -> List[Dict[str, Any]]:
        """
        Generate multiple schedule options based on requirements and preferences.
        
        Args:
            requiredCourses: List of required course codes
            availableSections: Dictionary mapping course codes to available sections
            preferences: User preferences for scheduling
            maxSchedules: Maximum number of schedules to generate
            
        Returns:
            List of schedule dictionaries with scores
        """
        allSchedules = []
        
        # Get all section combinations
        sectionLists = [availableSections.get(course, []) for course in requiredCourses]
        
        if not all(sectionLists):
            return []
        
        # Generate all possible combinations
        for sectionCombo in self._generateCombinations(sectionLists):
            if self._hasValidTimeConflicts(sectionCombo):
                schedule = {
                    "sections": sectionCombo,
                    "score": self._calculateScheduleScore(sectionCombo, preferences)
                }
                allSchedules.append(schedule)
        
        # Sort by score and return top schedules
        allSchedules.sort(key=lambda x: x["score"], reverse=True)
        return allSchedules[:maxSchedules]
    
    def _generateCombinations(self, sectionLists: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        """
        Generate all valid combinations of sections.
        
        Args:
            sectionLists: List of section lists for each course
            
        Returns:
            List of section combinations
        """
        if not sectionLists:
            return [[]]
        
        if len(sectionLists) == 1:
            return [[section] for section in sectionLists[0]]
        
        combinations = []
        firstSections = sectionLists[0]
        restCombinations = self._generateCombinations(sectionLists[1:])
        
        for section in firstSections:
            for restCombo in restCombinations:
                combinations.append([section] + restCombo)
        
        return combinations
    
    def _hasValidTimeConflicts(self, sections: List[Dict[str, Any]]) -> bool:
        """
        Check if sections have no time conflicts.
        
        Args:
            sections: List of sections to check
            
        Returns:
            True if no conflicts, False otherwise
        """
        for i, section1 in enumerate(sections):
            for section2 in sections[i + 1:]:
                if self._hasTimeConflict(section1, section2):
                    return False
        return True
    
    def _hasTimeConflict(self, section1: Dict[str, Any], section2: Dict[str, Any]) -> bool:
        """
        Check if two sections have overlapping times.
        
        Args:
            section1: First section
            section2: Second section
            
        Returns:
            True if conflict exists, False otherwise
        """
        # Check if any days overlap
        days1 = set(section1.get("days", []))
        days2 = set(section2.get("days", []))
        
        if not days1.intersection(days2):
            return False
        
        # Check time overlap
        start1 = self._parseTime(section1.get("startTime"))
        end1 = self._parseTime(section1.get("endTime"))
        start2 = self._parseTime(section2.get("startTime"))
        end2 = self._parseTime(section2.get("endTime"))
        
        if not all([start1, end1, start2, end2]):
            return False
        
        # Check if times overlap
        return not (end1 <= start2 or end2 <= start1)
    
    def _parseTime(self, timeStr: Optional[str]) -> Optional[time]:
        """
        Parse time string to time object.
        
        Args:
            timeStr: Time string (e.g., "10:00am")
            
        Returns:
            time object or None
        """
        if not timeStr:
            return None
        
        try:
            # Handle various time formats
            timeStr = timeStr.lower().replace(" ", "")
            if "am" in timeStr or "pm" in timeStr:
                return datetime.strptime(timeStr, "%I:%M%p").time()
            else:
                return datetime.strptime(timeStr, "%H:%M").time()
        except Exception:
            return None
    
    def _calculateScheduleScore(self, 
                                sections: List[Dict[str, Any]], 
                                preferences: Dict[str, Any]) -> float:
        """
        Calculate optimization score for a schedule based on preferences.
        
        Args:
            sections: List of sections in schedule
            preferences: User preferences
            
        Returns:
            Score as float (higher is better)
        """
        score = 0.0
        
        # Professor rating score
        if preferences.get("prioritizeProfessorRating", True):
            avgRating = self._calculateAverageProfessorRating(sections)
            score += avgRating * 20  # Weight: 20
        
        # GPA score
        if preferences.get("prioritizeEasyGPA", False):
            avgGPA = self._calculateAverageGPA(sections)
            score += avgGPA * 15  # Weight: 15
        
        # Time preference score
        timeScore = self._calculateTimePreferenceScore(sections, preferences)
        score += timeScore * 25  # Weight: 25
        
        # Day preference score
        dayScore = self._calculateDayPreferenceScore(sections, preferences)
        score += dayScore * 10  # Weight: 10
        
        # Back-to-back penalty
        if preferences.get("avoidBackToBack", False):
            backToBackPenalty = self._calculateBackToBackPenalty(sections)
            score -= backToBackPenalty * 10  # Penalty weight: 10
        
        # Gap optimization (prefer reasonable gaps)
        gapScore = self._calculateGapScore(sections)
        score += gapScore * 5  # Weight: 5
        
        return score
    
    def _calculateAverageProfessorRating(self, sections: List[Dict[str, Any]]) -> float:
        """Calculate average professor rating for sections."""
        ratings = [
            section.get("professor", {}).get("aggregatedScore", 3.0)
            for section in sections
        ]
        return sum(ratings) / len(ratings) if ratings else 3.0
    
    def _calculateAverageGPA(self, sections: List[Dict[str, Any]]) -> float:
        """Calculate average GPA for sections."""
        gpas = [
            section.get("professor", {}).get("planetTerpAvgGPA", 3.0)
            for section in sections
        ]
        return sum(gpas) / len(gpas) if gpas else 3.0
    
    def _calculateTimePreferenceScore(self, 
                                     sections: List[Dict[str, Any]], 
                                     preferences: Dict[str, Any]) -> float:
        """Calculate score based on time preferences."""
        score = 0.0
        preferMorning = preferences.get("preferMorning", False)
        preferAfternoon = preferences.get("preferAfternoon", False)
        preferEvening = preferences.get("preferEvening", False)
        
        for section in sections:
            startTime = self._parseTime(section.get("startTime"))
            if not startTime:
                continue
            
            hour = startTime.hour
            
            if preferMorning and 8 <= hour < 12:
                score += 1.0
            elif preferAfternoon and 12 <= hour < 17:
                score += 1.0
            elif preferEvening and 17 <= hour < 21:
                score += 1.0
        
        return score / len(sections) if sections else 0.0
    
    def _calculateDayPreferenceScore(self,
                                    sections: List[Dict[str, Any]],
                                    preferences: Dict[str, Any]) -> float:
        """Calculate score based on preferred days."""
        preferredDays = preferences.get("preferredDays", [])
        if not preferredDays:
            return 1.0
        
        score = 0.0
        for section in sections:
            sectionDays = set(section.get("days", []))
            preferredSet = set(preferredDays)
            
            if sectionDays.intersection(preferredSet):
                score += 1.0
        
        return score / len(sections) if sections else 0.0
    
    def _calculateBackToBackPenalty(self, sections: List[Dict[str, Any]]) -> float:
        """Calculate penalty for back-to-back classes."""
        penalty = 0.0
        
        # Group sections by day
        daySchedules = {}
        for section in sections:
            for day in section.get("days", []):
                if day not in daySchedules:
                    daySchedules[day] = []
                daySchedules[day].append(section)
        
        # Check for back-to-back classes
        for day, daySections in daySchedules.items():
            sortedSections = sorted(
                daySections,
                key=lambda s: self._parseTime(s.get("startTime")) or time.min
            )
            
            for i in range(len(sortedSections) - 1):
                endTime1 = self._parseTime(sortedSections[i].get("endTime"))
                startTime2 = self._parseTime(sortedSections[i + 1].get("startTime"))
                
                if endTime1 and startTime2:
                    # Calculate time difference in minutes
                    diff = (datetime.combine(datetime.today(), startTime2) - 
                           datetime.combine(datetime.today(), endTime1)).seconds / 60
                    
                    if diff < 15:  # Less than 15 minutes between classes
                        penalty += 1.0
        
        return penalty
    
    def _calculateGapScore(self, sections: List[Dict[str, Any]]) -> float:
        """Calculate score for optimal gaps between classes."""
        score = 0.0
        
        # Group sections by day
        daySchedules = {}
        for section in sections:
            for day in section.get("days", []):
                if day not in daySchedules:
                    daySchedules[day] = []
                daySchedules[day].append(section)
        
        # Calculate gap optimization
        for day, daySections in daySchedules.items():
            sortedSections = sorted(
                daySections,
                key=lambda s: self._parseTime(s.get("startTime")) or time.min
            )
            
            for i in range(len(sortedSections) - 1):
                endTime1 = self._parseTime(sortedSections[i].get("endTime"))
                startTime2 = self._parseTime(sortedSections[i + 1].get("startTime"))
                
                if endTime1 and startTime2:
                    gapMinutes = (datetime.combine(datetime.today(), startTime2) - 
                                 datetime.combine(datetime.today(), endTime1)).seconds / 60
                    
                    # Optimal gap is 30-90 minutes
                    if 30 <= gapMinutes <= 90:
                        score += 1.0
                    elif gapMinutes > 180:  # Large gaps are penalized
                        score -= 0.5
        
        return score


schedulingEngine = SchedulingEngine()

