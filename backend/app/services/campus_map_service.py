"""
Service for campus building locations and walking time calculations using OpenStreetMap.
"""

import httpx
from typing import Optional, Dict, Any, List, Tuple
from math import radians, cos, sin, asin, sqrt
from app.core.config import settings


class CampusMapService:
    """Service for UMD campus building data and walking time calculations."""
    
    def __init__(self):
        self.osmApiUrl = "https://nominatim.openstreetmap.org"
        self.overpassApiUrl = "https://overpass-api.de/api/interpreter"
        # Average walking speed in meters per minute
        self.walkingSpeedMpm = 80.0  # ~3 mph
        
    async def getBuildingCoordinates(self, buildingName: str) -> Optional[Dict[str, Any]]:
        """
        Get coordinates for a UMD campus building.
        
        Args:
            buildingName: Name of the building
            
        Returns:
            Dictionary with lat, lon, and display name
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.osmApiUrl}/search",
                    params={
                        "q": f"{buildingName}, University of Maryland, College Park",
                        "format": "json",
                        "limit": 1
                    },
                    headers={"User-Agent": "UMD-Mars-Scheduler/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        result = data[0]
                        return {
                            "buildingName": buildingName,
                            "latitude": float(result["lat"]),
                            "longitude": float(result["lon"]),
                            "displayName": result.get("display_name", buildingName),
                            "osmId": result.get("osm_id")
                        }
                
                return None
                
        except Exception as error:
            print(f"Error fetching building coordinates: {error}")
            return None
    
    async def getCampusBuildings(self) -> List[Dict[str, Any]]:
        """
        Get all major buildings on UMD campus using Overpass API.
        
        Returns:
            List of building dictionaries with coordinates
        """
        try:
            # Overpass QL query for buildings in UMD campus area
            query = """
            [out:json];
            (
              node["building"]["name"](38.98,−76.96,38.99,−76.93);
              way["building"]["name"](38.98,−76.96,38.99,−76.93);
              relation["building"]["name"](38.98,−76.96,38.99,−76.93);
            );
            out center;
            """
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.overpassApiUrl,
                    data={"data": query},
                    headers={"User-Agent": "UMD-Mars-Scheduler/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    buildings = []
                    
                    for element in data.get("elements", []):
                        name = element.get("tags", {}).get("name")
                        if name:
                            lat = element.get("lat") or element.get("center", {}).get("lat")
                            lon = element.get("lon") or element.get("center", {}).get("lon")
                            
                            if lat and lon:
                                buildings.append({
                                    "buildingName": name,
                                    "latitude": float(lat),
                                    "longitude": float(lon),
                                    "osmId": element.get("id")
                                })
                    
                    return buildings
                
                return []
                
        except Exception as error:
            print(f"Error fetching campus buildings: {error}")
            return []
    
    def calculateDistance(self, 
                         lat1: float, lon1: float,
                         lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in meters
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dLat = lat2 - lat1
        dLon = lon2 - lon1
        a = sin(dLat/2)**2 + cos(lat1) * cos(lat2) * sin(dLon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Earth radius in meters
        earthRadius = 6371000
        
        return earthRadius * c
    
    def calculateWalkingTime(self, distanceMeters: float) -> int:
        """
        Calculate walking time in minutes.
        
        Args:
            distanceMeters: Distance in meters
            
        Returns:
            Walking time in minutes (rounded up)
        """
        minutes = distanceMeters / self.walkingSpeedMpm
        return int(minutes) + 1  # Round up
    
    async def getWalkingTimeBetweenBuildings(self,
                                             building1: str,
                                             building2: str) -> Optional[int]:
        """
        Calculate walking time between two buildings.
        
        Args:
            building1: Name of first building
            building2: Name of second building
            
        Returns:
            Walking time in minutes or None
        """
        try:
            coords1 = await self.getBuildingCoordinates(building1)
            coords2 = await self.getBuildingCoordinates(building2)
            
            if not coords1 or not coords2:
                return None
            
            distance = self.calculateDistance(
                coords1["latitude"], coords1["longitude"],
                coords2["latitude"], coords2["longitude"]
            )
            
            return self.calculateWalkingTime(distance)
            
        except Exception as error:
            print(f"Error calculating walking time: {error}")
            return None
    
    async def validateScheduleWalkingTimes(self,
                                          sections: List[Dict[str, Any]],
                                          maxWalkingMinutes: int = 10) -> Dict[str, Any]:
        """
        Validate that walking times between consecutive classes are feasible.
        
        Args:
            sections: List of section dictionaries with building info
            maxWalkingMinutes: Maximum acceptable walking time
            
        Returns:
            Dictionary with validation results and warnings
        """
        warnings = []
        isValid = True
        
        # Sort sections by day and time
        sortedSections = sorted(
            sections,
            key=lambda x: (x.get("days", []), x.get("startTime", ""))
        )
        
        for i in range(len(sortedSections) - 1):
            current = sortedSections[i]
            next_section = sortedSections[i + 1]
            
            # Check if classes are on the same day
            currentDays = set(current.get("days", []))
            nextDays = set(next_section.get("days", []))
            
            if currentDays.intersection(nextDays):
                # Check time gap
                currentEnd = current.get("endTime", "")
                nextStart = next_section.get("startTime", "")
                
                if currentEnd and nextStart:
                    # Calculate time gap in minutes
                    timeGap = self._calculateTimeGap(currentEnd, nextStart)
                    
                    if timeGap > 0 and timeGap < 60:  # Classes within 1 hour
                        # Calculate walking time
                        building1 = current.get("building", "")
                        building2 = next_section.get("building", "")
                        
                        if building1 and building2 and building1 != building2:
                            walkingTime = await self.getWalkingTimeBetweenBuildings(
                                building1, building2
                            )
                            
                            if walkingTime and walkingTime > timeGap:
                                isValid = False
                                warnings.append({
                                    "type": "insufficient_time",
                                    "class1": current.get("courseCode", ""),
                                    "class2": next_section.get("courseCode", ""),
                                    "building1": building1,
                                    "building2": building2,
                                    "timeGap": timeGap,
                                    "walkingTime": walkingTime,
                                    "message": f"Only {timeGap} min between classes, but {walkingTime} min walk"
                                })
                            elif walkingTime and walkingTime > maxWalkingMinutes:
                                warnings.append({
                                    "type": "long_walk",
                                    "class1": current.get("courseCode", ""),
                                    "class2": next_section.get("courseCode", ""),
                                    "building1": building1,
                                    "building2": building2,
                                    "walkingTime": walkingTime,
                                    "message": f"{walkingTime} min walk between classes"
                                })
        
        return {
            "isValid": isValid,
            "warnings": warnings,
            "maxWalkingTime": max([w.get("walkingTime", 0) for w in warnings], default=0)
        }
    
    def _calculateTimeGap(self, endTime: str, startTime: str) -> int:
        """
        Calculate gap between two times in minutes.
        
        Args:
            endTime: End time (HH:MM format)
            startTime: Start time (HH:MM format)
            
        Returns:
            Gap in minutes
        """
        try:
            endParts = endTime.split(":")
            startParts = startTime.split(":")
            
            endMinutes = int(endParts[0]) * 60 + int(endParts[1])
            startMinutes = int(startParts[0]) * 60 + int(startParts[1])
            
            return startMinutes - endMinutes
            
        except Exception:
            return 0


campusMapService = CampusMapService()

