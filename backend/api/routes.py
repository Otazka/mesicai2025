"""
FastAPI routes for the AI Skills Development Chatbot
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging

from models.database import get_db, User, Assessment, Conversation, LearningPath as LearningPathDB, GapAnalysis as GapAnalysisDB
from models.schemas import (
    ChatRequest, ChatResponse, UserProfile, AssessmentQuestion, 
    AssessmentResponse, AssessmentResult, GapAnalysis, LearningPath,
    SkillExplanation, TargetRole, ExperienceLevel
)
from services.llm_service import LLMService
from services.assessment import SkillAssessor
from services.gap_analysis import GapAnalyzer
from services.recommendations import LearningPathGenerator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize services
llm_service = LLMService()
skill_assessor = SkillAssessor()
gap_analyzer = GapAnalyzer()
learning_path_generator = LearningPathGenerator()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint for conversational interaction"""
    try:
        # Get or create user
        user = db.query(User).filter(User.session_id == request.session_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please start with /api/start-assessment"
            )
        
        # Get conversation history
        conversation = db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).order_by(Conversation.updated_at.desc()).first()
        
        # Process the message
        response_message = await _process_chat_message(
            request.message, 
            user, 
            conversation,
            request.context or {}
        )
        
        # Save conversation
        if conversation:
            messages = conversation.messages
            messages.append({"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()})
            messages.append({"role": "assistant", "content": response_message, "timestamp": datetime.now().isoformat()})
            conversation.messages = messages
            conversation.updated_at = datetime.now()
        else:
            new_conversation = Conversation(
                user_id=user.id,
                messages=[
                    {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()},
                    {"role": "assistant", "content": response_message, "timestamp": datetime.now().isoformat()}
                ],
                context=request.context
            )
            db.add(new_conversation)
        
        db.commit()
        
        return ChatResponse(
            message=response_message,
            session_id=request.session_id,
            assessment_in_progress=False,  # Could be determined from context
            current_topic=None,  # Could be determined from context
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/start-assessment")
async def start_assessment(
    session_id: str,
    target_role: TargetRole,
    experience_level: ExperienceLevel,
    goals: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Start a new skill assessment"""
    try:
        # Create or update user
        user = db.query(User).filter(User.session_id == session_id).first()
        if user:
            user.target_role = target_role.value
            user.experience_level = experience_level.value
            user.goals = goals or []
        else:
            user = User(
                session_id=session_id,
                target_role=target_role.value,
                experience_level=experience_level.value,
                goals=goals or []
            )
            db.add(user)
        
        db.commit()
        
        # Get first assessment question
        questions = skill_assessor.get_assessment_questions("python", count=1)
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No assessment questions available"
            )
        
        first_question = questions[0]
        
        return {
            "session_id": session_id,
            "message": f"Welcome! I'll help you assess your skills for becoming a {target_role.value.replace('_', ' ')}. Let's start with Python fundamentals.",
            "question": first_question.dict(),
            "assessment_started": True
        }
        
    except Exception as e:
        logger.error(f"Error starting assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start assessment"
        )


@router.get("/assessment-results/{session_id}", response_model=List[AssessmentResult])
async def get_assessment_results(session_id: str, db: Session = Depends(get_db)):
    """Get assessment results for a session"""
    try:
        user = db.query(User).filter(User.session_id == session_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        assessments = db.query(Assessment).filter(Assessment.user_id == user.id).all()
        
        results = []
        for assessment in assessments:
            result = AssessmentResult(
                session_id=session_id,
                topic=assessment.topic,
                overall_score=assessment.overall_score or 0,
                skill_scores=[],  # Would need to parse from JSON
                strengths=assessment.strengths or [],
                weaknesses=assessment.weaknesses or [],
                recommendations=assessment.recommendations or [],
                completed_at=assessment.completed_at
            )
            results.append(result)
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting assessment results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assessment results"
        )


@router.post("/analyze-gaps", response_model=GapAnalysis)
async def analyze_gaps(
    session_id: str,
    current_skills: Dict[str, int],
    db: Session = Depends(get_db)
):
    """Analyze skill gaps for a user"""
    try:
        user = db.query(User).filter(User.session_id == session_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Perform gap analysis
        gap_analysis = await gap_analyzer.analyze(
            current_skills,
            TargetRole(user.target_role),
            ExperienceLevel(user.experience_level)
        )
        gap_analysis.session_id = session_id
        
        # Save gap analysis to database
        gap_analysis_db = GapAnalysisDB(
            session_id=session_id,
            target_role=user.target_role,
            current_skills=current_skills,
            required_skills=gap_analysis.required_skills,
            gaps=gap_analysis.gaps,
            priority_areas=gap_analysis.priority_areas
        )
        db.add(gap_analysis_db)
        db.commit()
        
        return gap_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing gaps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze skill gaps"
        )


@router.get("/learning-path/{session_id}", response_model=LearningPath)
async def get_learning_path(session_id: str, db: Session = Depends(get_db)):
    """Get personalized learning path for a user"""
    try:
        user = db.query(User).filter(User.session_id == session_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get latest gap analysis
        gap_analysis_db = db.query(GapAnalysisDB).filter(
            GapAnalysisDB.session_id == session_id
        ).order_by(GapAnalysisDB.generated_at.desc()).first()
        
        if not gap_analysis_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No gap analysis found. Please complete assessment first."
            )
        
        # Convert to schema
        gap_analysis = GapAnalysis(
            session_id=session_id,
            target_role=TargetRole(gap_analysis_db.target_role),
            current_skills=gap_analysis_db.current_skills,
            required_skills=gap_analysis_db.required_skills,
            gaps=gap_analysis_db.gaps,
            priority_areas=gap_analysis_db.priority_areas,
            generated_at=gap_analysis_db.generated_at
        )
        
        # Generate learning path
        learning_path = await learning_path_generator.generate_path(
            gap_analysis,
            user.goals or [],
            user.experience_level
        )
        learning_path.session_id = session_id
        
        # Save learning path to database
        learning_path_db = LearningPathDB(
            session_id=session_id,
            target_role=user.target_role,
            total_duration=learning_path.total_duration,
            objectives=learning_path.dict()["objectives"],
            weekly_breakdown=learning_path.weekly_breakdown
        )
        db.add(learning_path_db)
        db.commit()
        
        return learning_path
        
    except Exception as e:
        logger.error(f"Error getting learning path: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate learning path"
        )


@router.post("/explain-skill", response_model=SkillExplanation)
async def explain_skill(
    topic: str,
    subtopic: str,
    user_level: str = "intermediate"
):
    """Get detailed explanation of a skill"""
    try:
        explanation = await llm_service.explain_concept(topic, subtopic, user_level)
        
        return SkillExplanation(
            topic=topic,
            subtopic=subtopic,
            explanation=explanation.get("explanation", ""),
            examples=explanation.get("examples", []),
            resources=[],  # Could be populated from learning resources
            related_skills=explanation.get("related_concepts", [])
        )
        
    except Exception as e:
        logger.error(f"Error explaining skill: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to explain skill"
        )


@router.get("/questions/{topic}")
async def get_questions(topic: str, count: int = 5):
    """Get assessment questions for a topic"""
    try:
        questions = skill_assessor.get_assessment_questions(topic, count)
        return {"questions": [q.dict() for q in questions]}
        
    except Exception as e:
        logger.error(f"Error getting questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve questions"
        )


@router.get("/user-profile/{session_id}", response_model=UserProfile)
async def get_user_profile(session_id: str, db: Session = Depends(get_db)):
    """Get user profile"""
    try:
        user = db.query(User).filter(User.session_id == session_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile(
            session_id=user.session_id,
            target_role=TargetRole(user.target_role),
            experience_level=ExperienceLevel(user.experience_level),
            goals=user.goals or [],
            created_at=user.created_at
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


async def _process_chat_message(
    message: str, 
    user: User, 
    conversation: Optional[Conversation],
    context: Dict[str, Any]
) -> str:
    """Process a chat message and generate response"""
    try:
        # Simple response for now - could be enhanced with more sophisticated logic
        if "hello" in message.lower() or "hi" in message.lower():
            return f"Hello! I'm here to help you develop your IT skills for becoming a {user.target_role.replace('_', ' ')}. How can I assist you today?"
        
        elif "assessment" in message.lower():
            return "I can help you with a skill assessment! Let's start by evaluating your Python, OOP, and Algorithms knowledge. Would you like to begin?"
        
        elif "learning path" in message.lower() or "roadmap" in message.lower():
            return "I can create a personalized learning path for you! First, let's complete a skill assessment to identify your strengths and areas for improvement."
        
        elif "explain" in message.lower():
            return "I'd be happy to explain any IT concept! What specific topic would you like me to explain? (e.g., Python OOP, sorting algorithms, etc.)"
        
        else:
            return "I'm here to help with your IT skills development! I can assist with skill assessments, gap analysis, learning paths, and explaining technical concepts. What would you like to work on?"
    
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return "I apologize, but I'm having trouble processing your message right now. Please try again."
