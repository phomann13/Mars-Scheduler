"""
AI Assistant service using OpenAI and RAG for course recommendations.
"""

from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.services.vector_store_service import vectorStoreService


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
        Generate AI response to user message with RAG context.
        
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
            
            # Use RAG to retrieve relevant course information
            if vectorStoreService.pineconeEnabled:
                relevantCourses = await vectorStoreService.searchSimilarCourses(
                    query=userMessage,
                    topK=5
                )
                
                if relevantCourses:
                    ragContext = self._formatRAGContext(relevantCourses)
                    messages.append({
                        "role": "system",
                        "content": f"Relevant courses from knowledge base:\n{ragContext}"
                    })
            
            # Add context data if provided
            if contextData:
                contextMessage = self._formatContextData(contextData)
                messages.append({
                    "role": "system",
                    "content": f"Additional context: {contextMessage}"
                })
                
                # Add special instructions if schedule/plan was generated
                intent = contextData.get("intent", {})
                if intent.get("scheduleGenerated"):
                    messages.append({
                        "role": "system",
                        "content": "A schedule has been successfully generated and will be displayed to the user. Let them know the schedule is ready to view in the Schedule tab."
                    })
                elif intent.get("planGenerated"):
                    messages.append({
                        "role": "system",
                        "content": "A four-year plan has been successfully generated and will be displayed to the user. Let them know the plan is ready to view in the 4-Year Plan tab."
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
            prompt = f"""Analyze this student's request and extract structured information.

Student message: "{userMessage}"

Extract the following and respond in valid JSON format:
{{
  "intent": "schedule_generation" | "four_year_plan" | "course_recommendation" | "general_question",
  "courses": ["CMSC131", "MATH140"],  // Array of course codes if mentioned (e.g., CMSC131, ENGL101)
  "major": "Computer Science",  // Full major name if mentioned
  "minor": "Data Science",  // Minor if mentioned
  "semester": "Fall" | "Spring" | "Summer",  // Current or target semester
  "year": 2025,  // Current or target year
  "startSemester": "Fall",  // For four-year plans
  "startYear": 2025,  // For four-year plans
  "timePreference": "morning" | "afternoon" | "evening" | null,
  "professorPreference": "easy" | "highly_rated" | null,
  "completedCourses": [],  // Courses already taken
  "apCredits": []  // AP credits if mentioned
}}

IMPORTANT:
- Use exact intent categories: "schedule_generation", "four_year_plan", "course_recommendation", or "general_question"
- Extract course codes in standard format (e.g., "CMSC131", "MATH140")
- If the user asks to "generate schedule", "create schedule", "build schedule", use "schedule_generation"
- If the user asks for "4-year plan", "four year plan", "degree plan", use "four_year_plan"
- Include null for missing optional fields
- Only include fields that are relevant to the request"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a parameter extraction assistant. Always respond with valid JSON. Extract information accurately from the user's message."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            import json
            intentData = json.loads(response.choices[0].message.content)
            
            # Normalize course codes if present
            if "courses" in intentData and intentData["courses"]:
                intentData["courses"] = [
                    course.upper().replace(" ", "")
                    for course in intentData["courses"]
                ]
            
            return intentData
            
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
    
    def _formatRAGContext(self, courses: List[Dict[str, Any]]) -> str:
        """
        Format RAG retrieved courses for prompt context.
        
        Args:
            courses: List of course dictionaries from vector search
            
        Returns:
            Formatted string
        """
        formatted = []
        
        for course in courses[:5]:  # Limit to top 5
            courseInfo = [
                f"{course.get('courseCode')} - {course.get('courseName')}",
                f"Department: {course.get('department')}",
                f"Description: {course.get('description', 'N/A')[:150]}...",
            ]
            
            if course.get('avgGPA'):
                courseInfo.append(f"Avg GPA: {course['avgGPA']:.2f}")
            
            if course.get('professors'):
                courseInfo.append(f"Professors: {course['professors']}")
            
            # Include AI-generated review summary for rich context
            if course.get('reviewSummary'):
                courseInfo.append(f"Student Reviews: {course['reviewSummary']}")
            elif course.get('reviewCount'):
                courseInfo.append(f"Reviews: {course['reviewCount']} student reviews available")
            
            if course.get('similarityScore'):
                courseInfo.append(f"Relevance: {course['similarityScore']:.2%}")
            
            formatted.append("\n".join(courseInfo))
        
        return "\n\n".join(formatted)


aiAssistantService = AIAssistantService()

