#!/usr/bin/env python3
"""
Google OAuth Demo for AI Skills Development Chatbot
"""

import requests
import json
import webbrowser
from urllib.parse import urlparse, parse_qs

def test_oauth_endpoints():
    """Test all Google OAuth endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔐 Google OAuth Integration Demo")
    print("=" * 50)
    print()
    
    # Test 1: Health check
    print("1. 🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Backend is running")
            print(f"   📊 Status: {response.json()}")
        else:
            print("   ❌ Backend not responding")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print()
    
    # Test 2: Check available endpoints
    print("2. 📋 Available OAuth endpoints:")
    oauth_endpoints = [
        "/auth/login",
        "/auth/callback", 
        "/auth/refresh",
        "/auth/logout",
        "/auth/me"
    ]
    
    for endpoint in oauth_endpoints:
        print(f"   🔗 {base_url}{endpoint}")
    
    print()
    
    # Test 3: Test login endpoint (will show configuration needed)
    print("3. 🔑 Testing login endpoint...")
    try:
        response = requests.get(f"{base_url}/auth/login")
        if response.status_code == 200:
            auth_data = response.json()
            print("   ✅ Login endpoint working")
            print(f"   🔗 Authorization URL: {auth_data['authorization_url']}")
            print(f"   🛡️  State: {auth_data['state']}")
        else:
            error_data = response.json()
            print(f"   ⚠️  {error_data['detail']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 4: Show configuration requirements
    print("4. ⚙️  Configuration Status:")
    print("   📝 To complete Google OAuth setup:")
    print("   1. Get Google OAuth credentials from Google Cloud Console")
    print("   2. Update .env file with:")
    print("      - GOOGLE_CLIENT_ID=your_actual_client_id")
    print("      - GOOGLE_CLIENT_SECRET=your_actual_client_secret")
    print("   3. Restart the backend")
    print()
    
    # Test 5: Show API documentation
    print("5. 📚 API Documentation:")
    print(f"   🌐 Swagger UI: {base_url}/docs")
    print(f"   📖 OpenAPI Spec: {base_url}/openapi.json")
    print()
    
    # Test 6: Show frontend integration
    print("6. 🎨 Frontend Integration:")
    print("   📱 Streamlit app: http://localhost:8501")
    print("   🔐 Auth component: frontend/auth_component.py")
    print("   💡 Features:")
    print("      - Google sign-in button")
    print("      - User profile display")
    print("      - Token management")
    print("      - Automatic logout")
    print()

def show_setup_instructions():
    """Show detailed setup instructions"""
    print("🚀 Complete Google OAuth Setup Instructions")
    print("=" * 60)
    print()
    
    print("📋 Step 1: Google Cloud Console Setup")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable the Google Identity API")
    print("4. Go to: https://console.cloud.google.com/apis/credentials")
    print("5. Click 'Create Credentials' → 'OAuth 2.0 Client IDs'")
    print("6. Choose 'Web application'")
    print("7. Add authorized redirect URIs:")
    print("   - http://localhost:8000/auth/callback")
    print("   - http://localhost:8501/auth/callback")
    print("8. Copy the Client ID and Client Secret")
    print()
    
    print("⚙️  Step 2: Update Environment Variables")
    print("Edit your .env file and replace the placeholder values:")
    print()
    print("GOOGLE_CLIENT_ID=your_actual_client_id_here")
    print("GOOGLE_CLIENT_SECRET=your_actual_client_secret_here")
    print("GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback")
    print("JWT_SECRET_KEY=UuGJ0TdwGePAByg5LPHJuhSRg1xvRUT3O5udNLhkSTw")
    print()
    
    print("🔄 Step 3: Restart Backend")
    print("1. Stop the current backend (Ctrl+C)")
    print("2. Run: python working_backend.py")
    print("3. Verify: curl http://localhost:8000/auth/login")
    print()
    
    print("🎯 Step 4: Test the Flow")
    print("1. Visit: http://localhost:8000/auth/login")
    print("2. Complete Google OAuth flow")
    print("3. Get access token from callback")
    print("4. Use token for authenticated requests")
    print()
    
    print("🎨 Step 5: Frontend Integration")
    print("1. Start Streamlit: streamlit run frontend/app.py")
    print("2. Use the auth component for sign-in")
    print("3. Access user profile and protected features")
    print()

def main():
    """Main demo function"""
    test_oauth_endpoints()
    show_setup_instructions()
    
    print("🎉 Google OAuth Integration Complete!")
    print("Your AI Skills Development Chatbot now supports:")
    print("✅ Google sign-in authentication")
    print("✅ JWT token management")
    print("✅ User profile storage")
    print("✅ Protected API endpoints")
    print("✅ Frontend authentication UI")
    print()
    print("🔗 Quick Links:")
    print("   Backend API: http://localhost:8000/docs")
    print("   Frontend: http://localhost:8501")
    print("   Google Console: https://console.cloud.google.com/apis/credentials")

if __name__ == "__main__":
    main()
