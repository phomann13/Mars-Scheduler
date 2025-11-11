/**
 * API service for campus buildings and map data.
 */

import axios from 'axios';
import { Building, WalkingTimeWarning } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const campusApi = {
  /**
   * Get all campus buildings
   */
  async getBuildings(): Promise<Building[]> {
    const response = await axios.get(`${API_BASE_URL}/campus/buildings`);
    return response.data.buildings;
  },

  /**
   * Get details for a specific building
   */
  async getBuildingDetails(buildingCode: string): Promise<Building> {
    const response = await axios.get(`${API_BASE_URL}/campus/buildings/${buildingCode}`);
    return response.data;
  },

  /**
   * Search for a building by name
   */
  async searchBuilding(name: string): Promise<Building> {
    const response = await axios.get(`${API_BASE_URL}/campus/buildings/search/${name}`);
    return response.data;
  },

  /**
   * Get walking time between two buildings
   */
  async getWalkingTime(building1: string, building2: string): Promise<number> {
    const response = await axios.get(`${API_BASE_URL}/campus/walking-time`, {
      params: { building1, building2 }
    });
    return response.data.walkingTimeMinutes;
  },

  /**
   * Validate walking times for a schedule
   */
  async validateScheduleWalkingTimes(
    sections: any[],
    maxWalkingMinutes: number = 10
  ): Promise<{ isValid: boolean; warnings: WalkingTimeWarning[]; maxWalkingTime: number }> {
    const response = await axios.post(`${API_BASE_URL}/campus/validate-schedule-walking-times`, {
      sections,
      maxWalkingMinutes
    });
    return response.data;
  },

  /**
   * Get campus map data for visualization
   */
  async getCampusMapData(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/campus/campus-map`);
    return response.data;
  }
};

