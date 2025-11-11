"""
Web scraper for UMD course catalog.

Usage:
    python scripts/scrape_umd_courses.py https://academiccatalog.umd.edu/undergraduate/courses/aasp/
    python scripts/scrape_umd_courses.py --all  # Scrape all departments
"""

import asyncio
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store_service import vectorStoreService


class UMDCourseScraper:
    """Scraper for UMD Academic Catalog."""
    
    def __init__(self, enrichWithPlanetTerp: bool = True):
        self.baseUrl = "https://academiccatalog.umd.edu"
        self.planetTerpUrl = "https://api.planetterp.com/v1"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.enrichWithPlanetTerp = enrichWithPlanetTerp
    
    async def scrapeDepartmentCourses(self, url: str) -> List[Dict[str, Any]]:
        """
        Scrape all courses from a department page.
        
        Args:
            url: URL of department course page
            
        Returns:
            List of course dictionaries
        """
        print(f"Fetching: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
            soup = BeautifulSoup(response.text, 'html.parser')
            courses = []
            
            # Find all course blocks
            courseBlocks = soup.find_all('div', class_='courseblock')
            
            print(f"Found {len(courseBlocks)} courses")
            
            for block in courseBlocks:
                course = self._parseCourseBlock(block)
                if course:
                    courses.append(course)
            
            # Enrich with PlanetTerp data if enabled
            if self.enrichWithPlanetTerp and courses:
                print(f"\nEnriching courses with PlanetTerp data...")
                await self._enrichCoursesWithPlanetTerp(courses)
            
            return courses
            
        except Exception as error:
            print(f"Error scraping {url}: {error}")
            return []
    
    def _parseCourseBlock(self, block) -> Optional[Dict[str, Any]]:
        """
        Parse a single course block from HTML.
        
        Args:
            block: BeautifulSoup element for course block
            
        Returns:
            Course dictionary or None
        """
        try:
            # Extract title and code
            titleElement = block.find('p', class_='courseblocktitle')
            if not titleElement:
                return None
            
            titleStrong = titleElement.find('strong')
            if not titleStrong:
                return None
            
            titleText = titleStrong.get_text(strip=True)
            
            # Parse course code, name, and credits
            # Format: "AAAS100 Introduction to African American Studies (3 Credits)"
            # Also handles variable credits: "(1-4 Credits)"
            match = re.match(r'([A-Z]{4}\d{3}[A-Z]?)\s+(.+?)\s*\((\d+(?:-\d+)?)\s+Credits?\)', titleText)
            
            if not match:
                print(f"Warning: Could not parse title: {titleText}")
                return None
            
            courseCode = match.group(1)
            courseName = match.group(2)
            creditsStr = match.group(3)
            
            # Handle credit ranges (e.g., "1-4" -> take max value)
            if '-' in creditsStr:
                creditsParts = creditsStr.split('-')
                credits = int(creditsParts[1])  # Use max credits
            else:
                credits = int(creditsStr)
            
            # Extract department from course code
            department = self._getDepartmentName(courseCode[:4])
            
            # Extract description
            descElement = block.find('p', class_='courseblockdesc')
            description = descElement.get_text(strip=True) if descElement else ""
            
            # Extract additional info (prerequisites, restrictions, etc.)
            extraInfo = self._parseExtraInfo(block)
            
            # Determine course level
            level = courseCode[4] + "00"  # First digit after letters
            
            # Extract topics/keywords from description
            topics = self._extractTopics(courseName, description)
            
            course = {
                "courseCode": courseCode,
                "courseName": courseName,
                "department": department,
                "description": description,
                "credits": credits,
                "level": level,
                "prerequisites": extraInfo.get("prerequisites", []),
                "corequisites": extraInfo.get("corequisites", []),
                "restrictions": extraInfo.get("restrictions", ""),
                "topics": topics
            }
            
            return course
            
        except Exception as error:
            print(f"Error parsing course block: {error}")
            return None
    
    def _parseExtraInfo(self, block) -> Dict[str, Any]:
        """
        Parse extra course information (prerequisites, restrictions, etc.).
        
        Args:
            block: BeautifulSoup course block element
            
        Returns:
            Dictionary with extra info
        """
        info = {
            "prerequisites": [],
            "corequisites": [],
            "restrictions": ""
        }
        
        extraElements = block.find_all('p', class_='courseblockextra')
        
        for element in extraElements:
            text = element.get_text(strip=True)
            
            # Parse prerequisites
            if "Prerequisite:" in text or "Prerequisite(s):" in text:
                prereqs = self._extractCourseCodes(text)
                info["prerequisites"] = prereqs
            
            # Parse corequisites
            elif "Corequisite:" in text or "Corequisite(s):" in text:
                coreqs = self._extractCourseCodes(text)
                info["corequisites"] = coreqs
            
            # Parse restrictions
            elif "Restriction:" in text:
                info["restrictions"] = text
        
        return info
    
    def _extractCourseCodes(self, text: str) -> List[str]:
        """
        Extract course codes from text.
        
        Args:
            text: Text containing course codes
            
        Returns:
            List of course codes
        """
        # Pattern: AAAA123 or AAAA123A
        pattern = r'\b([A-Z]{4}\d{3}[A-Z]?)\b'
        matches = re.findall(pattern, text)
        return list(set(matches))  # Remove duplicates
    
    def _getDepartmentName(self, deptCode: str) -> str:
        """
        Get full department name from code.
        
        Args:
            deptCode: Department code (e.g., "CMSC")
            
        Returns:
            Full department name
        """
        departmentMap = {
            "AASP": "African American Studies",
            "AAAS": "African American Studies",
            "CMSC": "Computer Science",
            "MATH": "Mathematics",
            "ENGL": "English",
            "HIST": "History",
            "PHYS": "Physics",
            "CHEM": "Chemistry",
            "BIOL": "Biology",
            "PSYC": "Psychology",
            "ECON": "Economics",
            "ENES": "Engineering",
            "BMGT": "Business Management",
            "INST": "Information Studies",
            "ARTT": "Art Studio",
            "MUSC": "Music",
            "GVPT": "Government and Politics",
            "STAT": "Statistics",
            "ASTR": "Astronomy",
            "GEOG": "Geography",
            "SOCY": "Sociology",
            "ANTH": "Anthropology",
        }
        
        return departmentMap.get(deptCode, deptCode)
    
    def _extractTopics(self, courseName: str, description: str) -> List[str]:
        """
        Extract topic keywords from course name and description.
        
        Args:
            courseName: Course name
            description: Course description
            
        Returns:
            List of topic keywords
        """
        topics = []
        
        # Common keywords to extract
        keywords = [
            "programming", "algorithm", "data structure", "machine learning",
            "artificial intelligence", "database", "software", "web",
            "network", "security", "systems", "calculus", "algebra",
            "statistics", "probability", "design", "engineering", "physics",
            "chemistry", "biology", "writing", "literature", "history",
            "economics", "business", "management", "research", "analysis"
        ]
        
        combinedText = (courseName + " " + description).lower()
        
        for keyword in keywords:
            if keyword in combinedText:
                topics.append(keyword.title())
        
        # Extract words from course name
        nameWords = re.findall(r'\b[A-Z][a-z]+\b', courseName)
        topics.extend(nameWords[:5])  # Limit to 5 words from name
        
        return list(set(topics))[:10]  # Return unique, max 10 topics
    
    async def _enrichCoursesWithPlanetTerp(self, courses: List[Dict[str, Any]]):
        """
        Enrich course data with PlanetTerp API information.
        
        Args:
            courses: List of course dictionaries to enrich (modified in place)
        """
        enriched = 0
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for course in courses:
                courseCode = course.get("courseCode", "")
                
                try:
                    # Call PlanetTerp API (with reviews)
                    response = await client.get(
                        f"{self.planetTerpUrl}/course",
                        params={"name": courseCode, "reviews": True},
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Merge ALL PlanetTerp data into course
                        if data:
                            # Store all PlanetTerp fields
                            course["avgGPA"] = data.get("average_gpa")
                            course["professors"] = data.get("professors", [])
                            
                            # Store PlanetTerp-specific data separately for reference
                            course["planetTerp"] = {
                                "department": data.get("department"),
                                "courseNumber": data.get("course_number"),
                                "title": data.get("title"),
                                "description": data.get("description"),
                                "credits": data.get("credits"),
                                "averageGPA": data.get("average_gpa"),
                                "professors": data.get("professors", []),
                                "reviews": data.get("reviews", [])
                            }
                            
                            # Store review count at top level for easy access
                            reviews = data.get("reviews", [])
                            if reviews:
                                course["reviewCount"] = len(reviews)
                                course["reviews"] = reviews  # Full review list
                            
                            # Override catalog description if PlanetTerp has a better one
                            ptDescription = data.get("description", "")
                            if ptDescription and len(ptDescription) > len(course.get("description", "")):
                                course["descriptionPlanetTerp"] = ptDescription
                            
                            enriched += 1
                    
                    # Be nice to the API
                    await asyncio.sleep(0.2)
                    
                except Exception as error:
                    print(f"  Warning: Could not fetch PlanetTerp data for {courseCode}: {error}")
                    continue
        
        print(f"  ✅ Enriched {enriched}/{len(courses)} courses with PlanetTerp data")


async def scrapeDepartment(url: str, indexImmediately: bool = False, enrichWithPlanetTerp: bool = True):
    """
    Scrape courses from a department and optionally index them.
    
    Args:
        url: Department URL
        indexImmediately: If True, index to Pinecone immediately
        enrichWithPlanetTerp: If True, fetch additional data from PlanetTerp API
    """
    scraper = UMDCourseScraper(enrichWithPlanetTerp=enrichWithPlanetTerp)
    courses = await scraper.scrapeDepartmentCourses(url)
    
    if not courses:
        print("No courses found")
        return
    
    # Save to JSON file
    deptMatch = re.search(r'/courses/([a-z]+)/', url)
    deptCode = deptMatch.group(1).upper() if deptMatch else "courses"
    
    outputFile = f"data/scraped_{deptCode}.json"
    Path("data").mkdir(exist_ok=True)
    
    with open(outputFile, 'w') as f:
        json.dump({"courses": courses}, f, indent=2)
    
    print(f"\n✅ Saved {len(courses)} courses to {outputFile}")
    
    # Optionally index immediately
    if indexImmediately:
        if not vectorStoreService.pineconeEnabled:
            print("⚠️  Pinecone not enabled, skipping indexing")
            return
        
        print("\nIndexing courses to Pinecone...")
        stats = await vectorStoreService.indexCourses(courses)
        print(f"✅ Indexed: {stats['success']}")
        print(f"❌ Failed: {stats['failed']}")


async def scrapeAllDepartments(enrichWithPlanetTerp: bool = True):
    """
    Scrape all UMD departments.
    
    Args:
        enrichWithPlanetTerp: If True, fetch additional data from PlanetTerp API
    """
    # Common UMD department codes
    departments = [
        "aasp", "cmsc", "math", "engl", "hist", "phys", "chem", "biol",
        "psyc", "econ", "enes", "bmgt", "inst", "artt", "musc", "gvpt",
        "stat", "astr", "geog", "socy", "anth"
    ]
    
    baseUrl = "https://academiccatalog.umd.edu/undergraduate/courses"
    
    allCourses = []
    
    for dept in departments:
        url = f"{baseUrl}/{dept}/"
        print(f"\n{'='*60}")
        print(f"Scraping {dept.upper()}...")
        print('='*60)
        
        scraper = UMDCourseScraper(enrichWithPlanetTerp=enrichWithPlanetTerp)
        courses = await scraper.scrapeDepartmentCourses(url)
        
        if courses:
            allCourses.extend(courses)
            print(f"✅ {dept.upper()}: {len(courses)} courses")
        
        # Be nice to the server
        await asyncio.sleep(1)
    
    # Save all courses
    outputFile = "data/all_umd_courses.json"
    with open(outputFile, 'w') as f:
        json.dump({"courses": allCourses}, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ Total: {len(allCourses)} courses saved to {outputFile}")
    print('='*60)


async def main():
    """Main entry point."""
    
    print("=" * 60)
    print("UMD Course Catalog Scraper")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/scrape_umd_courses.py <URL> [--index] [--no-planetterp]")
        print("  python scripts/scrape_umd_courses.py --all [--no-planetterp]")
        print()
        print("Options:")
        print("  --index          Index courses to Pinecone immediately")
        print("  --no-planetterp  Skip PlanetTerp API enrichment")
        print()
        print("Examples:")
        print("  python scripts/scrape_umd_courses.py https://academiccatalog.umd.edu/undergraduate/courses/cmsc/")
        print("  python scripts/scrape_umd_courses.py --all")
        print("  python scripts/scrape_umd_courses.py --all --no-planetterp  # Faster, no API calls")
        print("  python scripts/scrape_umd_courses.py <URL> --index  # Scrape and index")
        return
    
    arg = sys.argv[1]
    
    # Check flags
    indexImmediately = "--index" in sys.argv
    enrichWithPlanetTerp = "--no-planetterp" not in sys.argv
    
    if arg == "--all":
        await scrapeAllDepartments(enrichWithPlanetTerp=enrichWithPlanetTerp)
    elif arg.startswith("http"):
        await scrapeDepartment(arg, indexImmediately, enrichWithPlanetTerp)
    else:
        print(f"Invalid argument: {arg}")
        print("Use --all or provide a URL")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
    except Exception as error:
        print(f"\n❌ Error: {error}")
        import traceback
        traceback.print_exc()

