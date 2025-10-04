"""
Streamlit frontend for AI Skills Development Chatbot
"""

import streamlit as st
import requests
import json
import uuid
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="AI Skills Development Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000/api"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "assessment_results" not in st.session_state:
    st.session_state.assessment_results = []
if "learning_path" not in st.session_state:
    st.session_state.learning_path = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"


def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API request to backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return {}


def render_sidebar():
    """Render sidebar with navigation and user info"""
    st.sidebar.title("🤖 AI Skills Bot")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigate",
        ["Home", "Chat", "Assessment", "Learning Path", "Skill Analysis"]
    )
    st.session_state.current_page = page.lower().replace(" ", "_")
    
    # User profile section
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Profile")
    
    if st.session_state.user_profile:
        st.sidebar.write(f"**Target Role:** {st.session_state.user_profile['target_role']}")
        st.sidebar.write(f"**Experience:** {st.session_state.user_profile['experience_level']}")
        if st.sidebar.button("Reset Profile"):
            st.session_state.user_profile = None
            st.session_state.chat_history = []
            st.session_state.assessment_results = []
            st.session_state.learning_path = None
            st.rerun()
    else:
        st.sidebar.write("No profile set")
    
    # Quick actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Quick Actions")
    
    if st.sidebar.button("Start Assessment"):
        st.session_state.current_page = "assessment"
        st.rerun()
    
    if st.sidebar.button("View Learning Path"):
        st.session_state.current_page = "learning_path"
        st.rerun()
    
    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


def render_home_page():
    """Render home page"""
    st.title("🎯 AI-Powered IT Skills Development")
    st.markdown("Welcome to your personalized IT skills development assistant!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 What I Can Do")
        st.markdown("""
        - **Skill Assessment**: Evaluate your Python, OOP, and Algorithms knowledge
        - **Gap Analysis**: Identify areas for improvement based on your target role
        - **Learning Paths**: Generate personalized roadmaps with resources
        - **Concept Explanation**: Get detailed explanations of technical topics
        - **Progress Tracking**: Monitor your learning journey
        """)
    
    with col2:
        st.subheader("🎯 Get Started")
        
        if not st.session_state.user_profile:
            st.info("👆 Set up your profile in the sidebar to get started!")
            
            with st.form("profile_setup"):
                target_role = st.selectbox(
                    "Target Role",
                    ["junior_developer", "mid_level_developer", "senior_developer", 
                     "backend_developer", "frontend_developer", "data_scientist"]
                )
                experience_level = st.selectbox(
                    "Experience Level",
                    ["beginner", "intermediate", "advanced"]
                )
                goals = st.text_area(
                    "Learning Goals (optional)",
                    placeholder="e.g., Master Python OOP, Learn algorithms, Build web apps"
                )
                
                if st.form_submit_button("Create Profile"):
                    # Create user profile
                    data = {
                        "session_id": st.session_state.session_id,
                        "target_role": target_role,
                        "experience_level": experience_level,
                        "goals": [goal.strip() for goal in goals.split(",") if goal.strip()]
                    }
                    
                    result = make_api_request("/start-assessment", "POST", data)
                    if result:
                        st.session_state.user_profile = {
                            "target_role": target_role,
                            "experience_level": experience_level,
                            "goals": data["goals"]
                        }
                        st.success("Profile created successfully!")
                        st.rerun()
        else:
            st.success("✅ Profile is set up!")
            st.write(f"**Target:** {st.session_state.user_profile['target_role']}")
            st.write(f"**Level:** {st.session_state.user_profile['experience_level']}")
            
            if st.button("Start Skill Assessment", type="primary"):
                st.session_state.current_page = "assessment"
                st.rerun()
    
    # Demo section
    st.markdown("---")
    st.subheader("🎬 Demo Scenario")
    st.markdown("""
    **Try this flow:**
    1. Set up your profile (target role: Senior Python Developer)
    2. Complete a skill assessment
    3. View your gap analysis
    4. Get a personalized learning path
    5. Ask questions about specific concepts
    """)


def render_chat_page():
    """Render chat interface"""
    st.title("💬 Chat with AI Assistant")
    
    # Chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI:** {message['content']}")
    
    # Chat input
    st.markdown("---")
    
    if not st.session_state.user_profile:
        st.warning("Please set up your profile first!")
        return
    
    user_input = st.text_input("Type your message:", key="chat_input")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        send_button = st.button("Send", type="primary")
    
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Make API request
        data = {
            "message": user_input,
            "session_id": st.session_state.session_id,
            "context": {}
        }
        
        with st.spinner("AI is thinking..."):
            response = make_api_request("/chat", "POST", data)
        
        if response:
            # Add AI response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["message"],
                "timestamp": response["timestamp"]
            })
            
            # Clear input and rerun
            if "chat_input" in st.session_state:
                del st.session_state.chat_input
            st.rerun()


def render_assessment_page():
    """Render assessment interface"""
    st.title("📝 Skill Assessment")
    
    if not st.session_state.user_profile:
        st.warning("Please set up your profile first!")
        return
    
    # Assessment form
    with st.form("assessment_form"):
        st.subheader("Python Fundamentals")
        
        # Sample questions (in a real app, these would come from the API)
        questions = [
            {
                "id": "python_basics_1",
                "question": "Explain the difference between a list and a tuple in Python. When would you use each?",
                "difficulty": "beginner"
            },
            {
                "id": "python_oop_1", 
                "question": "What is the difference between single and multiple inheritance in Python? What is the Method Resolution Order (MRO)?",
                "difficulty": "intermediate"
            },
            {
                "id": "algo_sorting_1",
                "question": "Explain the bubble sort algorithm. What is its time complexity? When would you use it?",
                "difficulty": "beginner"
            }
        ]
        
        answers = {}
        for i, q in enumerate(questions):
            st.markdown(f"**Question {i+1}:** {q['question']}")
            answers[q['id']] = st.text_area(
                f"Your answer:",
                key=f"answer_{i}",
                height=100
            )
            st.markdown("---")
        
        if st.form_submit_button("Submit Assessment", type="primary"):
            # Process assessment (simplified)
            st.success("Assessment submitted! Analyzing your responses...")
            
            # Simulate assessment results
            st.session_state.assessment_results = [
                {
                    "topic": "python",
                    "overall_score": 75,
                    "skill_scores": [
                        {"subtopic": "basics", "score": 80},
                        {"subtopic": "oop", "score": 70}
                    ]
                },
                {
                    "topic": "algorithms",
                    "overall_score": 65,
                    "skill_scores": [
                        {"subtopic": "sorting", "score": 60},
                        {"subtopic": "searching", "score": 70}
                    ]
                }
            ]
            
            st.session_state.current_page = "skill_analysis"
            st.rerun()


def render_skill_analysis_page():
    """Render skill analysis and visualization"""
    st.title("📊 Skill Analysis")
    
    if not st.session_state.assessment_results:
        st.warning("No assessment results available. Please complete an assessment first.")
        return
    
    # Skill radar chart
    st.subheader("Skill Overview")
    
    # Prepare data for radar chart
    categories = []
    values = []
    
    for result in st.session_state.assessment_results:
        for skill in result["skill_scores"]:
            categories.append(f"{result['topic']} - {skill['subtopic']}")
            values.append(skill["score"])
    
    if categories and values:
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Your Skills'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Skill Assessment Results"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results
    st.subheader("Detailed Results")
    
    for result in st.session_state.assessment_results:
        with st.expander(f"{result['topic'].title()} - Score: {result['overall_score']}/100"):
            for skill in result["skill_scores"]:
                st.write(f"**{skill['subtopic']}:** {skill['score']}/100")
                
                # Progress bar
                progress = skill['score'] / 100
                st.progress(progress)
    
    # Gap analysis button
    if st.button("Analyze Skill Gaps", type="primary"):
        st.session_state.current_page = "learning_path"
        st.rerun()


def render_learning_path_page():
    """Render learning path interface"""
    st.title("🗺️ Learning Path")
    
    if not st.session_state.user_profile:
        st.warning("Please set up your profile first!")
        return
    
    # Generate learning path if not exists
    if not st.session_state.learning_path:
        with st.spinner("Generating your personalized learning path..."):
            # Simulate learning path generation
            st.session_state.learning_path = {
                "total_duration": 120,
                "objectives": [
                    {
                        "id": "obj_1",
                        "title": "Master Python OOP Concepts",
                        "description": "Learn classes, inheritance, and polymorphism",
                        "estimated_time": 20,
                        "difficulty": "intermediate",
                        "resources": [
                            {"type": "course", "title": "Python OOP Course", "url": "#"},
                            {"type": "practice", "title": "OOP Exercises", "url": "#"}
                        ]
                    },
                    {
                        "id": "obj_2", 
                        "title": "Learn Sorting Algorithms",
                        "description": "Understand and implement various sorting algorithms",
                        "estimated_time": 15,
                        "difficulty": "intermediate",
                        "resources": [
                            {"type": "tutorial", "title": "Sorting Algorithms Guide", "url": "#"},
                            {"type": "practice", "title": "Algorithm Problems", "url": "#"}
                        ]
                    }
                ],
                "weekly_breakdown": [
                    {
                        "week": 1,
                        "focus": "Python OOP",
                        "objectives": ["obj_1"],
                        "tasks": ["Study classes and objects", "Practice inheritance"],
                        "estimated_hours": 15
                    },
                    {
                        "week": 2,
                        "focus": "Algorithms",
                        "objectives": ["obj_2"],
                        "tasks": ["Learn sorting algorithms", "Implement solutions"],
                        "estimated_hours": 12
                    }
                ]
            }
    
    # Display learning path
    learning_path = st.session_state.learning_path
    
    st.subheader("📋 Learning Objectives")
    st.write(f"**Total Duration:** {learning_path['total_duration']} hours")
    
    for obj in learning_path["objectives"]:
        with st.expander(f"{obj['title']} ({obj['estimated_time']} hours)"):
            st.write(obj["description"])
            st.write(f"**Difficulty:** {obj['difficulty']}")
            
            st.write("**Resources:**")
            for resource in obj["resources"]:
                st.write(f"- {resource['type'].title()}: {resource['title']}")
    
    st.subheader("📅 Weekly Breakdown")
    
    for week in learning_path["weekly_breakdown"]:
        with st.expander(f"Week {week['week']}: {week['focus']} ({week['estimated_hours']} hours)"):
            st.write("**Objectives:**")
            for obj_id in week["objectives"]:
                obj = next((o for o in learning_path["objectives"] if o["id"] == obj_id), None)
                if obj:
                    st.write(f"- {obj['title']}")
            
            st.write("**Tasks:**")
            for task in week["tasks"]:
                st.write(f"- {task}")
    
    # Progress tracking
    st.subheader("📈 Progress Tracking")
    
    completed_objectives = st.multiselect(
        "Mark completed objectives:",
        options=[obj["id"] for obj in learning_path["objectives"]],
        default=[]
    )
    
    if completed_objectives:
        progress = len(completed_objectives) / len(learning_path["objectives"])
        st.progress(progress)
        st.write(f"Progress: {len(completed_objectives)}/{len(learning_path['objectives'])} objectives completed")


def main():
    """Main application"""
    render_sidebar()
    
    # Route to appropriate page
    if st.session_state.current_page == "home":
        render_home_page()
    elif st.session_state.current_page == "chat":
        render_chat_page()
    elif st.session_state.current_page == "assessment":
        render_assessment_page()
    elif st.session_state.current_page == "learning_path":
        render_learning_path_page()
    elif st.session_state.current_page == "skill_analysis":
        render_skill_analysis_page()
    else:
        render_home_page()


if __name__ == "__main__":
    main()
