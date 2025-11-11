"""
API routes for campus map and building data.
"""

from fastapi import APIRouter, HTTPException, Query
from app.services.campus_map_service import campusMapService
from app.data.umd_buildings import getAllBuildings, getBuildingByCode, findBuildingByName
from typing import Optional, List, Dict, Any

router = APIRouter()


@router.get("/buildings")
async def getBuildings():
    """
    Get list of all UMD campus buildings.
    
    Returns:
        List of buildings with coordinates
    """
    try:
        buildings = getAllBuildings()
        return {"buildings": buildings}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/buildings/{buildingCode}")
async def getBuildingDetails(buildingCode: str):
    """
    Get details for a specific building.
    
    Args:
        buildingCode: Building code (e.g., "AVW")
        
    Returns:
        Building details
    """
    try:
        building = getBuildingByCode(buildingCode)
        
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        
        return building
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/buildings/search/{name}")
async def searchBuilding(name: str):
    """
    Search for a building by name.
    
    Args:
        name: Building name or partial name
        
    Returns:
        Building information
    """
    try:
        building = findBuildingByName(name)
        
        if not building:
            # Try OpenStreetMap if not in cache
            osmResult = await campusMapService.getBuildingCoordinates(name)
            if osmResult:
                return osmResult
            
            raise HTTPException(status_code=404, detail="Building not found")
        
        return building
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/walking-time")
async def getWalkingTime(
    building1: str = Query(..., description="First building code or name"),
    building2: str = Query(..., description="Second building code or name")
):
    """
    Calculate walking time between two buildings.
    
    Args:
        building1: First building
        building2: Second building
        
    Returns:
        Walking time in minutes
    """
    try:
        walkingTime = await campusMapService.getWalkingTimeBetweenBuildings(
            building1, building2
        )
        
        if walkingTime is None:
            raise HTTPException(
                status_code=404,
                detail="Could not calculate walking time. Check building names."
            )
        
        return {
            "building1": building1,
            "building2": building2,
            "walkingTimeMinutes": walkingTime
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/validate-schedule-walking-times")
async def validateScheduleWalkingTimes(request: Dict[str, Any]):
    """
    Validate walking times for a schedule.
    
    Args:
        request: Dictionary with 'sections' and optional 'maxWalkingMinutes'
        
    Returns:
        Validation results with warnings
    """
    try:
        sections = request.get("sections", [])
        maxWalkingMinutes = request.get("maxWalkingMinutes", 10)
        
        result = await campusMapService.validateScheduleWalkingTimes(
            sections, maxWalkingMinutes
        )
        
        return result
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/campus-map")
async def getCampusMapData():
    """
    Get campus map data for visualization.
    
    Returns:
        Campus boundaries and major landmarks
    """
    try:
        # UMD campus approximate boundaries
        campusData = {
            "center": {
                "latitude": 38.9869,
                "longitude": -76.9426
            },
            "bounds": {
                "north": 38.9920,
                "south": 38.9820,
                "east": -76.9350,
                "west": -76.9500
            },
            "zoom": 15,
            "buildings": getAllBuildings()
        }
        
        return campusData
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

