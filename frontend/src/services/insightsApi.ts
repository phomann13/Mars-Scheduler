/**
 * API service for course insights and RAG-based recommendations.
 */

import axios from 'axios';
import { CourseInsight } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const insightsApi = {
  /**
   * Get course recommendations for a career path
   */
  async getCoursesForCareer(career: string, limit: number = 15): Promise<CourseInsight[]> {
    const response = await axios.get(`${API_BASE_URL}/insights/career-courses`, {
      params: { career, limit }
    });
    return response.data.courses;
  },

  /**
   * Find courses similar to a given course
   */
  async getSimilarCourses(courseCode: string, limit: number = 5): Promise<CourseInsight[]> {
    const response = await axios.get(`${API_BASE_URL}/insights/similar-courses/${courseCode}`, {
      params: { limit }
    });
    return response.data.similarCourses;
  },

  /**
   * Semantic search for courses
   */
  async searchCourses(
    query: string,
    filters?: any,
    limit: number = 10
  ): Promise<CourseInsight[]> {
    const response = await axios.post(`${API_BASE_URL}/insights/search-courses`, {
      query,
      filters,
      limit
    });
    return response.data.courses;
  },

  /**
   * Get personalized recommendations based on interests
   */
  async getRecommendations(
    interest: string,
    department?: string,
    level?: string
  ): Promise<CourseInsight[]> {
    const response = await axios.get(`${API_BASE_URL}/insights/recommendations`, {
      params: { interest, department, level }
    });
    return response.data.recommendations;
  },

  /**
   * Index a course into the vector store
   */
  async indexCourse(courseData: any): Promise<{ success: boolean; message: string }> {
    const response = await axios.post(`${API_BASE_URL}/insights/index-course`, courseData);
    return response.data;
  },

  /**
   * Index multiple courses
   */
  async indexCourses(courses: any[]): Promise<{ success: number; failed: number }> {
    const response = await axios.post(`${API_BASE_URL}/insights/index-courses`, { courses });
    return response.data;
  },

  /**
   * Get vector store statistics
   */
  async getVectorStoreStats(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/insights/vector-store/stats`);
    return response.data;
  }
};

