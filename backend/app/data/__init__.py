"""
Data package for static campus and course information.
"""

from app.data.umd_buildings import (
    UMD_BUILDINGS,
    getBuildingByCode,
    getAllBuildings,
    findBuildingByName
)

__all__ = [
    'UMD_BUILDINGS',
    'getBuildingByCode',
    'getAllBuildings',
    'findBuildingByName'
]

