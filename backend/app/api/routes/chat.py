"""
API routes for chat/conversation functionality.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.ai_assistant_service import aiAssistantService
from app.services.scheduling_engine import schedulingEngine
from app.services.four_year_plan_service import fourYearPlanService
from app.services.umd_schedule_service import umdScheduleService
from typing import List, Dict, Any

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def handleChat(request: ChatRequest):
    """
    Handle chat messages from users.
    
    Args:
        request: Chat request with user message
        
    Returns:
        AI response with suggestions
    """
    try:
        # Extract user intent
        intent = await aiAssistantService.extractUserIntent(request.message)
        
        # Get conversation history (simplified - would fetch from database)
        conversationHistory = []
        
        # Initialize data dict
        responseData = {"intent": intent}
        
        # Handle schedule generation requests
        intentType = intent.get("intent", "general_question")
        
        if intentType == "schedule_generation":
            schedule = await handleScheduleGeneration(intent, request.userId)
            if schedule:
                responseData["schedule"] = schedule
                # Add schedule info to context
                intent["scheduleGenerated"] = True
        
        elif intentType == "four_year_plan":
            plan = await handlePlanGeneration(intent, request.userId)
            if plan:
                responseData["plan"] = plan
                # Add plan info to context
                intent["planGenerated"] = True
        
        # Generate response with schedule/plan context
        response = await aiAssistantService.generateChatResponse(
            userMessage=request.message,
            conversationHistory=conversationHistory,
            contextData={"intent": intent, "generatedData": responseData}
        )
        
        # Generate suggestions based on intent
        suggestions = generateSuggestions(intent)
        
        return ChatResponse(
            conversationId=request.conversationId or 1,
            response=response,
            suggestions=suggestions,
            data=responseData
        )
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


async def handleScheduleGeneration(intent: Dict[str, Any], userId: str) -> Dict[str, Any] | None:
    """Generate schedule based on extracted intent."""
    try:
        # Extract parameters from intent
        semester = intent.get("semester", "Fall")
        year = intent.get("year", 2025)
        requiredCourses = intent.get("courses", [])
        
        if not requiredCourses:
            return None
        
        # Get available sections
        availableSections = {}
        for courseCode in requiredCourses:
            try:
                sections = await umdScheduleService.getSections(
                    courseId=courseCode,
                    semester=f"{year}{getSemesterCode(semester)}"
                )
                parsedSections = [
                    await umdScheduleService.parseSectionData(section)
                    for section in sections
                ]
                availableSections[courseCode] = parsedSections
            except Exception as error:
                print(f"Error fetching sections for {courseCode}: {error}")
                continue
        
        if not availableSections:
            return None
        
        # Generate schedules
        preferences = {
            "timePreference": intent.get("timePreference"),
            "professorPreference": intent.get("professorPreference"),
        }
        
        schedules = await schedulingEngine.generateSchedules(
            requiredCourses=requiredCourses,
            availableSections=availableSections,
            preferences=preferences,
            maxSchedules=3
        )
        
        return {
            "semester": semester,
            "year": year,
            "schedules": schedules[:1] if schedules else []  # Return top schedule
        }
        
    except Exception as error:
        print(f"Error generating schedule: {error}")
        return None


async def handlePlanGeneration(intent: Dict[str, Any], userId: str) -> Dict[str, Any] | None:
    """Generate four-year plan based on extracted intent."""
    try:
        major = intent.get("major")
        if not major:
            return None
        
        plan = await fourYearPlanService.generatePlan(
            major=major,
            minor=intent.get("minor"),
            startSemester=intent.get("startSemester", "Fall"),
            startYear=intent.get("startYear", 2025),
            completedCourses=intent.get("completedCourses", []),
            apCredits=intent.get("apCredits", []),
            preferences={}
        )
        
        return plan
        
    except Exception as error:
        print(f"Error generating plan: {error}")
        return None


def generateSuggestions(intent: Dict[str, Any]) -> List[str]:
    """Generate follow-up suggestions based on intent."""
    intentType = intent.get("intent", "general_question")
    
    suggestions = {
        "schedule_generation": [
            "Show me schedules with morning classes",
            "Find sections with the best professors",
            "What are the easiest courses?"
        ],
        "four_year_plan": [
            "Show me CS electives focused on AI",
            "When should I take CMSC351?",
            "Can I graduate early?"
        ],
        "course_recommendation": [
            "What prerequisites do I need?",
            "Who are the best professors?",
            "How hard is this course?"
        ],
        "general_question": [
            "Help me plan my schedule",
            "Generate a 4-year plan",
            "Recommend courses for next semester"
        ]
    }
    
    return suggestions.get(intentType, suggestions["general_question"])

