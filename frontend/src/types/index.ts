/**
 * TypeScript type definitions for the UMD Scheduler application.
 */

export interface UserPreferences {
  preferMorning: boolean;
  preferAfternoon: boolean;
  preferEvening: boolean;
  preferredDays?: string[];
  avoidBackToBack: boolean;
  prioritizeProfessorRating: boolean;
  prioritizeEasyGPA: boolean;
  preferredTopics?: string[];
  maxCreditsPerSemester: number;
  minCreditsPerSemester: number;
  validateWalkingTime?: boolean;
  maxWalkingMinutes?: number;
}

export interface User {
  id: number;
  userId: string;
  major?: string;
  minor?: string;
  expectedGraduation?: string;
  apCredits?: string[];
  completedCourses?: string[];
  preferences?: UserPreferences;
}

export interface Course {
  id: number;
  courseCode: string;
  courseName: string;
  department: string;
  credits: number;
  description?: string;
  prerequisites?: string[];
  corequisites?: string[];
  genEds?: string[];
}

export interface Professor {
  id: number;
  name: string;
  department?: string;
  planetTerpRating?: number;
  planetTerpAvgGPA?: number;
  rmpRating?: number;
  rmpDifficulty?: number;
  rmpNumReviews?: number;
  aggregatedScore?: number;
}

export interface Section {
  id: number;
  courseId: number;
  professorId?: number;
  sectionNumber: string;
  semester: string;
  year: number;
  days: string[];
  startTime: string;
  endTime: string;
  building?: string;
  room?: string;
  availableSeats?: number;
  totalSeats?: number;
  course?: Course;
  professor?: Professor;
}

export interface WalkingTimeWarning {
  type: 'insufficient_time' | 'long_walk';
  class1: string;
  class2: string;
  building1: string;
  building2: string;
  timeGap?: number;
  walkingTime: number;
  message: string;
}

export interface Schedule {
  id: number;
  userId: number;
  semester: string;
  year: number;
  sections: Section[];
  score?: number;
  isActive: boolean;
  createdAt: string;
  walkingTimeWarnings?: WalkingTimeWarning[];
}

export interface SemesterPlan {
  semester: string;
  year: number;
  courses: string[];
  totalCredits: number;
}

export interface FourYearPlan {
  id: number;
  userId: number;
  planName: string;
  semesterPlans: SemesterPlan[];
  isActive: boolean;
  createdAt: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  conversationId: number;
  response: string;
  suggestions?: string[];
  data?: any;
}

export interface Building {
  code: string;
  fullName: string;
  latitude: number;
  longitude: number;
  departments?: string[];
}

export interface CourseInsight {
  courseCode: string;
  courseName: string;
  department: string;
  description: string;
  credits?: number;
  avgGPA?: number;
  avgRating?: number;
  similarityScore?: number;
}

