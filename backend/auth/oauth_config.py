"""
Google OAuth 2.0 Configuration
"""
import os
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json

class GoogleOAuthConfig:
    """Google OAuth 2.0 configuration and utilities"""
    
    def __init__(self):
        # OAuth 2.0 client configuration
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
        
        # Scopes for accessing user information
        self.scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ]
        
        # OAuth flow configuration
        self.flow_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate Google OAuth authorization URL"""
        if not self.client_id:
            raise ValueError("Google Client ID not configured")
        
        flow = Flow.from_client_config(
            self.flow_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state
        )
        
        return authorization_url
    
    def exchange_code_for_token(self, authorization_code: str) -> dict:
        """Exchange authorization code for access token"""
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")
        
        flow = Flow.from_client_config(
            self.flow_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=authorization_code)
        
        return {
            "access_token": flow.credentials.token,
            "refresh_token": flow.credentials.refresh_token,
            "expires_in": flow.credentials.expiry.timestamp() if flow.credentials.expiry else None,
            "token_type": "Bearer"
        }
    
    def get_user_info(self, access_token: str) -> dict:
        """Get user information from Google API"""
        try:
            service = build('oauth2', 'v2', credentials=Credentials(token=access_token))
            user_info = service.userinfo().get().execute()
            
            return {
                "id": user_info.get("id"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "given_name": user_info.get("given_name"),
                "family_name": user_info.get("family_name"),
                "picture": user_info.get("picture"),
                "verified_email": user_info.get("verified_email", False)
            }
        except Exception as e:
            raise ValueError(f"Failed to get user info: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")
        
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        credentials.refresh(Request())
        
        return {
            "access_token": credentials.token,
            "expires_in": credentials.expiry.timestamp() if credentials.expiry else None,
            "token_type": "Bearer"
        }

# Global instance
google_oauth = GoogleOAuthConfig()
