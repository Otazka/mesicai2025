"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """User experience levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TargetRole(str, Enum):
    """Target roles for skill development"""
    JUNIOR_DEVELOPER = "junior_developer"
    MID_LEVEL_DEVELOPER = "mid_level_developer"
    SENIOR_DEVELOPER = "senior_developer"
    BACKEND_DEVELOPER = "backend_developer"
    FRONTEND_DEVELOPER = "frontend_developer"
    FULL_STACK_DEVELOPER = "full_stack_developer"
    DATA_SCIENTIST = "data_scientist"
    DEVOPS_ENGINEER = "devops_engineer"


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message")
    session_id: str = Field(..., description="Session identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str = Field(..., description="Assistant response")
    session_id: str = Field(..., description="Session identifier")
    assessment_in_progress: bool = Field(False, description="Whether assessment is ongoing")
    current_topic: Optional[str] = Field(None, description="Current assessment topic")
    timestamp: datetime = Field(default_factory=datetime.now)


class UserProfile(BaseModel):
    """User profile model"""
    session_id: str = Field(..., description="Session identifier")
    target_role: TargetRole = Field(..., description="Target role")
    experience_level: ExperienceLevel = Field(..., description="Current experience level")
    goals: Optional[List[str]] = Field(None, description="Learning goals")
    created_at: datetime = Field(default_factory=datetime.now)


class AssessmentQuestion(BaseModel):
    """Assessment question model"""
    id: str = Field(..., description="Question identifier")
    topic: str = Field(..., description="Topic (python, oop, algorithms)")
    subtopic: str = Field(..., description="Subtopic")
    question: str = Field(..., description="Question text")
    difficulty: str = Field(..., description="Difficulty level")
    evaluation_criteria: List[str] = Field(..., description="Evaluation criteria")


class AssessmentResponse(BaseModel):
    """Assessment response model"""
    question_id: str = Field(..., description="Question identifier")
    user_answer: str = Field(..., description="User's answer")
    score: Optional[int] = Field(None, description="Score (0-100)")
    feedback: Optional[str] = Field(None, description="Detailed feedback")


class SkillScore(BaseModel):
    """Skill score model"""
    topic: str = Field(..., description="Skill topic")
    subtopic: str = Field(..., description="Skill subtopic")
    score: int = Field(..., description="Score (0-100)")
    confidence: float = Field(..., description="Confidence level (0-1)")


class AssessmentResult(BaseModel):
    """Assessment result model"""
    session_id: str = Field(..., description="Session identifier")
    topic: str = Field(..., description="Assessment topic")
    overall_score: int = Field(..., description="Overall score (0-100)")
    skill_scores: List[SkillScore] = Field(..., description="Individual skill scores")
    strengths: List[str] = Field(..., description="Identified strengths")
    weaknesses: List[str] = Field(..., description="Identified weaknesses")
    recommendations: List[str] = Field(..., description="Learning recommendations")
    completed_at: datetime = Field(default_factory=datetime.now)


class GapAnalysis(BaseModel):
    """Gap analysis model"""
    session_id: str = Field(..., description="Session identifier")
    target_role: TargetRole = Field(..., description="Target role")
    current_skills: Dict[str, int] = Field(..., description="Current skill scores")
    required_skills: Dict[str, int] = Field(..., description="Required skill scores")
    gaps: Dict[str, int] = Field(..., description="Skill gaps")
    priority_areas: List[str] = Field(..., description="Priority improvement areas")
    generated_at: datetime = Field(default_factory=datetime.now)


class LearningObjective(BaseModel):
    """Learning objective model"""
    id: str = Field(..., description="Objective identifier")
    title: str = Field(..., description="Objective title")
    description: str = Field(..., description="Objective description")
    topic: str = Field(..., description="Topic")
    subtopic: str = Field(..., description="Subtopic")
    estimated_time: int = Field(..., description="Estimated time in hours")
    difficulty: str = Field(..., description="Difficulty level")
    prerequisites: List[str] = Field(..., description="Prerequisite objectives")
    resources: List[Dict[str, str]] = Field(..., description="Learning resources")
    roadmap_url: Optional[str] = Field(None, description="Roadmap.sh URL")


class LearningPath(BaseModel):
    """Learning path model"""
    session_id: str = Field(..., description="Session identifier")
    target_role: TargetRole = Field(..., description="Target role")
    total_duration: int = Field(..., description="Total estimated time in hours")
    objectives: List[LearningObjective] = Field(..., description="Learning objectives")
    weekly_breakdown: List[Dict[str, Any]] = Field(..., description="Weekly learning plan")
    generated_at: datetime = Field(default_factory=datetime.now)


class SkillExplanation(BaseModel):
    """Skill explanation model"""
    topic: str = Field(..., description="Skill topic")
    subtopic: str = Field(..., description="Skill subtopic")
    explanation: str = Field(..., description="Detailed explanation")
    examples: List[str] = Field(..., description="Code examples")
    resources: List[Dict[str, str]] = Field(..., description="Additional resources")
    related_skills: List[str] = Field(..., description="Related skills")
