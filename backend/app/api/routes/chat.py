"""
API routes for chat/conversation functionality.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.ai_assistant_service import aiAssistantService
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
        
        # Generate response
        response = await aiAssistantService.generateChatResponse(
            userMessage=request.message,
            conversationHistory=conversationHistory,
            contextData={"intent": intent}
        )
        
        # Generate suggestions based on intent
        suggestions = generateSuggestions(intent)
        
        return ChatResponse(
            conversationId=request.conversationId or 1,
            response=response,
            suggestions=suggestions,
            data={"intent": intent}
        )
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


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

