"""
API routes for chat/conversation functionality.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.ai_assistant_service import aiAssistantService
from app.services.scheduling_engine import schedulingEngine
from app.services.four_year_plan_service import fourYearPlanService
from app.services.umd_schedule_service import umdScheduleService
from app.services.venus_schedule_service import venusScheduleService
from typing import List, Dict, Any
import asyncio

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
        # Check for exact "4-year plan" stub trigger
        if "4-year plan" in request.message:
            # Simulate 3 second processing time
            await asyncio.sleep(3)
            
            # Generate the four-year plan without AI query
            plan = await handlePlanGeneration({}, request.userId)
            
            # Return hardcoded response with plan data
            return ChatResponse(
                conversationId=request.conversationId or 1,
                response="I have loaded an example four year plan for you, let me know if you have other questions",
                suggestions=[
                    "Show me CS electives focused on AI",
                    "When should I take CMSC351?",
                    "Can I graduate early?"
                ],
                data={
                    "intent": {"intent": "four_year_plan"},
                    "plan": plan
                }
            )
        
        # Extract user intent
        intent = await aiAssistantService.extractUserIntent(request.message)
        
        # Get conversation history (simplified - would fetch from database)
        conversationHistory = []
        
        # Initialize data dict
        responseData = {"intent": intent}
        print(intent)
        # Handle schedule generation requests
        intentType = intent.get("intent", "general_question")
        
        if intentType == "schedule_generation":
            schedule = await handleScheduleGeneration(intent, request.userId)
            if schedule:
                responseData["schedule"] = schedule
                # Add schedule info to context
                intent["scheduleGenerated"] = True
                intent["usingSampleData"] = schedule.get("usingSampleData", False)
        
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
    """Generate schedule based on extracted intent using Venus API or sample data."""
    try:
        # Extract parameters from intent with proper defaults
        semester = intent.get("semester") or "Spring"
        year = intent.get("year") or 2026
        requiredCourses = intent.get("courses", [])
        
        if not requiredCourses:
            return None
        
        # Get term ID for the semester
        termId = venusScheduleService.getSemesterTermId(semester, year)
        
        print(f"🔍 Attempting to generate schedule for {semester} {year} (termId: {termId})")
        print(f"📚 Courses: {requiredCourses}")
        
        # Try Venus API first
        schedules = await venusScheduleService.generateSchedules(
            termId=termId,
            requiredCourses=requiredCourses,
            minCredits=intent.get("minCredits", 1),
            maxCredits=intent.get("maxCredits", 20)
        )
        
        usingSampleData = False
        
        # If Venus API fails (authentication required), load sample data
        if not schedules:
            print("⚠️  Venus API unavailable (requires UMD authentication)")
            print("📂 Loading sample schedule data as fallback...")
            schedules = loadSampleSchedules()
            usingSampleData = True
        
        if not schedules:
            return None
        
        return {
            "semester": semester,
            "year": year,
            "termId": termId,
            "schedules": schedules[:5],  # Return top 5 schedules
            "usingSampleData": usingSampleData
        }
        
    except Exception as error:
        print(f"❌ Error generating schedule: {error}")
        return None


def loadSampleSchedules() -> List[Dict[str, Any]]:
    """Load sample schedules from JSON file as fallback."""
    try:
        import json
        import os
        from pathlib import Path
        
        # UMD Building locations (lat, lng)
        buildingLocations = {
            "CMSC": [38.9890, -76.9383],  # Iribe Center / AVW
            "MATH": [38.9858, -76.9426],  # Mathematics Building
            "ENGL": [38.9869, -76.9464],  # Tawes Hall
            "COMM": [38.9886, -76.9458],  # Skinner Building
        }
        
        buildingNames = {
            "CMSC": "Iribe Center",
            "MATH": "Mathematics Building",
            "ENGL": "Tawes Hall",
            "COMM": "Skinner Building",
        }
        
        # Get the backend root directory (4 levels up from this file)
        # chat.py -> routes -> api -> app -> backend
        backendRoot = Path(__file__).parent.parent.parent.parent
        samplePath = backendRoot / "data" / "sample_semester_schedule.json"
        
        print(f"🔍 Looking for sample schedules at: {samplePath}")
        print(f"📁 File exists: {samplePath.exists()}")
        
        if samplePath.exists():
            with open(samplePath, 'r') as f:
                schedules = json.load(f)
                print(f"✅ Loaded {len(schedules)} sample schedules")
                
                # Add course metadata and location data to each schedule
                sampleCourses = ["CMSC131", "MATH140", "ENGL101", "COMM107", "CMSC100"]
                for schedule in schedules:
                    schedule["courses"] = sampleCourses
                    schedule["termId"] = "202601"
                    
                    # Add location data to each class
                    for day in schedule.get("scheduleDays", []):
                        for classResult in day.get("classResults", []):
                            coursePrefix = classResult["crs"][:4]  # Get first 4 chars (e.g., "CMSC")
                            
                            if coursePrefix in buildingLocations:
                                classResult["location"] = buildingLocations[coursePrefix]
                                classResult["building"] = buildingNames[coursePrefix]
                
                return schedules
        else:
            print(f"❌ Sample schedule file not found at {samplePath}")
            print(f"📂 Backend root: {backendRoot}")
            print(f"📂 Contents of backend root: {list(backendRoot.iterdir()) if backendRoot.exists() else 'N/A'}")
            return []
            
    except Exception as error:
        print(f"❌ Error loading sample schedules: {error}")
        return []


async def handlePlanGeneration(intent: Dict[str, Any], userId: str) -> Dict[str, Any] | None:
    """Generate four-year plan based on extracted intent."""
    try:
        # Default to Computer Science if no major specified
        major = intent.get("major", "Computer Science")
        
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


def getSemesterCode(semester: str) -> str:
    """Convert semester name to code."""
    mapping = {
        "Spring": "01",
        "Summer": "05",
        "Fall": "08",
        "Winter": "12"
    }
    return mapping.get(semester, "01")

