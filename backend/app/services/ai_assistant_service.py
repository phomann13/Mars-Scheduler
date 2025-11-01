"""
AI Assistant service using OpenAI and RAG for course recommendations.
"""

from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from app.core.config import settings


class AIAssistantService:
    """Service for AI-powered scheduling assistance with RAG."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.systemPrompt = """You are an intelligent academic scheduling assistant for University of Maryland students. 
You help students plan their academic careers by:
1. Understanding their major requirements and goals
2. Recommending courses based on prerequisites, professor ratings, and preferences
3. Creating optimized semester schedules
4. Generating four-year academic plans
5. Providing insights on course difficulty, workload, and professor quality

Always be helpful, accurate, and considerate of the student's preferences and constraints.
Use the provided data to make informed recommendations."""
    
    async def generateChatResponse(self, 
                                   userMessage: str,
                                   conversationHistory: List[Dict[str, str]],
                                   contextData: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate AI response to user message with context.
        
        Args:
            userMessage: User's message
            conversationHistory: Previous conversation messages
            contextData: Additional context (course data, schedules, etc.)
            
        Returns:
            AI-generated response
        """
        try:
            messages = [{"role": "system", "content": self.systemPrompt}]
            
            # Add conversation history
            messages.extend(conversationHistory)
            
            # Add context data if provided
            if contextData:
                contextMessage = self._formatContextData(contextData)
                messages.append({
                    "role": "system",
                    "content": f"Relevant data: {contextMessage}"
                })
            
            # Add current user message
            messages.append({"role": "user", "content": userMessage})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as error:
            print(f"Error generating AI response: {error}")
            return "I apologize, but I encountered an error. Please try again."
    
    async def extractUserIntent(self, userMessage: str) -> Dict[str, Any]:
        """
        Extract user intent and parameters from message.
        
        Args:
            userMessage: User's message
            
        Returns:
            Dictionary with intent and extracted parameters
        """
        try:
            prompt = f"""Analyze this student's request and extract:
1. Intent (schedule_generation, four_year_plan, course_recommendation, general_question)
2. Major (if mentioned)
3. Semester preferences (if mentioned)
4. Time preferences (morning/afternoon/evening)
5. Professor preferences (easy/good ratings/specific names)
6. Course preferences (specific courses or topics)

Student message: "{userMessage}"

Respond in JSON format."""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a parameter extraction assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse JSON response
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as error:
            print(f"Error extracting intent: {error}")
            return {"intent": "general_question"}
    
    async def generateScheduleRecommendation(self, 
                                            courses: List[Dict[str, Any]],
                                            preferences: Dict[str, Any],
                                            constraints: Dict[str, Any]) -> str:
        """
        Generate natural language recommendation for a schedule.
        
        Args:
            courses: List of recommended courses
            preferences: User preferences
            constraints: Schedule constraints
            
        Returns:
            Natural language recommendation
        """
        try:
            courseList = "\n".join([
                f"- {course.get('courseCode')}: {course.get('courseName')} "
                f"with {course.get('professor')} ({course.get('rating', 'N/A')} rating)"
                for course in courses
            ])
            
            prompt = f"""Based on these courses and student preferences, generate a helpful recommendation:

Courses:
{courseList}

Preferences: {preferences}
Constraints: {constraints}

Provide a brief, friendly explanation of why this schedule works well."""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.systemPrompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as error:
            print(f"Error generating schedule recommendation: {error}")
            return "Here's a schedule that matches your preferences."
    
    def _formatContextData(self, contextData: Dict[str, Any]) -> str:
        """
        Format context data for inclusion in prompt.
        
        Args:
            contextData: Dictionary of context information
            
        Returns:
            Formatted string
        """
        formatted = []
        
        if "courses" in contextData:
            formatted.append(f"Available courses: {len(contextData['courses'])}")
        
        if "professors" in contextData:
            formatted.append(f"Professor data available: {len(contextData['professors'])}")
        
        if "userProfile" in contextData:
            profile = contextData["userProfile"]
            formatted.append(f"Major: {profile.get('major', 'Unknown')}")
            formatted.append(f"Completed courses: {len(profile.get('completedCourses', []))}")
        
        return "; ".join(formatted)


aiAssistantService = AIAssistantService()

