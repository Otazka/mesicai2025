"""
Authentication routes for Google OAuth
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import secrets
import urllib.parse

from backend.models.database import get_db
from backend.auth.auth_service import auth_service
from backend.auth.oauth_config import google_oauth

router = APIRouter(prefix="/auth", tags=["authentication"])

# Store state for CSRF protection (in production, use Redis or database)
oauth_states = {}

@router.get("/login")
async def google_login():
    """Initiate Google OAuth login"""
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        oauth_states[state] = True
        
        # Get authorization URL
        auth_url = google_oauth.get_authorization_url(state=state)
        
        return {
            "authorization_url": auth_url,
            "state": state
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate login: {str(e)}"
        )

@router.get("/callback")
async def google_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Check for errors
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth error: {error}"
            )
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not provided"
            )
        
        # Verify state for CSRF protection
        if state not in oauth_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
        # Remove used state
        del oauth_states[state]
        
        # Authenticate user
        auth_result = auth_service.authenticate_user_with_google(code, db)
        
        # In a real app, you might redirect to frontend with tokens
        # For now, return the tokens directly
        return {
            "message": "Authentication successful",
            "user": auth_result["user"],
            "access_token": auth_result["access_token"],
            "refresh_token": auth_result["refresh_token"],
            "token_type": auth_result["token_type"],
            "expires_in": auth_result["expires_in"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    try:
        result = auth_service.refresh_access_token(refresh_token, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")
async def logout(refresh_token: str):
    """Logout user"""
    try:
        success = auth_service.logout_user(refresh_token)
        return {"message": "Logged out successfully", "success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get current user information"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required"
            )
        
        token = authorization.split(" ")[1]
        user = auth_service.get_current_user(token, db)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "picture_url": user.picture_url,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )
