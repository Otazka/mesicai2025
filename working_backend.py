#!/usr/bin/env python3
"""
Working backend server with full chatbot functionality
"""

import sys
import os
from pathlib import Path
import json
import uuid
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import authentication routes
try:
    from backend.api.auth_routes import router as auth_router
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    print("⚠️  Authentication routes not available - Google OAuth not configured")

# Create FastAPI app
app = FastAPI(
    title="AI Skills Development Chatbot",
    description="An AI-powered chatbot for IT skills assessment and personalized learning paths",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes if available
if AUTH_AVAILABLE:
    app.include_router(auth_router)
    print("✅ Google OAuth authentication routes included")

# Mock data for testing
MOCK_SKILLS = {
    "python_basics": 75,
    "python_oop": 60,
    "python_advanced": 40,
    "algorithms_sorting": 50,
    "algorithms_searching": 45,
    "algorithms_dynamic_programming": 30
}

MOCK_QUESTIONS = [
    {
        "id": "python_basics_1",
        "topic": "python",
        "subtopic": "basics",
        "question": "Explain the difference between a list and a tuple in Python. When would you use each?",
        "difficulty": "beginner",
        "evaluation_criteria": ["understanding of mutability", "knowledge of use cases", "awareness of performance implications"]
    },
    {
        "id": "python_oop_1",
        "topic": "python", 
        "subtopic": "oop",
        "question": "What is the difference between single and multiple inheritance in Python? What is the Method Resolution Order (MRO)?",
        "difficulty": "intermediate",
        "evaluation_criteria": ["understanding of inheritance concepts", "knowledge of MRO", "awareness of diamond problem"]
    },
    {
        "id": "algo_sorting_1",
        "topic": "algorithms",
        "subtopic": "sorting", 
        "question": "Explain the bubble sort algorithm. What is its time complexity? When would you use it?",
        "difficulty": "beginner",
        "evaluation_criteria": ["understanding of algorithm steps", "knowledge of time complexity", "awareness of use cases"]
    }
]

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Skills Development Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/start-assessment")
async def start_assessment(data: dict):
    """Start a new skill assessment"""
    session_id = str(uuid.uuid4())
    target_role = data.get("target_role", "senior_developer")
    experience_level = data.get("experience_level", "intermediate")
    goals = data.get("goals", [])
    
    return {
        "session_id": session_id,
        "message": f"Welcome! I'll help you assess your skills for becoming a {target_role.replace('_', ' ')}. Let's start with Python fundamentals.",
        "question": MOCK_QUESTIONS[0],
        "assessment_started": True,
        "target_role": target_role,
        "experience_level": experience_level,
        "goals": goals
    }

@app.get("/api/questions/{topic}")
async def get_questions(topic: str, count: int = 5):
    """Get assessment questions for a topic"""
    topic_questions = [q for q in MOCK_QUESTIONS if q["topic"] == topic]
    return {"questions": topic_questions[:count]}

@app.post("/api/chat")
async def chat(data: dict):
    """Main chat endpoint"""
    message = data.get("message", "")
    session_id = data.get("session_id", str(uuid.uuid4()))
    
    # Simple response logic
    if "hello" in message.lower() or "hi" in message.lower():
        response = "Hello! I'm here to help you develop your IT skills. How can I assist you today?"
    elif "assessment" in message.lower():
        response = "I can help you with a skill assessment! Let's start by evaluating your Python, OOP, and Algorithms knowledge. Would you like to begin?"
    elif "learning path" in message.lower() or "roadmap" in message.lower():
        response = "I can create a personalized learning path for you! First, let's complete a skill assessment to identify your strengths and areas for improvement."
    elif "explain" in message.lower():
        response = "I'd be happy to explain any IT concept! What specific topic would you like me to explain? (e.g., Python OOP, sorting algorithms, etc.)"
    else:
        response = "I'm here to help with your IT skills development! I can assist with skill assessments, gap analysis, learning paths, and explaining technical concepts. What would you like to work on?"
    
    return {
        "message": response,
        "session_id": session_id,
        "assessment_in_progress": False,
        "current_topic": None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analyze-gaps")
async def analyze_gaps(data: dict):
    """Analyze skill gaps for a user"""
    session_id = data.get("session_id", str(uuid.uuid4()))
    current_skills = data.get("current_skills", MOCK_SKILLS)
    target_role = data.get("target_role", "senior_developer")
    
    # Mock gap analysis
    required_skills = {
        "python_basics": 90,
        "python_oop": 85,
        "python_advanced": 80,
        "algorithms_sorting": 75,
        "algorithms_searching": 80,
        "algorithms_dynamic_programming": 70
    }
    
    gaps = {}
    for skill, required in required_skills.items():
        current = current_skills.get(skill, 0)
        gaps[skill] = max(0, required - current)
    
    priority_areas = []
    for skill, gap in sorted(gaps.items(), key=lambda x: x[1], reverse=True):
        if gap > 0:
            priority_areas.append(f"{skill.replace('_', ' ').title()} (Gap: {gap} points)")
    
    return {
        "session_id": session_id,
        "target_role": target_role,
        "current_skills": current_skills,
        "required_skills": required_skills,
        "gaps": gaps,
        "priority_areas": priority_areas[:3],
        "generated_at": datetime.now().isoformat()
    }

@app.get("/api/learning-path/{session_id}")
async def get_learning_path(session_id: str):
    """Get personalized learning path for a user"""
    return {
        "session_id": session_id,
        "target_role": "senior_developer",
        "total_duration": 120,
        "objectives": [
            {
                "id": "obj_1",
                "title": "Master Python OOP Concepts",
                "description": "Learn classes, inheritance, and polymorphism",
                "topic": "python",
                "subtopic": "oop",
                "estimated_time": 20,
                "difficulty": "intermediate",
                "prerequisites": [],
                "resources": [
                    {"type": "course", "title": "Python OOP Course", "url": "https://example.com/oop-course"},
                    {"type": "practice", "title": "OOP Exercises", "url": "https://example.com/oop-exercises"}
                ],
                "roadmap_url": "https://roadmap.sh/python"
            },
            {
                "id": "obj_2",
                "title": "Learn Sorting Algorithms",
                "description": "Understand and implement various sorting algorithms",
                "topic": "algorithms",
                "subtopic": "sorting",
                "estimated_time": 15,
                "difficulty": "intermediate",
                "prerequisites": ["obj_1"],
                "resources": [
                    {"type": "tutorial", "title": "Sorting Algorithms Guide", "url": "https://example.com/sorting-guide"},
                    {"type": "practice", "title": "Algorithm Problems", "url": "https://example.com/algorithm-problems"}
                ],
                "roadmap_url": "https://roadmap.sh/algorithms"
            }
        ],
        "weekly_breakdown": [
            {
                "week": 1,
                "focus": "Python OOP",
                "objectives": ["obj_1"],
                "tasks": ["Study classes and objects", "Practice inheritance"],
                "estimated_hours": 15,
                "start_date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "week": 2,
                "focus": "Algorithms",
                "objectives": ["obj_2"],
                "tasks": ["Learn sorting algorithms", "Implement solutions"],
                "estimated_hours": 12,
                "start_date": (datetime.now().replace(day=datetime.now().day + 7)).strftime("%Y-%m-%d")
            }
        ],
        "generated_at": datetime.now().isoformat()
    }

@app.post("/api/explain-skill")
async def explain_skill(data: dict):
    """Get detailed explanation of a skill"""
    topic = data.get("topic", "python")
    subtopic = data.get("subtopic", "oop")
    user_level = data.get("user_level", "intermediate")
    
    explanations = {
        "python": {
            "oop": {
                "explanation": "Object-Oriented Programming (OOP) in Python is a programming paradigm that uses objects and classes to organize code. It helps create reusable and maintainable code by grouping related data and functions together.",
                "examples": [
                    "Classes define the structure of objects",
                    "Objects are instances of classes",
                    "Inheritance allows classes to inherit properties from other classes",
                    "Polymorphism enables objects of different types to be treated uniformly"
                ],
                "code_snippets": [
                    "class Person:\n    def __init__(self, name):\n        self.name = name\n\n    def greet(self):\n        return f'Hello, I am {self.name}'"
                ],
                "applications": ["Building user interfaces", "Creating data models", "Organizing complex systems"],
                "best_practices": ["Use meaningful class names", "Keep classes focused on single responsibility", "Use composition over inheritance when possible"],
                "related_concepts": ["Classes", "Inheritance", "Polymorphism", "Encapsulation"]
            }
        },
        "algorithms": {
            "sorting": {
                "explanation": "Sorting algorithms are methods for arranging data in a particular order, typically numerical or lexicographical. They are fundamental to computer science and used in many applications.",
                "examples": [
                    "Bubble Sort: Simple but inefficient, good for learning",
                    "Quick Sort: Efficient average-case performance",
                    "Merge Sort: Guaranteed O(n log n) performance"
                ],
                "code_snippets": [
                    "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]"
                ],
                "applications": ["Database indexing", "Search algorithms", "Data analysis"],
                "best_practices": ["Choose the right algorithm for your data size", "Consider stability requirements", "Understand time and space complexity"],
                "related_concepts": ["Time Complexity", "Space Complexity", "Stability", "Comparison-based sorting"]
            }
        }
    }
    
    topic_data = explanations.get(topic, {}).get(subtopic, {})
    
    return {
        "topic": topic,
        "subtopic": subtopic,
        "explanation": topic_data.get("explanation", f"Explanation for {topic} - {subtopic}"),
        "examples": topic_data.get("examples", []),
        "resources": [
            {"type": "documentation", "title": f"{topic.title()} Documentation", "url": f"https://docs.python.org/3/"},
            {"type": "tutorial", "title": f"{subtopic.title()} Tutorial", "url": "https://example.com/tutorial"}
        ],
        "related_skills": topic_data.get("related_concepts", [])
    }

@app.get("/api/user-profile/{session_id}")
async def get_user_profile(session_id: str):
    """Get user profile"""
    return {
        "session_id": session_id,
        "target_role": "senior_developer",
        "experience_level": "intermediate",
        "goals": ["Master Python OOP", "Learn algorithms", "Become a senior developer"],
        "created_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting AI Skills Development Chatbot Backend...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("\n🎯 Available endpoints:")
    print("  POST /api/start-assessment - Start skill assessment")
    print("  POST /api/chat - Chat with the AI assistant")
    print("  POST /api/analyze-gaps - Analyze skill gaps")
    print("  GET  /api/learning-path/{session_id} - Get learning path")
    print("  POST /api/explain-skill - Explain a skill")
    print("  GET  /api/questions/{topic} - Get assessment questions")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
