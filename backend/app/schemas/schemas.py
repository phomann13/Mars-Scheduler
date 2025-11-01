"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserPreferences(BaseModel):
    """User preferences for scheduling."""
    preferMorning: bool = False
    preferAfternoon: bool = False
    preferEvening: bool = False
    preferredDays: Optional[List[str]] = None
    avoidBackToBack: bool = False
    prioritizeProfessorRating: bool = True
    prioritizeEasyGPA: bool = False
    preferredTopics: Optional[List[str]] = None
    maxCreditsPerSemester: int = 18
    minCreditsPerSemester: int = 12


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    userId: str
    major: Optional[str] = None
    minor: Optional[str] = None
    expectedGraduation: Optional[str] = None
    apCredits: Optional[List[str]] = None
    completedCourses: Optional[List[str]] = None
    preferences: Optional[UserPreferences] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    userId: str
    major: Optional[str]
    minor: Optional[str]
    expectedGraduation: Optional[str]
    apCredits: Optional[List[str]]
    completedCourses: Optional[List[str]]
    preferences: Optional[Dict[str, Any]]
    createdAt: datetime
    
    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    """Base course schema."""
    courseCode: str
    courseName: str
    department: str
    credits: int
    description: Optional[str] = None
    prerequisites: Optional[List[str]] = None
    corequisites: Optional[List[str]] = None
    genEds: Optional[List[str]] = None


class CourseResponse(CourseBase):
    """Course response schema."""
    id: int
    
    class Config:
        from_attributes = True


class ProfessorBase(BaseModel):
    """Base professor schema."""
    name: str
    department: Optional[str] = None
    planetTerpRating: Optional[float] = None
    planetTerpAvgGPA: Optional[float] = None
    rmpRating: Optional[float] = None
    rmpDifficulty: Optional[float] = None
    rmpNumReviews: Optional[int] = None
    aggregatedScore: Optional[float] = None


class ProfessorResponse(ProfessorBase):
    """Professor response schema."""
    id: int
    
    class Config:
        from_attributes = True


class SectionBase(BaseModel):
    """Base section schema."""
    sectionNumber: str
    semester: str
    year: int
    days: List[str]
    startTime: str
    endTime: str
    building: Optional[str] = None
    room: Optional[str] = None
    availableSeats: Optional[int] = None
    totalSeats: Optional[int] = None


class SectionResponse(SectionBase):
    """Section response schema."""
    id: int
    courseId: int
    professorId: Optional[int]
    
    class Config:
        from_attributes = True


class ScheduleRequest(BaseModel):
    """Request schema for schedule generation."""
    userId: str
    semester: str
    year: int
    requiredCourses: Optional[List[str]] = None
    preferences: Optional[UserPreferences] = None


class ScheduleResponse(BaseModel):
    """Response schema for generated schedules."""
    id: int
    userId: int
    semester: str
    year: int
    sections: List[int]
    score: Optional[float]
    isActive: bool
    createdAt: datetime
    
    class Config:
        from_attributes = True


class FourYearPlanRequest(BaseModel):
    """Request schema for four-year plan generation."""
    userId: str
    major: str
    minor: Optional[str] = None
    startSemester: str
    startYear: int
    apCredits: Optional[List[str]] = None
    completedCourses: Optional[List[str]] = None
    preferences: Optional[UserPreferences] = None


class SemesterPlan(BaseModel):
    """Schema for a single semester plan."""
    semester: str
    year: int
    courses: List[str]
    totalCredits: int


class FourYearPlanResponse(BaseModel):
    """Response schema for four-year plan."""
    id: int
    userId: int
    planName: str
    semesterPlans: List[Dict[str, Any]]
    isActive: bool
    createdAt: datetime
    
    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """Schema for chat messages."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request schema for chat interaction."""
    userId: str
    message: str
    conversationId: Optional[int] = None


class ChatResponse(BaseModel):
    """Response schema for chat interaction."""
    conversationId: int
    response: str
    suggestions: Optional[List[str]] = None
    data: Optional[Dict[str, Any]] = None  # Additional data like schedules, plans

