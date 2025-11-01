/**
 * API service for communicating with the backend.
 */

import axios from 'axios';
import type { ChatMessage, ChatResponse, Schedule, FourYearPlan } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  sendMessage: async (userId: string, message: string, conversationId?: number): Promise<ChatResponse> => {
    const response = await apiClient.post('/chat/chat', {
      userId,
      message,
      conversationId,
    });
    return response.data;
  },
};

export const scheduleApi = {
  generateSchedules: async (params: {
    userId: string;
    semester: string;
    year: number;
    requiredCourses?: string[];
    preferences?: any;
  }): Promise<Schedule[]> => {
    const response = await apiClient.post('/schedules/generate', params);
    return response.data;
  },
  
  getSchedule: async (scheduleId: number): Promise<Schedule> => {
    const response = await apiClient.get(`/schedules/${scheduleId}`);
    return response.data;
  },
  
  deleteSchedule: async (scheduleId: number): Promise<void> => {
    await apiClient.delete(`/schedules/${scheduleId}`);
  },
};

export const planApi = {
  generatePlan: async (params: {
    userId: string;
    major: string;
    minor?: string;
    startSemester: string;
    startYear: number;
    apCredits?: string[];
    completedCourses?: string[];
    preferences?: any;
  }): Promise<FourYearPlan> => {
    const response = await apiClient.post('/plans/generate', params);
    return response.data;
  },
  
  getPlan: async (planId: number): Promise<FourYearPlan> => {
    const response = await apiClient.get(`/plans/${planId}`);
    return response.data;
  },
  
  getUserPlans: async (userId: string): Promise<FourYearPlan[]> => {
    const response = await apiClient.get(`/plans/user/${userId}`);
    return response.data;
  },
  
  deletePlan: async (planId: number): Promise<void> => {
    await apiClient.delete(`/plans/${planId}`);
  },
};

export const courseApi = {
  searchCourses: async (params?: {
    department?: string;
    semester?: string;
  }): Promise<any> => {
    const response = await apiClient.get('/courses', { params });
    return response.data;
  },
  
  getCourseDetails: async (courseCode: string): Promise<any> => {
    const response = await apiClient.get(`/courses/${courseCode}`);
    return response.data;
  },
  
  getProfessorDetails: async (professorName: string): Promise<any> => {
    const response = await apiClient.get(`/professors/${professorName}`);
    return response.data;
  },
  
  getDepartments: async (): Promise<any> => {
    const response = await apiClient.get('/departments');
    return response.data;
  },
};

