"""
Database models for the UMD AI Scheduling Assistant.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for storing student information."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String, unique=True, index=True)
    major = Column(String, nullable=True)
    minor = Column(String, nullable=True)
    expectedGraduation = Column(String, nullable=True)
    apCredits = Column(JSON, nullable=True)  # List of AP credits
    completedCourses = Column(JSON, nullable=True)  # List of completed course codes
    preferences = Column(JSON, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    schedules = relationship("Schedule", back_populates="user")
    plans = relationship("FourYearPlan", back_populates="user")


class Course(Base):
    """Course model for storing UMD course information."""
    
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    courseCode = Column(String, unique=True, index=True)
    courseName = Column(String)
    department = Column(String)
    credits = Column(Integer)
    description = Column(Text, nullable=True)
    prerequisites = Column(JSON, nullable=True)  # List of prerequisite course codes
    corequisites = Column(JSON, nullable=True)
    genEds = Column(JSON, nullable=True)  # General education categories
    
    sections = relationship("Section", back_populates="course")


class Professor(Base):
    """Professor model with aggregated rating data."""
    
    __tablename__ = "professors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    department = Column(String, nullable=True)
    planetTerpRating = Column(Float, nullable=True)
    planetTerpAvgGPA = Column(Float, nullable=True)
    rmpRating = Column(Float, nullable=True)
    rmpDifficulty = Column(Float, nullable=True)
    rmpNumReviews = Column(Integer, nullable=True)
    aggregatedScore = Column(Float, nullable=True)  # Combined score
    
    sections = relationship("Section", back_populates="professor")


class Section(Base):
    """Course section model with scheduling information."""
    
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    courseId = Column(Integer, ForeignKey("courses.id"))
    professorId = Column(Integer, ForeignKey("professors.id"), nullable=True)
    sectionNumber = Column(String)
    semester = Column(String)  # e.g., "Fall 2025"
    year = Column(Integer)
    days = Column(JSON)  # List of days (e.g., ["Monday", "Wednesday", "Friday"])
    startTime = Column(String)
    endTime = Column(String)
    building = Column(String, nullable=True)
    room = Column(String, nullable=True)
    availableSeats = Column(Integer, nullable=True)
    totalSeats = Column(Integer, nullable=True)
    
    course = relationship("Course", back_populates="sections")
    professor = relationship("Professor", back_populates="sections")


class Schedule(Base):
    """Generated schedule model."""
    
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id"))
    semester = Column(String)
    year = Column(Integer)
    sections = Column(JSON)  # List of section IDs
    score = Column(Float, nullable=True)  # Optimization score
    isActive = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="schedules")


class FourYearPlan(Base):
    """Four-year academic plan model."""
    
    __tablename__ = "four_year_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id"))
    planName = Column(String)
    semesterPlans = Column(JSON)  # List of semester plans with courses
    isActive = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="plans")


class Conversation(Base):
    """Chat conversation history model."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String, index=True)
    messages = Column(JSON)  # List of message objects
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

