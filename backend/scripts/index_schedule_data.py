#!/usr/bin/env python3
"""
Index UMD Schedule Data into Pinecone
======================================

Indexes scraped schedule data with sections for AI-powered schedule generation.

Usage:
    python scripts/index_schedule_data.py backend/data/current_schedule.json
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store_service import vectorStoreService


class ScheduleDataIndexer:
    """Indexes schedule data with sections into vector store."""
    
    def __init__(self):
        self.coursesIndexed = 0
        self.sectionsIndexed = 0
        self.errors = 0
    
    async def indexScheduleData(self, courses: List[Dict[str, Any]]):
        """
        Index schedule data into Pinecone.
        
        Args:
            courses: List of course dictionaries with section information
        """
        if not vectorStoreService.pineconeEnabled:
            print("❌ Pinecone is not enabled. Set PINECONE_API_KEY in .env")
            return
        
        print("\n" + "="*60)
        print("   Indexing Schedule Data into Pinecone")
        print("="*60 + "\n")
        
        # Index courses with their sections
        for course in courses:
            try:
                await self._indexCourse(course)
                self.coursesIndexed += 1
                
                # Show progress every 10 courses
                if self.coursesIndexed % 10 == 0:
                    print(f"   Indexed {self.coursesIndexed}/{len(courses)} courses...")
                
            except Exception as error:
                print(f"   ❌ Error indexing {course.get('courseCode')}: {error}")
                self.errors += 1
        
        print("\n" + "="*60)
        print("Indexing Complete!")
        print("="*60)
        print(f"✓ Courses indexed: {self.coursesIndexed}")
        print(f"✓ Sections indexed: {self.sectionsIndexed}")
        if self.errors > 0:
            print(f"⚠️  Errors: {self.errors}")
        print("="*60 + "\n")
    
    async def _indexCourse(self, course: Dict[str, Any]):
        """Index a single course with all its sections."""
        courseCode = course.get('courseCode', 'UNKNOWN')
        courseName = course.get('courseName', '')
        description = course.get('description', '')
        sections = course.get('sections', [])
        
        # Create rich text representation for embedding
        # This allows the AI to find relevant courses and sections
        
        # 1. Index the course itself
        courseText = self._createCourseText(course)
        
        await vectorStoreService.indexCourse({
            "courseCode": courseCode,
            "courseName": courseName,
            "description": description,
            "department": course.get('department', ''),
            "credits": course.get('credits', 3),
            "semester": course.get('semester', ''),
            "totalSections": len(sections),
            "text": courseText,
            "restrictions": course.get('restrictions', ''),
            "crossListedWith": course.get('crossListedWith', []),
            "metadata": {
                "type": "course_with_sections",
                "semester": course.get('semester', ''),
                "hasMultipleSections": len(sections) > 1
            }
        })
        
        # 2. Index each section separately for detailed queries
        for section in sections:
            try:
                await self._indexSection(section, course)
                self.sectionsIndexed += 1
            except Exception as error:
                print(f"      ⚠️  Error indexing section {section.get('sectionId')}: {error}")
    
    async def _indexSection(self, section: Dict[str, Any], course: Dict[str, Any]):
        """Index a single course section."""
        courseCode = course.get('courseCode', 'UNKNOWN')
        sectionId = section.get('sectionId', '0000')
        semester = course.get('semester', '')
        
        # Create rich text for section
        sectionText = self._createSectionText(section, course)
        
        # Format section as a course document for indexing
        # This allows us to use the existing indexCourse method
        sectionCourseData = {
            "courseCode": f"{courseCode}-{sectionId}",
            "courseName": f"{course.get('courseName', 'Unknown')} - Section {sectionId}",
            "department": course.get('department', ''),
            "credits": course.get('credits', 3),
            "description": sectionText,  # Rich text with all section details
            "text": sectionText,
            "level": courseCode[4:7] if len(courseCode) > 4 else "100",
            # Section-specific metadata
            "sectionId": sectionId,
            "instructor": section.get('instructor', 'TBA'),
            "semester": semester,
            "deliveryMode": section.get('deliveryMode', 'face-to-face'),
            "totalSeats": section.get('totalSeats', 0),
            "openSeats": section.get('openSeats', 0),
            "waitlist": section.get('waitlist', 0),
            "hasOpenSeats": section.get('openSeats', 0) > 0,
            "metadata": {
                "type": "course_section",
                "courseCode": courseCode,
                "sectionId": sectionId,
                "semester": semester
            }
        }
        
        # Add meeting times info
        meetingTimes = section.get('meetingTimes', [])
        if meetingTimes:
            firstMeeting = meetingTimes[0]
            sectionCourseData.update({
                "days": firstMeeting.get('days', ''),
                "startTime": firstMeeting.get('startTime', ''),
                "endTime": firstMeeting.get('endTime', ''),
                "building": firstMeeting.get('building', ''),
                "room": firstMeeting.get('room', '')
            })
        
        # Index the section using indexCourse
        await vectorStoreService.indexCourse(sectionCourseData)
    
    def _createCourseText(self, course: Dict[str, Any]) -> str:
        """Create rich text representation of course for embedding."""
        parts = []
        
        # Basic info
        parts.append(f"Course: {course.get('courseCode')} - {course.get('courseName')}")
        parts.append(f"Department: {course.get('department', 'Unknown')}")
        parts.append(f"Credits: {course.get('credits', 3)}")
        parts.append(f"Semester: {self._formatSemester(course.get('semester', ''))}")
        
        # Description
        if course.get('description'):
            parts.append(f"Description: {course.get('description')}")
        
        # Restrictions
        if course.get('restrictions'):
            parts.append(f"Restrictions: {course.get('restrictions')}")
        
        # Cross-listings
        if course.get('crossListedWith'):
            crossListed = ', '.join(course.get('crossListedWith', []))
            parts.append(f"Cross-listed with: {crossListed}")
        
        # Section summary
        sections = course.get('sections', [])
        if sections:
            parts.append(f"\nAvailable Sections: {len(sections)}")
            
            # Summarize instructors
            instructors = set()
            deliveryModes = set()
            totalOpen = 0
            
            for section in sections:
                instructor = section.get('instructor', 'TBA')
                if instructor and instructor != 'TBA':
                    instructors.add(instructor)
                deliveryModes.add(section.get('deliveryMode', 'face-to-face'))
                totalOpen += section.get('openSeats', 0)
            
            if instructors:
                parts.append(f"Instructors: {', '.join(sorted(instructors))}")
            
            if len(deliveryModes) > 0:
                parts.append(f"Delivery modes: {', '.join(sorted(deliveryModes))}")
            
            parts.append(f"Total open seats across all sections: {totalOpen}")
        
        return "\n".join(parts)
    
    def _createSectionText(self, section: Dict[str, Any], course: Dict[str, Any]) -> str:
        """Create rich text representation of section for embedding."""
        parts = []
        
        courseCode = course.get('courseCode', 'UNKNOWN')
        sectionId = section.get('sectionId', '0000')
        
        parts.append(f"Section {courseCode}-{sectionId}")
        parts.append(f"Course: {course.get('courseName', '')}")
        parts.append(f"Instructor: {section.get('instructor', 'TBA')}")
        parts.append(f"Semester: {self._formatSemester(course.get('semester', ''))}")
        
        # Seats
        totalSeats = section.get('totalSeats', 0)
        openSeats = section.get('openSeats', 0)
        waitlist = section.get('waitlist', 0)
        
        if openSeats > 0:
            parts.append(f"Availability: {openSeats} open seats (out of {totalSeats})")
        else:
            parts.append(f"Availability: Full ({totalSeats} total seats, {waitlist} on waitlist)")
        
        # Delivery mode
        deliveryMode = section.get('deliveryMode', 'face-to-face')
        parts.append(f"Delivery: {deliveryMode}")
        
        # Meeting times
        meetingTimes = section.get('meetingTimes', [])
        if meetingTimes:
            parts.append("\nMeeting Times:")
            for meeting in meetingTimes:
                days = meeting.get('days', '')
                startTime = meeting.get('startTime', '')
                endTime = meeting.get('endTime', '')
                building = meeting.get('building', '')
                room = meeting.get('room', '')
                
                timeStr = f"  {days}: {startTime} - {endTime}"
                if building and room:
                    timeStr += f" in {building} {room}"
                elif building:
                    timeStr += f" in {building}"
                
                parts.append(timeStr)
        else:
            parts.append("Meeting times: Online or TBA")
        
        # Add course description for context
        if course.get('description'):
            parts.append(f"\nCourse Description: {course.get('description')}")
        
        return "\n".join(parts)
    
    def _formatSemester(self, semesterCode: str) -> str:
        """Format semester code to readable text."""
        if not semesterCode or len(semesterCode) < 6:
            return semesterCode
        
        year = semesterCode[:4]
        termCode = semesterCode[4:6]
        
        termMap = {
            "01": "Spring",
            "05": "Summer",
            "08": "Fall",
            "12": "Winter"
        }
        
        term = termMap.get(termCode, "Unknown")
        return f"{term} {year}"


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/index_schedule_data.py <schedule_json_file>")
        print("Example: python scripts/index_schedule_data.py backend/data/current_schedule.json")
        return
    
    inputFile = Path(sys.argv[1])
    
    if not inputFile.exists():
        print(f"❌ Error: File not found: {inputFile}")
        return
    
    print(f"Loading schedule data from: {inputFile}")
    
    with open(inputFile, 'r', encoding='utf-8') as f:
        courses = json.load(f)
    
    print(f"✓ Loaded {len(courses)} courses")
    
    indexer = ScheduleDataIndexer()
    await indexer.indexScheduleData(courses)


if __name__ == "__main__":
    asyncio.run(main())

