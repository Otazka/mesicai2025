"""
SQLAlchemy database models for the AI Skills Development Chatbot
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

# Create database engine
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    target_role = Column(String, nullable=False)
    experience_level = Column(String, nullable=False)
    goals = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assessments = relationship("Assessment", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")


class Assessment(Base):
    """Assessment model"""
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    questions_answers = Column(JSON, nullable=False)
    overall_score = Column(Integer, nullable=True)
    skill_scores = Column(JSON, nullable=True)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="assessments")


class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    messages = Column(JSON, nullable=False)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")


class LearningPath(Base):
    """Learning path model"""
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    target_role = Column(String, nullable=False)
    total_duration = Column(Integer, nullable=False)
    objectives = Column(JSON, nullable=False)
    weekly_breakdown = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)


class GapAnalysis(Base):
    """Gap analysis model"""
    __tablename__ = "gap_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    target_role = Column(String, nullable=False)
    current_skills = Column(JSON, nullable=False)
    required_skills = Column(JSON, nullable=False)
    gaps = Column(JSON, nullable=False)
    priority_areas = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)


# Database initialization
async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
