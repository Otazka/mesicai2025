"""
Configuration settings for the AI Skills Development Chatbot
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: str
    anthropic_api_key: Optional[str] = None
    
    # Google OAuth Configuration
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None
    
    # JWT Configuration
    jwt_secret_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./skills_chatbot.db"
    
    # Vector Database
    chroma_persist_dir: str = "./chroma_db"
    
    # Application Settings
    log_level: str = "INFO"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Frontend
    streamlit_port: int = 8501
    
    # LLM Settings
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
