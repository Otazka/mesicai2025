"""
Learning path recommendation service
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from .llm_service import LLMService
from .gap_analysis import GapAnalyzer
from models.schemas import LearningPath, LearningObjective, TargetRole, GapAnalysis

logger = logging.getLogger(__name__)


class LearningPathGenerator:
    """Service for generating personalized learning paths"""
    
    def __init__(self):
        """Initialize learning path generator"""
        self.llm_service = LLMService()
        self.gap_analyzer = GapAnalyzer()
        self.learning_resources = self._load_learning_resources()
        
    def _load_learning_resources(self) -> Dict[str, List[Dict[str, str]]]:
        """Load learning resources for different skills"""
        return {
            "python_basics": [
                {
                    "type": "course",
                    "title": "Python Basics - Codecademy",
                    "url": "https://www.codecademy.com/learn/learn-python-3",
                    "description": "Interactive Python fundamentals course"
                },
                {
                    "type": "book",
                    "title": "Python Crash Course",
                    "url": "https://nostarch.com/pythoncrashcourse2e",
                    "description": "Comprehensive Python introduction"
                },
                {
                    "type": "practice",
                    "title": "Python Exercises - W3Schools",
                    "url": "https://www.w3schools.com/python/python_exercises.asp",
                    "description": "Hands-on Python practice problems"
                }
            ],
            "python_oop": [
                {
                    "type": "course",
                    "title": "Object-Oriented Programming in Python - Coursera",
                    "url": "https://www.coursera.org/learn/python-object-oriented",
                    "description": "Deep dive into Python OOP concepts"
                },
                {
                    "type": "tutorial",
                    "title": "Python OOP Tutorial - Real Python",
                    "url": "https://realpython.com/python3-object-oriented-programming/",
                    "description": "Comprehensive OOP tutorial with examples"
                },
                {
                    "type": "project",
                    "title": "Build a Python Class Library",
                    "url": "https://github.com/trending/python",
                    "description": "Practice OOP by building a class library"
                }
            ],
            "algorithms_sorting": [
                {
                    "type": "course",
                    "title": "Algorithms Specialization - Coursera",
                    "url": "https://www.coursera.org/specializations/algorithms",
                    "description": "Comprehensive algorithms course"
                },
                {
                    "type": "book",
                    "title": "Introduction to Algorithms",
                    "url": "https://mitpress.mit.edu/books/introduction-algorithms",
                    "description": "Classic algorithms textbook"
                },
                {
                    "type": "practice",
                    "title": "LeetCode Sorting Problems",
                    "url": "https://leetcode.com/tag/sorting/",
                    "description": "Practice sorting algorithm problems"
                }
            ],
            "algorithms_searching": [
                {
                    "type": "course",
                    "title": "Data Structures and Algorithms - Udacity",
                    "url": "https://www.udacity.com/course/data-structures-and-algorithms-nanodegree",
                    "description": "Comprehensive DSA course"
                },
                {
                    "type": "tutorial",
                    "title": "Graph Algorithms - GeeksforGeeks",
                    "url": "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/",
                    "description": "Graph algorithms tutorial"
                },
                {
                    "type": "practice",
                    "title": "HackerRank Graph Problems",
                    "url": "https://www.hackerrank.com/domains/algorithms/graph-theory",
                    "description": "Practice graph and search problems"
                }
            ]
        }
    
    async def generate_path(self, gap_analysis: GapAnalysis, user_goals: List[str], experience_level: str) -> LearningPath:
        """Generate a personalized learning path based on gap analysis"""
        try:
            # Use LLM to generate structured learning objectives
            llm_path = await self.llm_service.generate_learning_path(
                gap_analysis.dict(),
                user_goals
            )
            
            # Create learning objectives
            objectives = []
            for obj_data in llm_path.get("objectives", []):
                objective = LearningObjective(
                    id=obj_data.get("id", f"obj_{len(objectives)}"),
                    title=obj_data.get("title", "Learning Objective"),
                    description=obj_data.get("description", ""),
                    topic=obj_data.get("topic", ""),
                    subtopic=obj_data.get("subtopic", ""),
                    estimated_time=obj_data.get("estimated_time", 10),
                    difficulty=obj_data.get("difficulty", "intermediate"),
                    prerequisites=obj_data.get("prerequisites", []),
                    resources=obj_data.get("resources", self._get_default_resources(obj_data.get("topic", ""))),
                    roadmap_url=obj_data.get("roadmap_url")
                )
                objectives.append(objective)
            
            # Create weekly breakdown
            weekly_breakdown = self._create_weekly_breakdown(objectives, experience_level)
            
            # Calculate total duration
            total_duration = sum(obj.estimated_time for obj in objectives)
            
            # Create learning path
            learning_path = LearningPath(
                session_id="",  # Will be set by caller
                target_role=gap_analysis.target_role,
                total_duration=total_duration,
                objectives=objectives,
                weekly_breakdown=weekly_breakdown,
                generated_at=datetime.now()
            )
            
            return learning_path
            
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return self._create_fallback_path(gap_analysis)
    
    def _get_default_resources(self, topic: str) -> List[Dict[str, str]]:
        """Get default resources for a topic"""
        return self.learning_resources.get(topic, [
            {
                "type": "documentation",
                "title": f"{topic.title()} Documentation",
                "url": "https://docs.python.org/3/",
                "description": f"Official documentation for {topic}"
            }
        ])
    
    def _create_weekly_breakdown(self, objectives: List[LearningObjective], experience_level: str) -> List[Dict[str, Any]]:
        """Create a weekly breakdown of learning objectives"""
        # Adjust time estimates based on experience level
        time_multiplier = {
            "beginner": 1.5,
            "intermediate": 1.0,
            "advanced": 0.7
        }.get(experience_level, 1.0)
        
        weekly_breakdown = []
        current_week = 1
        current_week_hours = 0
        max_weekly_hours = 15  # Maximum hours per week
        
        for i, objective in enumerate(objectives):
            adjusted_time = int(objective.estimated_time * time_multiplier)
            
            # If adding this objective would exceed weekly limit, start new week
            if current_week_hours + adjusted_time > max_weekly_hours and current_week_hours > 0:
                current_week += 1
                current_week_hours = 0
            
            # Add objective to current week
            if current_week_hours == 0:
                weekly_breakdown.append({
                    "week": current_week,
                    "focus": objective.topic,
                    "objectives": [],
                    "tasks": [],
                    "estimated_hours": 0,
                    "start_date": (datetime.now() + timedelta(weeks=current_week-1)).strftime("%Y-%m-%d")
                })
            
            weekly_breakdown[-1]["objectives"].append(objective.id)
            weekly_breakdown[-1]["tasks"].append(f"Complete: {objective.title}")
            weekly_breakdown[-1]["estimated_hours"] += adjusted_time
            current_week_hours += adjusted_time
        
        return weekly_breakdown
    
    def _create_fallback_path(self, gap_analysis: GapAnalysis) -> LearningPath:
        """Create a fallback learning path if LLM generation fails"""
        objectives = []
        
        # Create basic objectives based on priority areas
        for i, priority_area in enumerate(gap_analysis.priority_areas[:5]):
            objective = LearningObjective(
                id=f"fallback_obj_{i}",
                title=f"Improve {priority_area}",
                description=f"Focus on developing skills in {priority_area}",
                topic="general",
                subtopic="improvement",
                estimated_time=20,
                difficulty="intermediate",
                prerequisites=[],
                resources=self._get_default_resources("python_basics"),
                roadmap_url=None
            )
            objectives.append(objective)
        
        return LearningPath(
            session_id="",
            target_role=gap_analysis.target_role,
            total_duration=sum(obj.estimated_time for obj in objectives),
            objectives=objectives,
            weekly_breakdown=self._create_weekly_breakdown(objectives, "intermediate"),
            generated_at=datetime.now()
        )
    
    def get_learning_path_summary(self, learning_path: LearningPath) -> Dict[str, Any]:
        """Generate a summary of the learning path"""
        total_weeks = len(learning_path.weekly_breakdown)
        total_hours = learning_path.total_duration
        
        # Calculate difficulty distribution
        difficulty_counts = {}
        for objective in learning_path.objectives:
            difficulty_counts[objective.difficulty] = difficulty_counts.get(objective.difficulty, 0) + 1
        
        # Calculate topic distribution
        topic_counts = {}
        for objective in learning_path.objectives:
            topic_counts[objective.topic] = topic_counts.get(objective.topic, 0) + 1
        
        return {
            "total_duration_weeks": total_weeks,
            "total_duration_hours": total_hours,
            "average_weekly_hours": total_hours / total_weeks if total_weeks > 0 else 0,
            "difficulty_distribution": difficulty_counts,
            "topic_distribution": topic_counts,
            "milestones": [
                {
                    "week": week,
                    "milestone": f"Complete Week {week} objectives",
                    "focus": week_data["focus"]
                }
                for week, week_data in enumerate(learning_path.weekly_breakdown, 1)
            ]
        }
    
    def adapt_path_to_progress(self, learning_path: LearningPath, completed_objectives: List[str]) -> LearningPath:
        """Adapt the learning path based on completed objectives"""
        # Filter out completed objectives
        remaining_objectives = [
            obj for obj in learning_path.objectives
            if obj.id not in completed_objectives
        ]
        
        # Recalculate weekly breakdown
        new_weekly_breakdown = self._create_weekly_breakdown(
            remaining_objectives,
            "intermediate"  # Could be determined from user profile
        )
        
        # Create updated learning path
        updated_path = LearningPath(
            session_id=learning_path.session_id,
            target_role=learning_path.target_role,
            total_duration=sum(obj.estimated_time for obj in remaining_objectives),
            objectives=remaining_objectives,
            weekly_breakdown=new_weekly_breakdown,
            generated_at=datetime.now()
        )
        
        return updated_path
    
    def get_next_objective(self, learning_path: LearningPath, completed_objectives: List[str]) -> Optional[LearningObjective]:
        """Get the next recommended learning objective"""
        # Find objectives that have all prerequisites completed
        available_objectives = []
        
        for objective in learning_path.objectives:
            if objective.id in completed_objectives:
                continue
            
            # Check if all prerequisites are completed
            prerequisites_met = all(
                prereq in completed_objectives
                for prereq in objective.prerequisites
            )
            
            if prerequisites_met:
                available_objectives.append(objective)
        
        # Return the first available objective (could be improved with priority scoring)
        return available_objectives[0] if available_objectives else None
