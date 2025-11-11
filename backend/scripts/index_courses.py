"""
Script to index course data into Pinecone vector store.

Usage:
    python scripts/index_courses.py                    # Index sample courses
    python scripts/index_courses.py data/courses.json  # Index from file
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store_service import vectorStoreService


async def indexCoursesFromFile(filePath: str):
    """
    Index courses from a JSON file.
    
    Args:
        filePath: Path to JSON file with course data
    """
    print(f"Loading courses from {filePath}...")
    
    try:
        with open(filePath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {filePath}")
        return
    except json.JSONDecodeError as error:
        print(f"❌ Error: Invalid JSON: {error}")
        return
    
    courses = data.get('courses', data)  # Handle both formats
    
    if not isinstance(courses, list):
        print("❌ Error: Expected a list of courses")
        return
    
    print(f"Found {len(courses)} courses to index")
    
    # Validate course structure
    validCourses = []
    for i, course in enumerate(courses):
        required = ['courseCode', 'courseName', 'department', 'description']
        missing = [field for field in required if field not in course]
        
        if missing:
            print(f"⚠️  Warning: Course {i+1} missing required fields: {missing}")
            continue
        
        validCourses.append(course)
    
    if not validCourses:
        print("❌ No valid courses to index")
        return
    
    print(f"Indexing {len(validCourses)} valid courses...")
    
    # Index courses in batches
    batchSize = 50
    totalSuccess = 0
    totalFailed = 0
    
    for i in range(0, len(validCourses), batchSize):
        batch = validCourses[i:i+batchSize]
        batchNum = i // batchSize + 1
        totalBatches = (len(validCourses) + batchSize - 1) // batchSize
        
        print(f"\nProcessing batch {batchNum}/{totalBatches} ({len(batch)} courses)...")
        stats = await vectorStoreService.indexCourses(batch)
        
        totalSuccess += stats['success']
        totalFailed += stats['failed']
        
        print(f"  ✅ Success: {stats['success']}")
        print(f"  ❌ Failed: {stats['failed']}")
        
        # Small delay to avoid rate limits
        if i + batchSize < len(validCourses):
            await asyncio.sleep(0.5)
    
    print(f"\n{'='*50}")
    print(f"Indexing complete!")
    print(f"✅ Total successfully indexed: {totalSuccess}")
    print(f"❌ Total failed: {totalFailed}")
    print(f"{'='*50}")


async def indexSampleCourses():
    """Index sample UMD courses for testing."""
    
    sampleCourses = [
        {
            "courseCode": "CMSC131",
            "courseName": "Object-Oriented Programming I",
            "department": "Computer Science",
            "description": "Introduction to programming and computer science. Emphasizes understanding and implementation of applications using object-oriented techniques. Requires no prior programming background. Uses Java programming language. Topics include problem solving, algorithm development, object-oriented design, encapsulation, composition, inheritance, polymorphism.",
            "credits": 4,
            "level": "100",
            "prerequisites": [],
            "topics": ["Java", "OOP", "Programming Fundamentals", "Data Structures", "Algorithm Development"]
        },
        {
            "courseCode": "CMSC132",
            "courseName": "Object-Oriented Programming II",
            "department": "Computer Science",
            "description": "Introduction to use of computers to solve problems using software development in Java. Design, build, test, and debug medium-size software systems. Learn to use relevant tools and environments. Understand object-oriented design including interfaces, polymorphism, encapsulation, inheritance, exceptions, recursion, and efficient searching and sorting.",
            "credits": 4,
            "level": "100",
            "prerequisites": ["CMSC131"],
            "topics": ["Java", "OOP", "Software Development", "Data Structures", "Algorithms", "Testing", "Debugging"]
        },
        {
            "courseCode": "CMSC216",
            "courseName": "Introduction to Computer Systems",
            "department": "Computer Science",
            "description": "Introduction to computer systems from programmer's perspective. Assembly language programming, memory management, file I/O, linking and loading, system-level I/O, introduction to concurrency and synchronization, network programming, and sockets.",
            "credits": 4,
            "level": "200",
            "prerequisites": ["CMSC132"],
            "topics": ["C Programming", "Assembly Language", "Memory Management", "Systems Programming", "Concurrency"]
        },
        {
            "courseCode": "CMSC250",
            "courseName": "Discrete Structures",
            "department": "Computer Science",
            "description": "Fundamental mathematical concepts related to computer science, including finite and infinite sets, relations, functions, propositional logic, induction, recursion, combinatorics, and graph theory.",
            "credits": 4,
            "level": "200",
            "prerequisites": ["CMSC131"],
            "topics": ["Discrete Mathematics", "Logic", "Graph Theory", "Combinatorics", "Proof Techniques"]
        },
        {
            "courseCode": "CMSC330",
            "courseName": "Organization of Programming Languages",
            "department": "Computer Science",
            "description": "Survey of programming languages, their properties and trade-offs. Topics include functional programming, type systems, memory management, formal semantics, grammars and parsing, lambda calculus, and concurrent programming.",
            "credits": 3,
            "level": "300",
            "prerequisites": ["CMSC216", "CMSC250"],
            "topics": ["OCaml", "Ruby", "Rust", "Functional Programming", "Type Systems", "Lambda Calculus", "Concurrency"]
        },
        {
            "courseCode": "CMSC351",
            "courseName": "Algorithms",
            "department": "Computer Science",
            "description": "Fundamental techniques for designing efficient algorithms. Analysis of algorithms, divide and conquer, greedy algorithms, dynamic programming, graph algorithms, NP-completeness. Applications to sorting, searching, optimization problems.",
            "credits": 3,
            "level": "300",
            "prerequisites": ["CMSC250"],
            "topics": ["Algorithm Design", "Complexity Analysis", "Dynamic Programming", "Graph Algorithms", "NP-Completeness"]
        },
        {
            "courseCode": "CMSC420",
            "courseName": "Data Structures",
            "department": "Computer Science",
            "description": "Advanced data structures including AVL trees, B-trees, skip lists, heaps, hash tables, spatial data structures like quadtrees and KD-trees, and their applications to databases and geographic information systems.",
            "credits": 3,
            "level": "400",
            "prerequisites": ["CMSC351"],
            "topics": ["AVL Trees", "B-Trees", "Hash Tables", "Spatial Structures", "Quadtrees", "KD-Trees"]
        },
        {
            "courseCode": "CMSC421",
            "courseName": "Introduction to Artificial Intelligence",
            "department": "Computer Science",
            "description": "Introduction to artificial intelligence concepts and techniques. Search algorithms, game playing, knowledge representation, logic, constraint satisfaction, probabilistic reasoning, machine learning, neural networks.",
            "credits": 3,
            "level": "400",
            "prerequisites": ["CMSC351"],
            "topics": ["AI", "Machine Learning", "Search Algorithms", "Neural Networks", "Logic", "Constraint Satisfaction"]
        },
        {
            "courseCode": "CMSC422",
            "courseName": "Introduction to Machine Learning",
            "department": "Computer Science",
            "description": "Introduction to machine learning concepts and algorithms. Supervised learning (regression, classification, SVMs, neural networks), unsupervised learning (clustering, dimensionality reduction), deep learning, reinforcement learning.",
            "credits": 3,
            "level": "400",
            "prerequisites": ["CMSC351", "MATH240"],
            "topics": ["Machine Learning", "Neural Networks", "Deep Learning", "Supervised Learning", "Clustering", "SVMs"]
        },
        {
            "courseCode": "CMSC424",
            "courseName": "Database Design",
            "department": "Computer Science",
            "description": "Database management systems including data models, query languages, database design, transactions, concurrency control, distributed databases, NoSQL databases.",
            "credits": 3,
            "level": "400",
            "prerequisites": ["CMSC351"],
            "topics": ["SQL", "Database Design", "Transactions", "NoSQL", "Distributed Databases"]
        },
        {
            "courseCode": "MATH140",
            "courseName": "Calculus I",
            "department": "Mathematics",
            "description": "Introduction to calculus including limits, continuity, derivatives and their applications, introduction to integration with applications to area and volume.",
            "credits": 4,
            "level": "100",
            "prerequisites": [],
            "topics": ["Calculus", "Derivatives", "Limits", "Integration", "Applications"]
        },
        {
            "courseCode": "MATH240",
            "courseName": "Linear Algebra",
            "department": "Mathematics",
            "description": "Systems of linear equations, matrices, vector spaces, linear transformations, eigenvalues and eigenvectors, orthogonality, applications to data science and machine learning.",
            "credits": 4,
            "level": "200",
            "prerequisites": ["MATH140"],
            "topics": ["Linear Algebra", "Matrices", "Vector Spaces", "Eigenvalues", "Data Science"]
        },
        {
            "courseCode": "ENGL101",
            "courseName": "Academic Writing",
            "department": "English",
            "description": "Academic writing course focusing on critical reading, rhetorical analysis, argumentation, research methods, and documentation styles.",
            "credits": 3,
            "level": "100",
            "prerequisites": [],
            "topics": ["Writing", "Research", "Argumentation", "Critical Thinking"]
        },
        {
            "courseCode": "ENES100",
            "courseName": "Introduction to Engineering Design",
            "department": "Engineering",
            "description": "Introduction to engineering design process, teamwork, project management, technical communication, and hands-on design projects.",
            "credits": 3,
            "level": "100",
            "prerequisites": [],
            "topics": ["Engineering Design", "Teamwork", "Project Management", "Prototyping"]
        },
        {
            "courseCode": "STAT400",
            "courseName": "Applied Probability and Statistics",
            "department": "Statistics",
            "description": "Introduction to probability theory and statistics with applications. Random variables, distributions, hypothesis testing, regression analysis.",
            "credits": 3,
            "level": "400",
            "prerequisites": ["MATH141"],
            "topics": ["Probability", "Statistics", "Hypothesis Testing", "Regression", "Data Analysis"]
        }
    ]
    
    print(f"Indexing {len(sampleCourses)} sample UMD courses...")
    stats = await vectorStoreService.indexCourses(sampleCourses)
    
    print(f"\nIndexing complete!")
    print(f"✅ Successfully indexed: {stats['success']}")
    print(f"❌ Failed: {stats['failed']}")


async def main():
    """Main entry point."""
    
    print("=" * 60)
    print("Pinecone Vector Store - Course Indexing Tool")
    print("=" * 60)
    print()
    
    # Check if Pinecone is enabled
    if not vectorStoreService.pineconeEnabled:
        print("❌ Error: Pinecone is not enabled!")
        print()
        print("To enable Pinecone, add these to your backend/.env file:")
        print("  PINECONE_API_KEY=your-api-key")
        print("  PINECONE_ENVIRONMENT=us-east-1")
        print("  PINECONE_INDEX_NAME=umd-courses")
        print()
        print("Get your API key from: https://www.pinecone.io/")
        return
    
    print("✅ Pinecone is enabled and ready")
    
    # Show current stats
    stats = vectorStoreService.getStats()
    if stats.get('enabled'):
        print(f"Current index: {stats.get('totalVectors', 0)} vectors")
    print()
    
    if len(sys.argv) > 1:
        # Index from file
        filePath = sys.argv[1]
        await indexCoursesFromFile(filePath)
    else:
        # Index sample courses
        print("No file provided, indexing sample courses...")
        print("(Use: python scripts/index_courses.py data/courses.json)")
        print()
        await indexSampleCourses()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nIndexing interrupted by user")
    except Exception as error:
        print(f"\n❌ Error: {error}")
        import traceback
        traceback.print_exc()

