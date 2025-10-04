"""
Skill assessment service for evaluating user responses
"""

import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .llm_service import LLMService
from models.schemas import AssessmentQuestion, AssessmentResponse, SkillScore, AssessmentResult

logger = logging.getLogger(__name__)


class SkillAssessor:
    """Service for conducting skill assessments"""
    
    def __init__(self):
        """Initialize skill assessor"""
        self.llm_service = LLMService()
        self.questions = self._load_questions()
        self.skill_taxonomy = self._load_skill_taxonomy()
        
    def _load_questions(self) -> Dict[str, Any]:
        """Load assessment questions from JSON file"""
        try:
            with open("backend/data/questions.json", "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading questions: {e}")
            return {}
    
    def _load_skill_taxonomy(self) -> Dict[str, Any]:
        """Load skill taxonomy from JSON file"""
        try:
            with open("backend/data/skill_taxonomy.json", "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading skill taxonomy: {e}")
            return {}
    
    def get_assessment_questions(self, topic: str, count: int = 5) -> List[AssessmentQuestion]:
        """Get random assessment questions for a topic"""
        if topic not in self.questions:
            return []
        
        topic_questions = []
        for subtopic, questions in self.questions[topic].items():
            topic_questions.extend(questions)
        
        # Select random questions
        selected_questions = random.sample(topic_questions, min(count, len(topic_questions)))
        
        return [AssessmentQuestion(**q) for q in selected_questions]
    
    async def conduct_assessment(self, topic: str, user_responses: List[AssessmentResponse]) -> AssessmentResult:
        """Conduct a complete assessment for a topic"""
        try:
            # Calculate individual skill scores
            skill_scores = []
            all_strengths = []
            all_weaknesses = []
            all_recommendations = []
            
            for response in user_responses:
                # Get the question details
                question = self._find_question_by_id(response.question_id)
                if not question:
                    continue
                
                # Assess the response
                assessment = await self.llm_service.assess_skill_response(
                    question.question,
                    response.user_answer,
                    question.evaluation_criteria
                )
                
                # Create skill score
                skill_score = SkillScore(
                    topic=topic,
                    subtopic=question.subtopic,
                    score=assessment.get("score", 50),
                    confidence=0.8  # Could be calculated based on response quality
                )
                skill_scores.append(skill_score)
                
                # Collect feedback
                all_strengths.extend(assessment.get("strengths", []))
                all_weaknesses.extend(assessment.get("improvements", []))
                all_recommendations.extend(assessment.get("suggestions", []))
            
            # Calculate overall score
            overall_score = sum(score.score for score in skill_scores) // len(skill_scores) if skill_scores else 0
            
            # Create assessment result
            result = AssessmentResult(
                session_id="",  # Will be set by caller
                topic=topic,
                overall_score=overall_score,
                skill_scores=skill_scores,
                strengths=list(set(all_strengths)),
                weaknesses=list(set(all_weaknesses)),
                recommendations=list(set(all_recommendations))
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error conducting assessment: {e}")
            return AssessmentResult(
                session_id="",
                topic=topic,
                overall_score=0,
                skill_scores=[],
                strengths=[],
                weaknesses=[],
                recommendations=[]
            )
    
    def _find_question_by_id(self, question_id: str) -> Optional[AssessmentQuestion]:
        """Find a question by its ID"""
        for topic, subtopics in self.questions.items():
            for subtopic, questions in subtopics.items():
                for question in questions:
                    if question["id"] == question_id:
                        return AssessmentQuestion(**question)
        return None
    
    async def generate_follow_up_question(self, topic: str, subtopic: str, previous_answers: List[str]) -> str:
        """Generate a follow-up question based on previous answers"""
        return await self.llm_service.generate_follow_up_question(topic, subtopic, previous_answers)
    
    def get_skill_level_description(self, score: int) -> str:
        """Get a description of the skill level based on score"""
        if score >= 90:
            return "Expert"
        elif score >= 75:
            return "Advanced"
        elif score >= 60:
            return "Intermediate"
        elif score >= 40:
            return "Beginner"
        else:
            return "Novice"
    
    def calculate_topic_proficiency(self, skill_scores: List[SkillScore]) -> Dict[str, Any]:
        """Calculate overall proficiency for a topic"""
        if not skill_scores:
            return {"level": "Unknown", "score": 0, "confidence": 0}
        
        avg_score = sum(score.score for score in skill_scores) / len(skill_scores)
        avg_confidence = sum(score.confidence for score in skill_scores) / len(skill_scores)
        
        return {
            "level": self.get_skill_level_description(int(avg_score)),
            "score": int(avg_score),
            "confidence": avg_confidence,
            "subtopic_scores": {score.subtopic: score.score for score in skill_scores}
        }
    
    def get_assessment_summary(self, results: List[AssessmentResult]) -> Dict[str, Any]:
        """Generate a summary of all assessment results"""
        if not results:
            return {"overall_level": "Unknown", "topics": {}, "recommendations": []}
        
        topic_summaries = {}
        all_recommendations = []
        
        for result in results:
            topic_summaries[result.topic] = self.calculate_topic_proficiency(result.skill_scores)
            all_recommendations.extend(result.recommendations)
        
        # Calculate overall level
        overall_scores = [summary["score"] for summary in topic_summaries.values()]
        overall_avg = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        return {
            "overall_level": self.get_skill_level_description(int(overall_avg)),
            "overall_score": int(overall_avg),
            "topics": topic_summaries,
            "recommendations": list(set(all_recommendations))
        }
