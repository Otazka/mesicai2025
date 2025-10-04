"""
Authentication component for Streamlit frontend
"""
import streamlit as st
import requests
import json
from typing import Optional, Dict, Any

# API configuration
API_BASE_URL = "http://localhost:8000"

def check_auth_status() -> Optional[Dict[str, Any]]:
    """Check if user is authenticated"""
    if "access_token" in st.session_state and st.session_state.access_token:
        try:
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                # Token expired or invalid
                st.session_state.access_token = None
                st.session_state.refresh_token = None
                return None
        except Exception as e:
            st.error(f"Authentication check failed: {str(e)}")
            return None
    return None

def render_login_button():
    """Render Google login button"""
    st.markdown("### 🔐 Sign in with Google")
    st.markdown("Sign in to save your progress and access personalized features.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Sign in with Google", type="primary", use_container_width=True):
            try:
                # Get authorization URL from backend
                response = requests.get(f"{API_BASE_URL}/auth/login")
                
                if response.status_code == 200:
                    auth_data = response.json()
                    auth_url = auth_data["authorization_url"]
                    
                    # Store state for verification
                    st.session_state.oauth_state = auth_data["state"]
                    
                    # Redirect to Google OAuth
                    st.markdown(f"""
                    <script>
                        window.open('{auth_url}', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
                    
                    st.info("🔗 Please complete the sign-in process in the new window that opened.")
                    st.markdown(f"[Click here to sign in with Google]({auth_url})")
                else:
                    st.error("Failed to initiate Google sign-in")
                    
            except Exception as e:
                st.error(f"Sign-in error: {str(e)}")

def render_user_profile(user_info: Dict[str, Any]):
    """Render user profile information"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if user_info.get("picture_url"):
            st.image(user_info["picture_url"], width=80)
        else:
            st.markdown("👤")
    
    with col2:
        st.markdown(f"**Welcome, {user_info.get('name', 'User')}!**")
        st.markdown(f"📧 {user_info.get('email', '')}")
        
        if st.button("🚪 Sign Out", type="secondary"):
            # Clear session data
            for key in ["access_token", "refresh_token", "user_info"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def handle_oauth_callback():
    """Handle OAuth callback (for manual token entry)"""
    st.markdown("### 🔑 Manual Token Entry")
    st.markdown("If you completed the OAuth flow, paste the tokens here:")
    
    access_token = st.text_input("Access Token", type="password")
    refresh_token = st.text_input("Refresh Token", type="password")
    
    if st.button("Save Tokens"):
        if access_token and refresh_token:
            st.session_state.access_token = access_token
            st.session_state.refresh_token = refresh_token
            
            # Verify the tokens
            user_info = check_auth_status()
            if user_info:
                st.session_state.user_info = user_info
                st.success("✅ Successfully authenticated!")
                st.rerun()
            else:
                st.error("❌ Invalid tokens")
        else:
            st.error("Please enter both tokens")

def render_auth_section():
    """Main authentication section"""
    st.markdown("---")
    
    # Check if user is authenticated
    user_info = check_auth_status()
    
    if user_info:
        # User is authenticated
        render_user_profile(user_info)
    else:
        # User is not authenticated
        render_login_button()
        
        # Show manual token entry option
        with st.expander("🔧 Manual Token Entry (for testing)"):
            handle_oauth_callback()

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers for API requests"""
    if "access_token" in st.session_state and st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}

def is_authenticated() -> bool:
    """Check if user is currently authenticated"""
    return check_auth_status() is not None
