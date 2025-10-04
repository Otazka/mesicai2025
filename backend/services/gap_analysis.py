"""
Gap analysis service for identifying skill gaps and improvement areas
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .llm_service import LLMService
from models.schemas import GapAnalysis, TargetRole, ExperienceLevel

logger = logging.getLogger(__name__)


class GapAnalyzer:
    """Service for analyzing skill gaps"""
    
    def __init__(self):
        """Initialize gap analyzer"""
        self.llm_service = LLMService()
        self.role_requirements = self._load_role_requirements()
        
    def _load_role_requirements(self) -> Dict[str, Dict[str, int]]:
        """Load role requirements from configuration"""
        return {
            "junior_developer": {
                "python_basics": 70,
                "python_oop": 50,
                "python_advanced": 30,
                "algorithms_sorting": 40,
                "algorithms_searching": 50,
                "algorithms_dynamic_programming": 20
            },
            "mid_level_developer": {
                "python_basics": 85,
                "python_oop": 75,
                "python_advanced": 60,
                "algorithms_sorting": 70,
                "algorithms_searching": 75,
                "algorithms_dynamic_programming": 50
            },
            "senior_developer": {
                "python_basics": 95,
                "python_oop": 90,
                "algorithms_sorting": 85,
                "algorithms_searching": 90,
                "algorithms_dynamic_programming": 80
            },
            "backend_developer": {
                "python_basics": 90,
                "python_oop": 85,
                "python_advanced": 80,
                "algorithms_sorting": 70,
                "algorithms_searching": 75,
                "algorithms_dynamic_programming": 60
            },
            "data_scientist": {
                "python_basics": 85,
                "python_oop": 70,
                "python_advanced": 75,
                "algorithms_sorting": 80,
                "algorithms_searching": 85,
                "algorithms_dynamic_programming": 90
            }
        }
    
    async def analyze(self, current_skills: Dict[str, int], target_role: TargetRole, experience_level: ExperienceLevel) -> GapAnalysis:
        """Analyze skill gaps for a target role"""
        try:
            # Get required skills for target role
            required_skills = self.role_requirements.get(target_role.value, {})
            
            # Calculate gaps
            gaps = {}
            for skill, required_score in required_skills.items():
                current_score = current_skills.get(skill, 0)
                gap = max(0, required_score - current_score)
                gaps[skill] = gap
            
            # Use LLM to analyze gaps and provide insights
            llm_analysis = await self.llm_service.analyze_skill_gaps(current_skills, target_role.value)
            
            # Create gap analysis result
            result = GapAnalysis(
                session_id="",  # Will be set by caller
                target_role=target_role,
                current_skills=current_skills,
                required_skills=required_skills,
                gaps=gaps,
                priority_areas=llm_analysis.get("priority_areas", self._calculate_priority_areas(gaps)),
                generated_at=datetime.now()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing gaps: {e}")
            return GapAnalysis(
                session_id="",
                target_role=target_role,
                current_skills=current_skills,
                required_skills={},
                gaps={},
                priority_areas=[],
                generated_at=datetime.now()
            )
    
    def _calculate_priority_areas(self, gaps: Dict[str, int]) -> List[str]:
        """Calculate priority areas based on gap sizes"""
        # Sort gaps by size (largest first)
        sorted_gaps = sorted(gaps.items(), key=lambda x: x[1], reverse=True)
        
        # Map skill keys to human-readable names
        skill_names = {
            "python_basics": "Python Fundamentals",
            "python_oop": "Object-Oriented Programming",
            "python_advanced": "Advanced Python Features",
            "algorithms_sorting": "Sorting Algorithms",
            "algorithms_searching": "Search Algorithms",
            "algorithms_dynamic_programming": "Dynamic Programming"
        }
        
        # Return top 3 priority areas
        priority_areas = []
        for skill_key, gap_size in sorted_gaps[:3]:
            if gap_size > 0:  # Only include areas with actual gaps
                skill_name = skill_names.get(skill_key, skill_key)
                priority_areas.append(f"{skill_name} (Gap: {gap_size} points)")
        
        return priority_areas
    
    def get_gap_summary(self, gap_analysis: GapAnalysis) -> Dict[str, Any]:
        """Generate a summary of the gap analysis"""
        total_gaps = sum(gap_analysis.gaps.values())
        num_skills_with_gaps = len([gap for gap in gap_analysis.gaps.values() if gap > 0])
        
        # Calculate gap severity
        if total_gaps > 200:
            severity = "High"
        elif total_gaps > 100:
            severity = "Medium"
        else:
            severity = "Low"
        
        return {
            "total_gap": total_gaps,
            "skills_with_gaps": num_skills_with_gaps,
            "severity": severity,
            "priority_areas": gap_analysis.priority_areas,
            "estimated_improvement_time": self._estimate_improvement_time(total_gaps)
        }
    
    def _estimate_improvement_time(self, total_gap: int) -> str:
        """Estimate time needed to close skill gaps"""
        if total_gap > 200:
            return "6-12 months"
        elif total_gap > 100:
            return "3-6 months"
        elif total_gap > 50:
            return "1-3 months"
        else:
            return "2-4 weeks"
    
    def get_skill_importance_explanation(self, skill: str, target_role: TargetRole) -> str:
        """Get explanation of why a skill is important for a role"""
        explanations = {
            "python_basics": {
                "junior_developer": "Essential for writing clean, maintainable code and understanding Python syntax",
                "mid_level_developer": "Critical for code quality, debugging, and mentoring junior developers",
                "senior_developer": "Fundamental for architecture decisions and code review processes",
                "backend_developer": "Core requirement for API development and server-side programming",
                "data_scientist": "Essential for data manipulation, analysis, and scientific computing"
            },
            "python_oop": {
                "junior_developer": "Important for understanding code organization and design patterns",
                "mid_level_developer": "Critical for building scalable applications and following best practices",
                "senior_developer": "Essential for system design and architectural decisions",
                "backend_developer": "Core for building maintainable APIs and service architectures",
                "data_scientist": "Useful for organizing data processing pipelines and creating reusable components"
            },
            "algorithms_sorting": {
                "junior_developer": "Important for understanding data processing and optimization",
                "mid_level_developer": "Critical for performance optimization and system efficiency",
                "senior_developer": "Essential for making informed decisions about data structures and algorithms",
                "backend_developer": "Important for database optimization and data processing",
                "data_scientist": "Critical for data preprocessing and analysis pipeline optimization"
            }
        }
        
        return explanations.get(skill, {}).get(target_role.value, "Important skill for professional development")
    
    def create_improvement_roadmap(self, gap_analysis: GapAnalysis) -> Dict[str, Any]:
        """Create a structured improvement roadmap"""
        roadmap = {
            "phases": [],
            "total_estimated_time": 0,
            "milestones": []
        }
        
        # Phase 1: Foundation (smallest gaps first)
        foundation_skills = []
        for skill, gap in gap_analysis.gaps.items():
            if gap <= 20:
                foundation_skills.append(skill)
        
        if foundation_skills:
            roadmap["phases"].append({
                "name": "Foundation Building",
                "skills": foundation_skills,
                "estimated_time": len(foundation_skills) * 2,  # 2 weeks per skill
                "description": "Build solid foundation in core areas"
            })
        
        # Phase 2: Core Development (medium gaps)
        core_skills = []
        for skill, gap in gap_analysis.gaps.items():
            if 20 < gap <= 40:
                core_skills.append(skill)
        
        if core_skills:
            roadmap["phases"].append({
                "name": "Core Development",
                "skills": core_skills,
                "estimated_time": len(core_skills) * 4,  # 4 weeks per skill
                "description": "Develop core competencies for the role"
            })
        
        # Phase 3: Advanced Mastery (largest gaps)
        advanced_skills = []
        for skill, gap in gap_analysis.gaps.items():
            if gap > 40:
                advanced_skills.append(skill)
        
        if advanced_skills:
            roadmap["phases"].append({
                "name": "Advanced Mastery",
                "skills": advanced_skills,
                "estimated_time": len(advanced_skills) * 6,  # 6 weeks per skill
                "description": "Achieve mastery in advanced areas"
            })
        
        # Calculate total time
        roadmap["total_estimated_time"] = sum(phase["estimated_time"] for phase in roadmap["phases"])
        
        # Create milestones
        roadmap["milestones"] = [
            {
                "name": "Foundation Complete",
                "time": roadmap["phases"][0]["estimated_time"] if roadmap["phases"] else 0,
                "description": "Core foundation skills developed"
            },
            {
                "name": "Core Competencies",
                "time": sum(phase["estimated_time"] for phase in roadmap["phases"][:2]) if len(roadmap["phases"]) > 1 else 0,
                "description": "Essential role skills acquired"
            },
            {
                "name": "Role Ready",
                "time": roadmap["total_estimated_time"],
                "description": "Ready for target role responsibilities"
            }
        ]
        
        return roadmap
