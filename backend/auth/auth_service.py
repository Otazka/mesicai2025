"""
Authentication Service for Google OAuth
"""
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.models.database import User, get_db
from backend.auth.oauth_config import google_oauth
import os

class AuthService:
    """Authentication service for handling Google OAuth and JWT tokens"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, user_id: str, email: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authenticate_user_with_google(self, authorization_code: str, db: Session) -> Dict[str, Any]:
        """Authenticate user with Google OAuth and create/update user record"""
        try:
            # Exchange code for token
            token_data = google_oauth.exchange_code_for_token(authorization_code)
            access_token = token_data["access_token"]
            refresh_token = token_data.get("refresh_token")
            
            # Get user info from Google
            user_info = google_oauth.get_user_info(access_token)
            
            # Check if user exists
            user = db.query(User).filter(User.google_id == user_info["id"]).first()
            
            if not user:
                # Create new user
                user = User(
                    google_id=user_info["id"],
                    email=user_info["email"],
                    name=user_info["name"],
                    picture_url=user_info.get("picture"),
                    is_verified=user_info.get("verified_email", False),
                    created_at=datetime.utcnow()
                )
                db.add(user)
            else:
                # Update existing user
                user.email = user_info["email"]
                user.name = user_info["name"]
                user.picture_url = user_info.get("picture")
                user.is_verified = user_info.get("verified_email", False)
                user.last_login = datetime.utcnow()
            
            db.commit()
            db.refresh(user)
            
            # Create JWT tokens
            access_token_jwt = self.create_access_token(str(user.id), user.email)
            refresh_token_jwt = self.create_refresh_token(str(user.id))
            
            return {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "picture_url": user.picture_url,
                    "is_verified": user.is_verified
                },
                "access_token": access_token_jwt,
                "refresh_token": refresh_token_jwt,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except Exception as e:
            db.rollback()
            raise ValueError(f"Authentication failed: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str, db: Session) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        new_access_token = self.create_access_token(str(user.id), user.email)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def get_current_user(self, token: str, db: Session) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if not payload or payload.get("type") != "access":
            return None
        
        user_id = payload["sub"]
        return db.query(User).filter(User.id == user_id).first()
    
    def logout_user(self, refresh_token: str) -> bool:
        """Logout user (invalidate refresh token)"""
        # In a production app, you might want to blacklist the token
        # For now, we'll just return True as JWT tokens are stateless
        return True

# Global instance
auth_service = AuthService()
