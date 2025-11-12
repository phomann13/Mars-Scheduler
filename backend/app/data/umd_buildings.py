"""
Static data for common UMD campus buildings with coordinates.
Pre-cached to reduce API calls to OpenStreetMap.
"""

from typing import Dict, Any, List, Optional

# Common UMD campus buildings with coordinates
UMD_BUILDINGS: Dict[str, Dict[str, Any]] = {
    # Computer Science & Engineering
    "AVW": {
        "fullName": "A.V. Williams Building",
        "latitude": 38.9887,
        "longitude": -76.9364,
        "departments": ["Computer Science"]
    },
    "IRB": {
        "fullName": "Iribe Center",
        "latitude": 38.9890,
        "longitude": -76.9368,
        "departments": ["Computer Science"]
    },
    "CSI": {
        "fullName": "Computer Science Instructional Center",
        "latitude": 38.9889,
        "longitude": -76.9372,
        "departments": ["Computer Science"]
    },
    
    # Engineering Buildings
    "JMP": {
        "fullName": "Jeong H. Kim Engineering Building",
        "latitude": 38.9883,
        "longitude": -76.9368,
        "departments": ["Engineering"]
    },
    "EGR": {
        "fullName": "Engineering Classroom Building",
        "latitude": 38.9892,
        "longitude": -76.9394,
        "departments": ["Engineering"]
    },
    "CHE": {
        "fullName": "Chemical Engineering Building",
        "latitude": 38.9902,
        "longitude": -76.9385,
        "departments": ["Engineering"]
    },
    
    # Mathematics & Sciences
    "MTH": {
        "fullName": "Mathematics Building (Kirwin Hall)",
        "latitude": 38.988329,
        "longitude": -76.939208,
        "departments": ["Mathematics"]
    },
    "PHY": {
        "fullName": "Physics Building",
        "latitude": 38.9889,
        "longitude": -76.9428,
        "departments": ["Physics"]
    },
    "PSC": {
        "fullName": "Physical Sciences Complex",
        "latitude": 38.9893,
        "longitude": -76.9419,
        "departments": ["Physics", "Chemistry"]
    },
    "CHM": {
        "fullName": "Chemistry Building",
        "latitude": 38.9872,
        "longitude": -76.9430,
        "departments": ["Chemistry"]
    },
    
    # Life Sciences
    "BIO": {
        "fullName": "Biology-Psychology Building",
        "latitude": 38.9864,
        "longitude": -76.9458,
        "departments": ["Biology", "Psychology"]
    },
    "MMH": {
        "fullName": "Marie Mount Hall",
        "latitude": 38.9907,
        "longitude": -76.9458,
        "departments": ["Biology"]
    },
    
    # Liberal Arts
    "TYD": {
        "fullName": "Tydings Hall",
        "latitude": 38.9876,
        "longitude": -76.9448,
        "departments": ["Government", "Politics"]
    },
    "SKN": {
        "fullName": "Skinner Building",
        "latitude": 38.9858,
        "longitude": -76.9447,
        "departments": ["Arts", "Languages"]
    },
    "JMZ": {
        "fullName": "Jimenez Hall",
        "latitude": 38.9871,
        "longitude": -76.9434,
        "departments": ["Spanish", "Portuguese"]
    },
    
    # Business
    "VMH": {
        "fullName": "Van Munching Hall",
        "latitude": 38.9852,
        "longitude": -76.9461,
        "departments": ["Business"]
    },
    
    # Behavioral & Social Sciences
    "LFR": {
        "fullName": "Le Frak Hall",
        "latitude": 38.9853,
        "longitude": -76.9436,
        "departments": ["Behavioral Sciences"]
    },
    
    # McKeldin Library & Student Services
    "MCK": {
        "fullName": "McKeldin Library",
        "latitude": 38.9859,
        "longitude": -76.9452,
        "departments": ["Library"]
    },
    "SQH": {
        "fullName": "Susquehanna Hall",
        "latitude": 38.9878,
        "longitude": -76.9413,
        "departments": ["Student Services"]
    },
    "STM": {
        "fullName": "Stamp Student Union",
        "latitude": 38.9881,
        "longitude": -76.9445,
        "departments": ["Student Union"]
    },
    
    # Performing Arts
    "CLA": {
        "fullName": "Clarice Smith Performing Arts Center",
        "latitude": 38.9880,
        "longitude": -76.9390,
        "departments": ["Music", "Theater", "Dance"]
    },
    
    # Additional Academic Buildings
    "HJP": {
        "fullName": "Hornbake Library South Wing",
        "latitude": 38.9869,
        "longitude": -76.9464,
        "departments": ["Library", "Archives"]
    },
    "SYM": {
        "fullName": "Symons Hall",
        "latitude": 38.9903,
        "longitude": -76.9411,
        "departments": ["Honors"]
    },
    "ESJ": {
        "fullName": "Edward St. John Learning & Teaching Center",
        "latitude": 38.9889,
        "longitude": -76.9444,
        "departments": ["General Classrooms"]
    },
}


def getBuildingByCode(buildingCode: str) -> Optional[Dict[str, Any]]:
    """
    Get building information by code.
    
    Args:
        buildingCode: Building abbreviation (e.g., "AVW")
        
    Returns:
        Building information dictionary
    """
    building = UMD_BUILDINGS.get(buildingCode.upper())
    if building:
        return {
            "code": buildingCode.upper(),
            **building
        }
    return None


def getAllBuildings() -> List[Dict[str, Any]]:
    """
    Get all buildings as a list.
    
    Returns:
        List of building dictionaries
    """
    return [
        {"code": code, **info}
        for code, info in UMD_BUILDINGS.items()
    ]


def findBuildingByName(name: str) -> Optional[Dict[str, Any]]:
    """
    Find building by full or partial name.
    
    Args:
        name: Full or partial building name
        
    Returns:
        Building information or None
    """
    nameLower = name.lower()
    
    for code, info in UMD_BUILDINGS.items():
        if (nameLower in info["fullName"].lower() or 
            nameLower == code.lower()):
            return {"code": code, **info}
    
    return None

