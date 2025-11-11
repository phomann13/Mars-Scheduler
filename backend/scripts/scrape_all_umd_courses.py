#!/usr/bin/env python3
"""
Comprehensive UMD Course Scraper and Indexer
===========================================

This script:
1. Scrapes the UMD approved courses page to get all department codes
2. Scrapes each department's courses with PlanetTerp enrichment
3. Aggregates all courses into a single JSON file
4. Automatically indexes everything into Pinecone

Usage:
    python scripts/scrape_all_umd_courses.py [--no-index] [--no-planetterp]
    
Options:
    --no-index       Skip automatic indexing after scraping
    --no-planetterp  Skip PlanetTerp API enrichment (faster but less data)
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Set
from datetime import datetime

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.scrape_umd_courses import UMDCourseScraper


class UMDDepartmentScraper:
    """Scraper for all UMD departments and their courses."""
    
    def __init__(self, enrichWithPlanetTerp: bool = True):
        self.baseUrl = "https://academiccatalog.umd.edu"
        self.approvedCoursesUrl = f"{self.baseUrl}/undergraduate/approved-courses/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.enrichWithPlanetTerp = enrichWithPlanetTerp
    
    async def getDepartmentCodes(self) -> List[Dict[str, str]]:
        """
        Scrape the approved courses page to get all department codes.
        
        Returns:
            List of dicts with 'code' and 'name' fields
        """
        print(f"Fetching department list from {self.approvedCoursesUrl}...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self.approvedCoursesUrl, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"❌ Failed to fetch approved courses page: {response.status_code}")
                    return []
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all department links
                # Pattern: <li><a href="/undergraduate/approved-courses/aast/">AAST - Asian American Studies</a></li>
                departments = []
                departmentLinks = soup.find_all('a', href=lambda href: href and '/undergraduate/approved-courses/' in href)
                
                for link in departmentLinks:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Extract department code from href (e.g., /undergraduate/approved-courses/aast/ -> AAST)
                    if '/undergraduate/approved-courses/' in href:
                        # Extract path segment
                        pathParts = href.strip('/').split('/')
                        if len(pathParts) >= 3:
                            code = pathParts[-1].upper()
                            
                            # Validate it's a 4-letter code (with optional special patterns)
                            if len(code) >= 2 and len(code) <= 6 and code.isalpha():
                                # Extract full name from text (e.g., "AAST - Asian American Studies")
                                if ' - ' in text:
                                    codePart, namePart = text.split(' - ', 1)
                                    departments.append({
                                        'code': code,
                                        'name': namePart.strip(),
                                        'url': f"{self.baseUrl}{href}"
                                    })
                
                # Remove duplicates (some departments appear multiple times)
                uniqueDepartments = []
                seenCodes = set()
                
                for dept in departments:
                    if dept['code'] not in seenCodes:
                        uniqueDepartments.append(dept)
                        seenCodes.add(dept['code'])
                
                print(f"✅ Found {len(uniqueDepartments)} departments")
                return uniqueDepartments
                
        except Exception as error:
            print(f"❌ Error fetching department list: {error}")
            return []
    
    async def scrapeAllDepartments(self, autoIndex: bool = False) -> Dict[str, Any]:
        """
        Scrape all UMD departments and optionally index them.
        
        Args:
            autoIndex: Whether to automatically index after scraping
            
        Returns:
            Summary statistics
        """
        startTime = datetime.now()
        
        # Get all department codes
        departments = await self.getDepartmentCodes()
        
        if not departments:
            print("❌ No departments found to scrape")
            return {
                'success': False,
                'departments': 0,
                'courses': 0
            }
        
        print(f"\n{'='*60}")
        print(f"Starting comprehensive scrape of {len(departments)} departments")
        print(f"PlanetTerp enrichment: {'ENABLED' if self.enrichWithPlanetTerp else 'DISABLED'}")
        print(f"{'='*60}\n")
        
        # Initialize scraper
        scraper = UMDCourseScraper(enrichWithPlanetTerp=self.enrichWithPlanetTerp)
        
        # Track results
        allCourses = []
        successfulDepts = 0
        failedDepts = []
        
        # Scrape each department
        for i, dept in enumerate(departments, 1):
            print(f"\n[{i}/{len(departments)}] Scraping {dept['code']} - {dept['name']}")
            print(f"URL: {dept['url']}")
            
            try:
                # Scrape this department
                courses = await scraper.scrapeDepartmentCourses(dept['url'])
                
                if courses:
                    # Add department info to each course
                    for course in courses:
                        course['departmentCode'] = dept['code']
                        course['departmentName'] = dept['name']
                    
                    allCourses.extend(courses)
                    successfulDepts += 1
                    print(f"  ✅ Found {len(courses)} courses")
                else:
                    print(f"  ⚠️  No courses found")
                
                # Small delay to be respectful
                await asyncio.sleep(1.0)
                
            except Exception as error:
                print(f"  ❌ Error: {error}")
                failedDepts.append(dept['code'])
                continue
        
        # Save all courses to JSON
        outputPath = Path(__file__).parent.parent / 'data' / 'scraped_all_courses.json'
        outputPath.parent.mkdir(exist_ok=True)
        
        with open(outputPath, 'w') as f:
            json.dump({
                'metadata': {
                    'scrapedAt': datetime.now().isoformat(),
                    'totalDepartments': len(departments),
                    'successfulDepartments': successfulDepts,
                    'failedDepartments': failedDepts,
                    'totalCourses': len(allCourses),
                    'enrichedWithPlanetTerp': self.enrichWithPlanetTerp
                },
                'courses': allCourses
            }, f, indent=2)
        
        endTime = datetime.now()
        duration = (endTime - startTime).total_seconds()
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successful departments: {successfulDepts}/{len(departments)}")
        if failedDepts:
            print(f"❌ Failed departments: {', '.join(failedDepts)}")
        print(f"📚 Total courses scraped: {len(allCourses)}")
        print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"💾 Saved to: {outputPath}")
        print(f"{'='*60}\n")
        
        # Auto-index if requested
        if autoIndex and allCourses:
            print("Starting automatic indexing into Pinecone...")
            await self.indexCourses(str(outputPath))
        
        return {
            'success': True,
            'departments': successfulDepts,
            'courses': len(allCourses),
            'outputPath': str(outputPath),
            'duration': duration
        }
    
    async def indexCourses(self, jsonFilePath: str):
        """
        Index scraped courses into Pinecone using the index_courses script.
        
        Args:
            jsonFilePath: Path to the JSON file with scraped courses
        """
        try:
            from scripts.index_courses import indexCoursesFromFile
            
            print(f"\n{'='*60}")
            print(f"INDEXING COURSES INTO PINECONE")
            print(f"{'='*60}\n")
            
            await indexCoursesFromFile(jsonFilePath)
            
        except Exception as error:
            print(f"❌ Error during indexing: {error}")
            print("You can manually index later with:")
            print(f"  python scripts/index_courses.py {jsonFilePath}")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scrape all UMD courses and optionally index them into Pinecone'
    )
    parser.add_argument(
        '--no-index',
        action='store_true',
        help='Skip automatic indexing after scraping'
    )
    parser.add_argument(
        '--no-planetterp',
        action='store_true',
        help='Skip PlanetTerp API enrichment (faster but less data)'
    )
    parser.add_argument(
        '--departments',
        nargs='+',
        help='Only scrape specific departments (e.g., CMSC MATH PHYS)'
    )
    
    args = parser.parse_args()
    
    # Configuration
    autoIndex = not args.no_index
    enrichWithPlanetTerp = not args.no_planetterp
    
    # Create scraper
    scraper = UMDDepartmentScraper(enrichWithPlanetTerp=enrichWithPlanetTerp)
    
    if args.departments:
        # Scrape only specific departments
        print(f"Scraping specific departments: {', '.join(args.departments)}")
        
        # Get all departments first
        allDepts = await scraper.getDepartmentCodes()
        
        # Filter to requested ones
        requestedDepts = [
            dept for dept in allDepts 
            if dept['code'].upper() in [d.upper() for d in args.departments]
        ]
        
        if not requestedDepts:
            print(f"❌ None of the requested departments found")
            return
        
        print(f"Found {len(requestedDepts)} matching departments")
        
        # Scrape them
        courseScraper = UMDCourseScraper(enrichWithPlanetTerp=enrichWithPlanetTerp)
        allCourses = []
        
        for dept in requestedDepts:
            print(f"\nScraping {dept['code']} - {dept['name']}")
            courses = await courseScraper.scrapeDepartmentCourses(dept['url'])
            
            if courses:
                for course in courses:
                    course['departmentCode'] = dept['code']
                    course['departmentName'] = dept['name']
                allCourses.extend(courses)
                print(f"  ✅ Found {len(courses)} courses")
            
            await asyncio.sleep(1.0)
        
        # Save
        outputPath = Path(__file__).parent.parent / 'data' / f"scraped_{'_'.join(args.departments)}.json"
        outputPath.parent.mkdir(exist_ok=True)
        
        with open(outputPath, 'w') as f:
            json.dump({'courses': allCourses}, f, indent=2)
        
        print(f"\n✅ Saved {len(allCourses)} courses to {outputPath}")
        
        if autoIndex and allCourses:
            await scraper.indexCourses(str(outputPath))
    
    else:
        # Scrape ALL departments
        await scraper.scrapeAllDepartments(autoIndex=autoIndex)


if __name__ == "__main__":
    asyncio.run(main())

