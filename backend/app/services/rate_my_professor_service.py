"""
Service for interacting with RateMyProfessor data.
"""

import httpx
from typing import Optional, Dict, Any
from app.core.config import settings


class RateMyProfessorService:
    """Service for fetching professor ratings from RateMyProfessor."""
    
    def __init__(self):
        self.baseUrl = settings.RATE_MY_PROFESSOR_API_URL
        self.schoolId = "1270"  # University of Maryland College Park
        
    async def searchProfessor(self, professorName: str) -> Optional[Dict[str, Any]]:
        """
        Search for a professor on RateMyProfessor.
        
        Args:
            professorName: Name of the professor
            
        Returns:
            Dictionary containing professor rating data or None
        """
        try:
            # This is a GraphQL query for RateMyProfessor
            query = """
            query TeacherSearchQuery($query: TeacherSearchQuery!) {
              search: newSearch {
                teachers(query: $query) {
                  edges {
                    node {
                      id
                      firstName
                      lastName
                      avgRating
                      avgDifficulty
                      numRatings
                      department
                    }
                  }
                }
              }
            }
            """
            
            variables = {
                "query": {
                    "text": professorName,
                    "schoolID": self.schoolId
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.baseUrl,
                    json={"query": query, "variables": variables},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    edges = data.get("data", {}).get("search", {}).get("teachers", {}).get("edges", [])
                    
                    if edges:
                        # Return the first match
                        professorData = edges[0]["node"]
                        return {
                            "id": professorData.get("id"),
                            "name": f"{professorData.get('firstName')} {professorData.get('lastName')}",
                            "rating": professorData.get("avgRating"),
                            "difficulty": professorData.get("avgDifficulty"),
                            "numReviews": professorData.get("numRatings"),
                            "department": professorData.get("department")
                        }
                    
                return None
                
        except Exception as error:
            print(f"Error fetching RateMyProfessor data: {error}")
            return None
    
    async def getProfessorRating(self, professorId: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed rating for a specific professor.
        
        Args:
            professorId: RateMyProfessor ID
            
        Returns:
            Dictionary containing detailed rating data or None
        """
        try:
            query = """
            query TeacherRatingsPageQuery($id: ID!) {
              node(id: $id) {
                ... on Teacher {
                  id
                  firstName
                  lastName
                  avgRating
                  avgDifficulty
                  numRatings
                  department
                  wouldTakeAgainPercent
                }
              }
            }
            """
            
            variables = {"id": professorId}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.baseUrl,
                    json={"query": query, "variables": variables},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    professorData = data.get("data", {}).get("node", {})
                    
                    if professorData:
                        return {
                            "id": professorData.get("id"),
                            "name": f"{professorData.get('firstName')} {professorData.get('lastName')}",
                            "rating": professorData.get("avgRating"),
                            "difficulty": professorData.get("avgDifficulty"),
                            "numReviews": professorData.get("numRatings"),
                            "department": professorData.get("department"),
                            "wouldTakeAgainPercent": professorData.get("wouldTakeAgainPercent")
                        }
                    
                return None
                
        except Exception as error:
            print(f"Error fetching professor details: {error}")
            return None


rateMyProfessorService = RateMyProfessorService()

