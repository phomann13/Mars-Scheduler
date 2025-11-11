"""
Vector store service using Pinecone for semantic search and RAG.
"""

from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
import json


class VectorStoreService:
    """Service for managing embeddings and semantic search with Pinecone."""
    
    def __init__(self):
        self.openaiClient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embeddingModel = "text-embedding-3-small"
        self.embeddingDimension = 1536
        
        # Initialize Pinecone if credentials are available
        self.pineconeEnabled = False
        self.index = None
        
        if settings.PINECONE_API_KEY:
            try:
                self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                self.indexName = settings.PINECONE_INDEX_NAME
                self._initializeIndex()
                self.pineconeEnabled = True
            except Exception as error:
                print(f"Pinecone initialization failed: {error}")
                print("Vector store features will be disabled")
    
    def _initializeIndex(self):
        """Initialize or connect to Pinecone index."""
        try:
            # Check if index exists
            existingIndexes = self.pc.list_indexes()
            
            if self.indexName not in [idx.name for idx in existingIndexes]:
                # Create new index
                print(f"Creating Pinecone index: {self.indexName}")
                self.pc.create_index(
                    name=self.indexName,
                    dimension=self.embeddingDimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENVIRONMENT or "us-east-1"
                    )
                )
            
            # Connect to index
            self.index = self.pc.Index(self.indexName)
            print(f"Connected to Pinecone index: {self.indexName}")
            
        except Exception as error:
            print(f"Error initializing Pinecone index: {error}")
            raise
    
    async def createEmbedding(self, text: str) -> List[float]:
        """
        Create embedding vector for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = await self.openaiClient.embeddings.create(
                model=self.embeddingModel,
                input=text
            )
            return response.data[0].embedding
        except Exception as error:
            print(f"Error creating embedding: {error}")
            return []
    
    async def generateReviewSummary(self, reviews: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate a concise summary paragraph of all course reviews using OpenAI.
        
        Args:
            reviews: List of review dictionaries with 'review', 'rating', 'professor' fields
            
        Returns:
            Summary paragraph or None if generation fails
        """
        if not reviews or len(reviews) == 0:
            return None
        
        try:
            # Prepare review text
            reviewTexts = []
            for i, review in enumerate(reviews[:20]):  # Limit to 20 reviews to avoid token limits
                if isinstance(review, dict) and review.get("review"):
                    rating = review.get("rating", "N/A")
                    reviewTexts.append(f"[Rating: {rating}/5] {review['review']}")
            
            if not reviewTexts:
                return None
            
            # Generate summary using OpenAI
            prompt = f"""Summarize the following student reviews for this course into a single comprehensive paragraph (150-200 words). 
Include:
- Overall sentiment (positive/negative/mixed)
- Common themes about teaching quality, difficulty, workload
- Specific strengths and weaknesses mentioned
- Notable professor feedback

Reviews:
{chr(10).join(reviewTexts)}

Summary:"""

            response = await self.openaiClient.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap for summarization
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes student course reviews concisely and objectively."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3  # Lower temperature for more consistent summaries
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as error:
            print(f"Error generating review summary: {error}")
            return None
    
    async def indexCourse(self, courseData: Dict[str, Any]) -> bool:
        """
        Index a course with its embedding.
        
        Args:
            courseData: Course information dictionary
            
        Returns:
            Success status
        """
        if not self.pineconeEnabled:
            return False
        
        try:
            # Option to generate AI summary or use raw reviews
            # Set to False to skip AI summarization and index raw reviews instead
            useAISummary = True
            
            if useAISummary and courseData.get("reviews") and len(courseData["reviews"]) > 0:
                print(f"  Generating review summary for {courseData.get('courseCode')}...")
                reviewSummary = await self.generateReviewSummary(courseData["reviews"])
                if reviewSummary:
                    courseData["reviewSummary"] = reviewSummary
            
            # Create text representation of course
            courseText = self._formatCourseForEmbedding(courseData)
            
            # Generate embedding
            embedding = await self.createEmbedding(courseText)
            
            if not embedding:
                return False
            
            # Prepare metadata (filter out None values for Pinecone)
            metadata = {
                "courseCode": courseData.get("courseCode", ""),
                "courseName": courseData.get("courseName", ""),
                "department": courseData.get("department", ""),
                "credits": courseData.get("credits", 0),
                "description": courseData.get("description", "")[:1000],  # Limit size
                "level": courseData.get("level", "")
            }
            
            # Only add optional fields if they exist (not None)
            if courseData.get("avgGPA") is not None:
                metadata["avgGPA"] = float(courseData.get("avgGPA"))
            
            if courseData.get("avgRating") is not None:
                metadata["avgRating"] = float(courseData.get("avgRating"))
            
            # Add professors list if available
            if courseData.get("professors"):
                professors = courseData.get("professors", [])
                if isinstance(professors, list) and professors:
                    # Store as comma-separated string for Pinecone
                    metadata["professors"] = ", ".join(professors[:5])  # Limit to 5 professors
            
            # Add review count if available
            if courseData.get("reviewCount"):
                metadata["reviewCount"] = int(courseData.get("reviewCount"))
            
            # Add prerequisites if available
            if courseData.get("prerequisites"):
                prereqs = courseData.get("prerequisites", [])
                if isinstance(prereqs, list) and prereqs:
                    metadata["prerequisites"] = ", ".join(prereqs[:10])  # Limit to 10
            
            # Add topics if available
            if courseData.get("topics"):
                topics = courseData.get("topics", [])
                if isinstance(topics, list) and topics:
                    metadata["topics"] = ", ".join(topics[:10])  # Limit to 10
            
            # Add review summary if available (AI-generated)
            if courseData.get("reviewSummary"):
                # Truncate to fit metadata limits
                metadata["reviewSummary"] = courseData["reviewSummary"][:500]
            
            # Store full reviews as JSON string (optional, for retrieval)
            if courseData.get("reviews"):
                reviews = courseData["reviews"]
                if isinstance(reviews, list) and reviews:
                    # Store compact version: just rating and short text
                    compactReviews = []
                    for review in reviews[:20]:  # Limit to 20
                        if isinstance(review, dict):
                            compactReviews.append({
                                "rating": review.get("rating"),
                                "text": review.get("review", "")[:150]  # 150 chars per review
                            })
                    
                    import json
                    reviewsJson = json.dumps(compactReviews)
                    # Only store if under 10KB (Pinecone limit consideration)
                    if len(reviewsJson) < 10000:
                        metadata["reviewsData"] = reviewsJson
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": courseData.get("courseCode", ""),
                    "values": embedding,
                    "metadata": metadata
                }]
            )
            
            return True
            
        except Exception as error:
            print(f"Error indexing course: {error}")
            return False
    
    async def indexCourses(self, courses: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Index multiple courses in batch.
        
        Args:
            courses: List of course dictionaries
            
        Returns:
            Statistics on indexing
        """
        if not self.pineconeEnabled:
            return {"success": 0, "failed": 0}
        
        success = 0
        failed = 0
        
        for course in courses:
            result = await self.indexCourse(course)
            if result:
                success += 1
            else:
                failed += 1
        
        return {"success": success, "failed": failed}
    
    async def searchSimilarCourses(self,
                                   query: str,
                                   topK: int = 10,
                                   filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for courses similar to query using semantic search.
        
        Args:
            query: Search query
            topK: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of similar courses with scores
        """
        if not self.pineconeEnabled:
            return []
        
        try:
            # Generate embedding for query
            queryEmbedding = await self.createEmbedding(query)
            
            if not queryEmbedding:
                return []
            
            # Search in Pinecone
            searchResults = self.index.query(
                vector=queryEmbedding,
                top_k=topK,
                include_metadata=True,
                filter=filters
            )
            
            # Format results
            courses = []
            for match in searchResults.matches:
                course = {
                    "courseCode": match.metadata.get("courseCode"),
                    "courseName": match.metadata.get("courseName"),
                    "department": match.metadata.get("department"),
                    "description": match.metadata.get("description"),
                    "credits": match.metadata.get("credits"),
                    "level": match.metadata.get("level"),
                    "similarityScore": match.score
                }
                
                # Add optional fields if they exist
                if match.metadata.get("avgGPA"):
                    course["avgGPA"] = match.metadata.get("avgGPA")
                
                if match.metadata.get("avgRating"):
                    course["avgRating"] = match.metadata.get("avgRating")
                
                if match.metadata.get("professors"):
                    course["professors"] = match.metadata.get("professors")
                
                if match.metadata.get("reviewCount"):
                    course["reviewCount"] = match.metadata.get("reviewCount")
                
                if match.metadata.get("prerequisites"):
                    course["prerequisites"] = match.metadata.get("prerequisites")
                
                if match.metadata.get("topics"):
                    course["topics"] = match.metadata.get("topics")
                
                if match.metadata.get("reviewSummary"):
                    course["reviewSummary"] = match.metadata.get("reviewSummary")
                
                # Include raw reviews if stored
                if match.metadata.get("reviewsData"):
                    import json
                    try:
                        course["reviews"] = json.loads(match.metadata.get("reviewsData"))
                    except:
                        pass
                
                courses.append(course)
            
            return courses
            
        except Exception as error:
            print(f"Error searching courses: {error}")
            return []
    
    async def getCoursesForCareerPath(self,
                                     careerInterest: str,
                                     topK: int = 15) -> List[Dict[str, Any]]:
        """
        Get course recommendations based on career interest.
        
        Args:
            careerInterest: Career path or interest (e.g., "AI research", "software engineering")
            topK: Number of courses to return
            
        Returns:
            List of relevant courses
        """
        query = f"Courses relevant for {careerInterest} career path and professional development"
        return await self.searchSimilarCourses(query, topK=topK)
    
    async def findCourseSimilarTo(self,
                                  courseCode: str,
                                  topK: int = 5) -> List[Dict[str, Any]]:
        """
        Find courses similar to a given course.
        
        Args:
            courseCode: Course code to find similar courses for
            topK: Number of similar courses to return
            
        Returns:
            List of similar courses
        """
        if not self.pineconeEnabled:
            return []
        
        try:
            # Fetch the course's embedding
            result = self.index.fetch(ids=[courseCode])
            
            if not result.vectors or courseCode not in result.vectors:
                return []
            
            vector = result.vectors[courseCode].values
            
            # Search for similar courses
            searchResults = self.index.query(
                vector=vector,
                top_k=topK + 1,  # +1 to exclude the course itself
                include_metadata=True
            )
            
            # Format results (excluding the course itself)
            courses = []
            for match in searchResults.matches:
                if match.metadata.get("courseCode") != courseCode:
                    courses.append({
                        "courseCode": match.metadata.get("courseCode"),
                        "courseName": match.metadata.get("courseName"),
                        "department": match.metadata.get("department"),
                        "description": match.metadata.get("description"),
                        "similarityScore": match.score
                    })
            
            return courses[:topK]
            
        except Exception as error:
            print(f"Error finding similar courses: {error}")
            return []
    
    def _formatCourseForEmbedding(self, courseData: Dict[str, Any]) -> str:
        """
        Format course data into text for embedding.
        
        Args:
            courseData: Course information
            
        Returns:
            Formatted text string
        """
        parts = []
        
        # Course code and name
        if courseData.get("courseCode"):
            parts.append(f"Course: {courseData['courseCode']}")
        
        if courseData.get("courseName"):
            parts.append(f"Title: {courseData['courseName']}")
        
        # Description (prefer PlanetTerp if available and longer)
        description = courseData.get("descriptionPlanetTerp") or courseData.get("description")
        if description:
            parts.append(f"Description: {description}")
        
        # Department and level
        if courseData.get("department"):
            parts.append(f"Department: {courseData['department']}")
        
        if courseData.get("level"):
            parts.append(f"Level: {courseData['level']}")
        
        # Prerequisites
        if courseData.get("prerequisites"):
            prereqs = courseData["prerequisites"]
            if isinstance(prereqs, list):
                prereqs = ", ".join(prereqs)
            parts.append(f"Prerequisites: {prereqs}")
        
        # Topics/Keywords
        if courseData.get("topics"):
            topics = courseData["topics"]
            if isinstance(topics, list):
                topics = ", ".join(topics)
            parts.append(f"Topics: {topics}")
        
        # Professors (for better semantic matching)
        if courseData.get("professors"):
            professors = courseData["professors"]
            if isinstance(professors, list) and professors:
                parts.append(f"Professors: {', '.join(professors[:3])}")
        
        # Average GPA (indicates difficulty)
        if courseData.get("avgGPA"):
            gpa = courseData["avgGPA"]
            difficulty = "Easy" if gpa > 3.5 else "Moderate" if gpa > 3.0 else "Challenging"
            parts.append(f"Difficulty: {difficulty} (GPA: {gpa})")
        
        # Review summary (AI-generated comprehensive summary of all reviews)
        if courseData.get("reviewSummary"):
            parts.append(f"Student Review Summary: {courseData['reviewSummary']}")
        # OR include raw reviews if no summary
        elif courseData.get("reviews"):
            reviews = courseData["reviews"]
            if isinstance(reviews, list) and len(reviews) > 0:
                # Include top 10 reviews for semantic search
                reviewTexts = []
                for review in reviews[:10]:
                    if isinstance(review, dict) and review.get("review"):
                        rating = review.get("rating", "N/A")
                        text = review["review"][:200]  # Limit per review
                        reviewTexts.append(f"[{rating}/5] {text}")
                
                if reviewTexts:
                    parts.append(f"Student Reviews: {' | '.join(reviewTexts)}")
        
        return " | ".join(parts)
    
    def getStats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with stats
        """
        if not self.pineconeEnabled:
            return {
                "enabled": False,
                "message": "Pinecone not configured"
            }
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "enabled": True,
                "totalVectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "indexFullness": stats.index_fullness
            }
        except Exception as error:
            return {
                "enabled": True,
                "error": str(error)
            }


vectorStoreService = VectorStoreService()

