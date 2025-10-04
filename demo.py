#!/usr/bin/env python3
"""
Demo script for the AI Skills Development Chatbot
"""

import requests
import json
import time
import uuid
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api"
DEMO_SESSION_ID = str(uuid.uuid4())

def make_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Make API request"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return {}
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend is running (python run_backend.py)")
        return {}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def demo_assessment_flow():
    """Demonstrate the assessment flow"""
    print("🎯 Demo: Skill Assessment Flow")
    print("=" * 40)
    
    # 1. Start assessment
    print("1. Starting skill assessment...")
    assessment_data = {
        "session_id": DEMO_SESSION_ID,
        "target_role": "senior_developer",
        "experience_level": "intermediate",
        "goals": ["Master Python OOP", "Learn advanced algorithms", "Become a senior developer"]
    }
    
    result = make_request("/start-assessment", "POST", assessment_data)
    if result:
        print(f"✅ Assessment started: {result.get('message', '')}")
        print(f"📝 First question: {result.get('question', {}).get('question', 'N/A')}")
    else:
        print("❌ Failed to start assessment")
        return
    
    # 2. Simulate answering questions
    print("\n2. Simulating user responses...")
    
    sample_answers = [
        "Lists are mutable and can be modified after creation, while tuples are immutable. Lists use square brackets [] and tuples use parentheses (). I would use lists when I need to modify the data, and tuples when I want to ensure data integrity.",
        "Single inheritance allows a class to inherit from one parent class, while multiple inheritance allows a class to inherit from multiple parent classes. The Method Resolution Order (MRO) determines the order in which Python searches for methods in the inheritance hierarchy, especially important in multiple inheritance to avoid ambiguity.",
        "Bubble sort is a simple sorting algorithm that repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order. It has O(n²) time complexity in the worst case. It's mainly used for educational purposes or when dealing with very small datasets."
    ]
    
    for i, answer in enumerate(sample_answers, 1):
        print(f"   Answer {i}: {answer[:100]}...")
        time.sleep(1)  # Simulate thinking time
    
    print("✅ Assessment responses simulated")
    
    # 3. Get assessment results
    print("\n3. Retrieving assessment results...")
    results = make_request(f"/assessment-results/{DEMO_SESSION_ID}")
    if results:
        print(f"✅ Retrieved {len(results)} assessment results")
        for result in results:
            print(f"   📊 {result.get('topic', 'Unknown')}: {result.get('overall_score', 0)}/100")
    else:
        print("❌ No assessment results found")

def demo_chat_flow():
    """Demonstrate the chat flow"""
    print("\n💬 Demo: Chat Flow")
    print("=" * 40)
    
    # Sample chat messages
    chat_messages = [
        "Hello! I want to become a senior Python developer",
        "Can you explain Python inheritance?",
        "What are the key differences between lists and tuples?",
        "How can I improve my algorithm skills?"
    ]
    
    for i, message in enumerate(chat_messages, 1):
        print(f"{i}. User: {message}")
        
        chat_data = {
            "message": message,
            "session_id": DEMO_SESSION_ID,
            "context": {}
        }
        
        response = make_request("/chat", "POST", chat_data)
        if response:
            print(f"   AI: {response.get('message', 'No response')}")
        else:
            print("   AI: [Error getting response]")
        
        time.sleep(1)  # Simulate conversation flow

def demo_gap_analysis():
    """Demonstrate gap analysis"""
    print("\n📊 Demo: Gap Analysis")
    print("=" * 40)
    
    # Simulate current skills
    current_skills = {
        "python_basics": 75,
        "python_oop": 60,
        "python_advanced": 40,
        "algorithms_sorting": 50,
        "algorithms_searching": 45,
        "algorithms_dynamic_programming": 30
    }
    
    print("Current skills:")
    for skill, score in current_skills.items():
        print(f"   {skill}: {score}/100")
    
    # Perform gap analysis
    gap_data = {
        "session_id": DEMO_SESSION_ID,
        "current_skills": current_skills
    }
    
    result = make_request("/analyze-gaps", "POST", gap_data)
    if result:
        print(f"\n✅ Gap analysis completed")
        print(f"🎯 Target role: {result.get('target_role', 'Unknown')}")
        print(f"📈 Priority areas: {', '.join(result.get('priority_areas', []))}")
        
        gaps = result.get('gaps', {})
        if gaps:
            print("\nSkill gaps:")
            for skill, gap in gaps.items():
                if gap > 0:
                    print(f"   {skill}: {gap} points gap")
    else:
        print("❌ Gap analysis failed")

def demo_learning_path():
    """Demonstrate learning path generation"""
    print("\n🗺️ Demo: Learning Path Generation")
    print("=" * 40)
    
    result = make_request(f"/learning-path/{DEMO_SESSION_ID}")
    if result:
        print(f"✅ Learning path generated")
        print(f"⏱️ Total duration: {result.get('total_duration', 0)} hours")
        print(f"🎯 Target role: {result.get('target_role', 'Unknown')}")
        
        objectives = result.get('objectives', [])
        print(f"\n📋 Learning objectives ({len(objectives)}):")
        for i, obj in enumerate(objectives[:3], 1):  # Show first 3
            print(f"   {i}. {obj.get('title', 'Unknown')} ({obj.get('estimated_time', 0)} hours)")
        
        weekly_breakdown = result.get('weekly_breakdown', [])
        print(f"\n📅 Weekly breakdown ({len(weekly_breakdown)} weeks):")
        for week in weekly_breakdown[:2]:  # Show first 2 weeks
            print(f"   Week {week.get('week', '?')}: {week.get('focus', 'Unknown')} ({week.get('estimated_hours', 0)} hours)")
    else:
        print("❌ Learning path generation failed")

def demo_skill_explanation():
    """Demonstrate skill explanation"""
    print("\n📚 Demo: Skill Explanation")
    print("=" * 40)
    
    # Request explanation for Python OOP
    result = make_request("/explain-skill", "POST", {
        "topic": "python",
        "subtopic": "oop",
        "user_level": "intermediate"
    })
    
    if result:
        print(f"✅ Skill explanation generated")
        print(f"📖 Topic: {result.get('topic', 'Unknown')} - {result.get('subtopic', 'Unknown')}")
        print(f"📝 Explanation: {result.get('explanation', 'No explanation')[:200]}...")
        
        examples = result.get('examples', [])
        if examples:
            print(f"\n💡 Examples ({len(examples)}):")
            for i, example in enumerate(examples[:2], 1):  # Show first 2
                print(f"   {i}. {example[:100]}...")
        
        related_skills = result.get('related_skills', [])
        if related_skills:
            print(f"\n🔗 Related skills: {', '.join(related_skills[:3])}")
    else:
        print("❌ Skill explanation failed")

def main():
    """Main demo function"""
    print("🤖 AI Skills Development Chatbot - Demo")
    print("=" * 50)
    print(f"Session ID: {DEMO_SESSION_ID}")
    print(f"API Base URL: {API_BASE_URL}")
    print()
    
    # Check if backend is running
    health_check = make_request("/health")
    if not health_check:
        print("❌ Backend is not running!")
        print("Please start the backend with: python run_backend.py")
        return
    
    print("✅ Backend is running")
    
    # Run demos
    try:
        demo_assessment_flow()
        demo_chat_flow()
        demo_gap_analysis()
        demo_learning_path()
        demo_skill_explanation()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\nTo see the full application:")
        print("1. Start the frontend: python run_frontend.py")
        print("2. Open http://localhost:8501 in your browser")
        print("3. Try the interactive features!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")

if __name__ == "__main__":
    main()
