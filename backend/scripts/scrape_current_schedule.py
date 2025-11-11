#!/usr/bin/env python3
"""
UMD Schedule of Classes (SOC) Scraper
======================================

Scrapes current semester course sections with instructors, times, and seat availability.
Uses Testudo's sections API for direct data access.

Installation:
    pip install httpx beautifulsoup4

Usage:
    python scripts/scrape_current_schedule.py --semester 202601 --department CMSC
    python scripts/scrape_current_schedule.py --semester 202601 --all  # All departments
    
Semester codes:
    - Spring: YYYY01
    - Summer: YYYY05
    - Fall: YYYY08
    - Winter: YYYY12
    
API Endpoint:
    https://app.testudo.umd.edu/soc/{semester}/sections?courseIds={courseId}
"""

import asyncio
import json
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse
import httpx

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class UMDScheduleScraper:
    """Scraper for UMD Schedule of Classes (current semester sections)."""
    
    def __init__(self, semester: str):
        """
        Initialize scraper.
        
        Args:
            semester: Semester code (e.g., "202601" for Spring 2026)
        """
        self.semester = semester
        self.baseUrl = "https://app.testudo.umd.edu/soc"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Day mapping
        self.dayMapping = {
            "M": "Monday",
            "Tu": "Tuesday",
            "W": "Wednesday",
            "Th": "Thursday",
            "F": "Friday",
            "Sa": "Saturday",
            "Su": "Sunday"
        }
    
    async def scrapeDepartment(self, departmentCode: str) -> List[Dict[str, Any]]:
        """
        Scrape all courses and sections for a department.
        Uses Testudo's sections API for direct access.
        
        Args:
            departmentCode: Department code (e.g., "CMSC")
            
        Returns:
            List of course dictionaries with section information
        """
        print(f"\n📚 Fetching {departmentCode} courses for semester {self.semester}...")
        
        try:
            # Step 1: Get list of courses from department page
            courseIds = await self._getCourseIdsForDepartment(departmentCode)
            
            if not courseIds:
                print(f"   ⚠️  No courses found")
                return []
            
            print(f"   ✓ Found {len(courseIds)} courses")
            
            # Step 2: Fetch sections for each course using the API
            courses = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for courseId in courseIds:
                    try:
                        course = await self._fetchCourseWithSections(
                            client, courseId, departmentCode
                        )
                        if course:
                            courses.append(course)
                    except Exception as error:
                        print(f"   ⚠️  Error fetching {courseId}: {error}")
                        continue
            
            print(f"   ✓ Parsed {len(courses)} courses with sections")
            return courses
                
        except Exception as error:
            print(f"   ❌ Error: {error}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _getCourseIdsForDepartment(self, departmentCode: str) -> List[str]:
        """Get list of course IDs for a department."""
        url = f"{self.baseUrl}/{self.semester}/{departmentCode}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all course divs and extract IDs
            courseIds = []
            courseDivs = soup.find_all('div', class_='course')
            
            for courseDiv in courseDivs:
                courseId = courseDiv.get('id')
                if courseId:
                    courseIds.append(courseId)
            
            return courseIds
            
        except Exception as error:
            print(f"   ❌ Error fetching course list: {error}")
            return []
    
    async def _fetchCourseWithSections(
        self, 
        client: httpx.AsyncClient, 
        courseId: str, 
        departmentCode: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch course details and sections using the sections API.
        
        Args:
            client: HTTP client
            courseId: Course ID (e.g., "CMSC131")
            departmentCode: Department code
            
        Returns:
            Course dictionary with sections
        """
        # Fetch course metadata from main page (we already have it in cache)
        # For now, fetch sections first and we'll get metadata separately
        
        sectionsUrl = f"{self.baseUrl}/{self.semester}/sections?courseIds={courseId}"
        
        try:
            response = await client.get(sectionsUrl, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the course-sections div
            courseSectionsDiv = soup.find('div', class_='course-sections')
            
            if not courseSectionsDiv:
                return None
            
            # Parse sections
            sections = []
            sectionDivs = courseSectionsDiv.find_all('div', class_='section')
            
            for sectionDiv in sectionDivs:
                section = self._parseSection(sectionDiv, courseId)
                if section:
                    sections.append(section)
            
            # Get course metadata (we'll fetch from the course details API or parse from cache)
            courseMetadata = await self._getCourseMetadata(client, courseId)
            
            return {
                "courseCode": courseId,
                "courseName": courseMetadata.get("courseName", "Unknown"),
                "department": departmentCode,
                "credits": courseMetadata.get("credits", 3),
                "gradingMethod": courseMetadata.get("gradingMethod", "Regular"),
                "description": courseMetadata.get("description", ""),
                "restrictions": courseMetadata.get("restrictions", ""),
                "crossListedWith": courseMetadata.get("crossListedWith", []),
                "semester": self.semester,
                "sections": sections,
                "totalSections": len(sections)
            }
            
        except Exception as error:
            print(f"      ⚠️  Error fetching sections for {courseId}: {error}")
            return None
    
    async def _getCourseMetadata(
        self, 
        client: httpx.AsyncClient, 
        courseId: str
    ) -> Dict[str, Any]:
        """Get course metadata from the main course page."""
        # Fetch from the main department page which we cached
        # For now, return minimal metadata - we can enhance this later
        try:
            # Try to get from course-specific page
            url = f"{self.baseUrl}/{self.semester}/{courseId[:4]}"  # Department from course ID
            response = await client.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the specific course div
            courseDiv = soup.find('div', id=courseId)
            
            if courseDiv:
                return self._parseCourseMetadata(courseDiv)
        except:
            pass
        
        # Return defaults if we can't fetch
        return {
            "courseName": "Unknown",
            "credits": 3,
            "gradingMethod": "Regular",
            "description": "",
            "restrictions": "",
            "crossListedWith": []
        }
    
    def _parseCourseMetadata(self, courseDiv) -> Dict[str, Any]:
        """Parse course metadata from course div."""
        metadata = {}
        
        # Course title
        titleSpan = courseDiv.find('span', class_='course-title')
        metadata["courseName"] = titleSpan.get_text(strip=True) if titleSpan else "Unknown"
        
        # Credits
        creditsSpan = courseDiv.find('span', class_='course-min-credits')
        metadata["credits"] = self._parseCredits(creditsSpan.get_text(strip=True) if creditsSpan else "3")
        
        # Grading method
        gradingSpan = courseDiv.find('span', class_='grading-method')
        metadata["gradingMethod"] = self._parseGradingMethod(gradingSpan) if gradingSpan else "Regular"
        
        # Description
        descriptionDivs = courseDiv.find_all('div', class_='approved-course-text')
        metadata["description"] = ""
        metadata["restrictions"] = ""
        metadata["crossListedWith"] = []
        
        for descDiv in descriptionDivs:
            text = descDiv.get_text(strip=True)
            
            if 'Restriction:' in text:
                metadata["restrictions"] = text
            elif 'Cross-listed with:' in text:
                metadata["crossListedWith"] = self._extractCrossListed(text)
            elif len(text) > 50 and 'Credit only granted for' not in text:
                metadata["description"] = text
        
        return metadata
    
    def _parseSection(self, sectionDiv, courseCode: str) -> Optional[Dict[str, Any]]:
        """Parse a single section div."""
        try:
            # Section ID
            sectionIdSpan = sectionDiv.find('span', class_='section-id')
            sectionId = sectionIdSpan.get_text(strip=True) if sectionIdSpan else "0000"
            
            # Instructor
            instructorSpan = sectionDiv.find('span', class_='section-instructor')
            instructor = "TBA"
            if instructorSpan:
                instructor = instructorSpan.get_text(strip=True).replace('Instructor:', '').strip()
            
            # Seats information
            seatsInfo = self._parseSeatsInfo(sectionDiv)
            
            # Meeting times
            meetingTimes = self._parseMeetingTimes(sectionDiv)
            
            # Delivery mode (online, blended, f2f)
            deliveryMode = self._getDeliveryMode(sectionDiv)
            
            return {
                "sectionId": sectionId,
                "courseCode": courseCode,
                "instructor": instructor,
                "totalSeats": seatsInfo["total"],
                "openSeats": seatsInfo["open"],
                "waitlist": seatsInfo["waitlist"],
                "meetingTimes": meetingTimes,
                "deliveryMode": deliveryMode
            }
            
        except Exception as error:
            print(f"      ⚠️  Error parsing section: {error}")
            return None
    
    def _parseSeatsInfo(self, sectionDiv) -> Dict[str, int]:
        """Extract seat availability information."""
        result = {"total": 0, "open": 0, "waitlist": 0}
        
        try:
            # Total seats
            totalSeatsSpan = sectionDiv.find('span', class_='total-seats-count')
            if totalSeatsSpan:
                result["total"] = int(totalSeatsSpan.get_text(strip=True))
            
            # Open seats
            openSeatsSpan = sectionDiv.find('span', class_='open-seats-count')
            if openSeatsSpan:
                result["open"] = int(openSeatsSpan.get_text(strip=True))
            
            # Waitlist
            waitlistSpan = sectionDiv.find('span', class_='waitlist-count')
            if waitlistSpan:
                result["waitlist"] = int(waitlistSpan.get_text(strip=True))
        except:
            pass
        
        return result
    
    def _parseMeetingTimes(self, sectionDiv) -> List[Dict[str, str]]:
        """Extract meeting times and locations."""
        meetingTimes = []
        
        try:
            classDaysContainer = sectionDiv.find('div', class_='class-days-container')
            if not classDaysContainer:
                return meetingTimes
            
            # Find all time slots
            rows = classDaysContainer.find_all('div', class_='row')
            
            for row in rows:
                # Days
                daysSpan = row.find('span', class_='section-days')
                if not daysSpan:
                    continue
                
                days = daysSpan.get_text(strip=True)
                
                # Start time
                startTimeSpan = row.find('span', class_='class-start-time')
                startTime = startTimeSpan.get_text(strip=True) if startTimeSpan else ""
                
                # End time
                endTimeSpan = row.find('span', class_='class-end-time')
                endTime = endTimeSpan.get_text(strip=True) if endTimeSpan else ""
                
                # Building and room
                buildingSpan = row.find('span', class_='building-code')
                building = buildingSpan.get_text(strip=True) if buildingSpan else ""
                
                roomSpan = row.find('span', class_='class-room')
                room = roomSpan.get_text(strip=True) if roomSpan else ""
                
                if days and startTime:
                    meetingTimes.append({
                        "days": days,
                        "startTime": startTime,
                        "endTime": endTime,
                        "building": building,
                        "room": room
                    })
        except Exception as error:
            print(f"         ⚠️  Error parsing meeting times: {error}")
        
        return meetingTimes
    
    def _getDeliveryMode(self, sectionDiv) -> str:
        """Determine delivery mode (online, blended, face-to-face)."""
        classes = sectionDiv.get('class', [])
        
        if 'delivery-online' in classes:
            return "online"
        elif 'delivery-blended' in classes:
            return "blended"
        elif 'delivery-f2f' in classes:
            return "face-to-face"
        
        return "face-to-face"  # Default
    
    def _parseGradingMethod(self, gradingSpan) -> str:
        """Parse grading method abbreviations."""
        text = gradingSpan.get_text(strip=True)
        
        abbr = gradingSpan.find('abbr')
        if abbr and abbr.get('title'):
            return abbr.get('title')
        
        # Common abbreviations
        mapping = {
            "Reg": "Regular",
            "P/F": "Pass/Fail",
            "Audit": "Audit",
            "Sat": "Satisfactory"
        }
        
        return mapping.get(text, text)
    
    def _parseCredits(self, creditsText: str) -> int:
        """Parse credits (handles ranges like '1-4')."""
        try:
            # If it's a range, take the first number
            match = re.search(r'(\d+)', creditsText)
            if match:
                return int(match.group(1))
        except:
            pass
        
        return 3  # Default
    
    def _extractCrossListed(self, text: str) -> List[str]:
        """Extract cross-listed course codes."""
        # Example: "Cross-listed with: INST101."
        match = re.search(r'Cross-listed with:\s*([A-Z]{4}\d{3}[A-Z]?(?:,\s*[A-Z]{4}\d{3}[A-Z]?)*)', text)
        if match:
            coursesText = match.group(1)
            return [c.strip().rstrip('.') for c in coursesText.split(',')]
        return []
    
    async def scrapeAllDepartments(self, departments: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape multiple departments.
        
        Args:
            departments: List of department codes
            
        Returns:
            List of all courses from all departments
        """
        allCourses = []
        totalDepts = len(departments)
        
        for idx, dept in enumerate(departments, 1):
            print(f"\n[{idx}/{totalDepts}] Processing {dept}...")
            courses = await self.scrapeDepartment(dept)
            allCourses.extend(courses)
            
            # Be nice to the server - wait between departments
            if idx < totalDepts:
                await asyncio.sleep(2)
        
        return allCourses


async def getDepartmentList() -> List[str]:
    """Get list of all UMD departments."""
    # Common UMD departments - you can expand this list
    return [
        "AASP", "AAST", "AGNR", "AMSC", "ANSC", "ANTH", "AOSC", "ARAB", "ARCH",
        "AREC", "ARHU", "ARMY", "ARSC", "ARTH", "ARTT", "ASTR", "BCHM", "BEES",
        "BENG", "BIOE", "BIOM", "BISI", "BMGT", "BSCI", "BSGC", "BSOS", "BUFN",
        "BUMO", "BUSI", "CBMG", "CCJS", "CHBE", "CHEM", "CHIN", "CINE", "CLFS",
        "CMLT", "CMSC", "COMM", "CPGH", "CPJT", "CPMS", "CPPL", "CPSP", "DANC",
        "ECON", "EDCI", "EDCP", "EDHD", "EDHI", "EDMS", "EDSP", "EDUC", "ENCE",
        "ENAE", "ENBE", "ENCH", "ENCO", "ENEE", "ENES", "ENFP", "ENGL", "ENMA",
        "ENME", "ENPM", "ENRE", "ENSE", "ENSP", "ENST", "ENTM", "EPIB", "FMSC",
        "FOLA", "FREN", "GEOG", "GEOL", "GERM", "GREK", "GVPT", "HEBR", "HEIP",
        "HHUM", "HISP", "HIST", "HLSA", "HLTH", "HONR", "IDEA", "IMMR", "INFM",
        "INFO", "INST", "ITAL", "JAPN", "JEWI", "JOUR", "KNES", "KORA", "LARC",
        "LASC", "LAST", "LATN", "LBSC", "LIBS", "LING", "MATH", "MEES", "MIEH",
        "MLSC", "MUSC", "NEUR", "NFSC", "PERS", "PHIL", "PHPE", "PHSC", "PHYS",
        "PLCY", "PLSC", "PORT", "PSYC", "PUAF", "RDEV", "RELS", "RUSS", "SLAA",
        "SLLC", "SOCY", "SPAN", "SPHL", "STAT", "TDPS", "THET", "TLPL", "UMEI",
        "UNIV", "URSP", "USLT", "VMSC", "WGSS", "WMST"
    ]


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Scrape UMD Schedule of Classes')
    parser.add_argument('--semester', type=str, required=True, 
                       help='Semester code (e.g., 202601 for Spring 2026)')
    parser.add_argument('--department', type=str, 
                       help='Single department code (e.g., CMSC)')
    parser.add_argument('--all', action='store_true',
                       help='Scrape all departments')
    parser.add_argument('--output', type=str, 
                       default='backend/data/current_schedule.json',
                       help='Output JSON file path')
    
    args = parser.parse_args()
    
    scraper = UMDScheduleScraper(args.semester)
    
    print("\n" + "="*60)
    print("   UMD Schedule of Classes Scraper")
    print("="*60)
    print(f"Semester: {args.semester}")
    
    courses = []
    
    if args.department:
        # Single department
        print(f"Mode: Single department ({args.department})")
        courses = await scraper.scrapeDepartment(args.department)
    
    elif args.all:
        # All departments
        print("Mode: All departments")
        departments = await getDepartmentList()
        print(f"Scraping {len(departments)} departments...")
        courses = await scraper.scrapeAllDepartments(departments)
    
    else:
        print("❌ Error: Must specify --department or --all")
        return
    
    # Save to file
    outputPath = Path(args.output)
    outputPath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(outputPath, 'w', encoding='utf-8') as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print(f"✓ Scraped {len(courses)} courses with sections")
    print(f"✓ Saved to: {outputPath}")
    print("="*60 + "\n")
    
    # Statistics
    totalSections = sum(course.get('totalSections', 0) for course in courses)
    coursesWithSections = sum(1 for c in courses if c.get('sections'))
    
    print("Statistics:")
    print(f"  - Total courses: {len(courses)}")
    print(f"  - Courses with sections: {coursesWithSections}")
    print(f"  - Total sections: {totalSections}")


if __name__ == "__main__":
    asyncio.run(main())

