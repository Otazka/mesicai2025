#!/usr/bin/env python3
"""
Google OAuth Setup Script
This script helps you set up Google OAuth for the AI Skills Development Chatbot
"""

import os
import webbrowser
from pathlib import Path

def print_setup_instructions():
    """Print detailed setup instructions for Google OAuth"""
    print("🔐 Google OAuth Setup for AI Skills Development Chatbot")
    print("=" * 60)
    print()
    
    print("📋 Step 1: Create Google Cloud Project")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable the Google+ API (or Google Identity API)")
    print()
    
    print("🔑 Step 2: Create OAuth 2.0 Credentials")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Click 'Create Credentials' → 'OAuth 2.0 Client IDs'")
    print("3. Choose 'Web application'")
    print("4. Add these authorized redirect URIs:")
    print("   - http://localhost:8000/auth/callback")
    print("   - http://localhost:8501/auth/callback")
    print("5. Copy the Client ID and Client Secret")
    print()
    
    print("⚙️  Step 3: Configure Environment Variables")
    print("Add these to your .env file:")
    print()
    print("GOOGLE_CLIENT_ID=your_client_id_here")
    print("GOOGLE_CLIENT_SECRET=your_client_secret_here")
    print("GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback")
    print("JWT_SECRET_KEY=your_random_secret_key_here")
    print()
    
    print("🚀 Step 4: Install Dependencies")
    print("Run: pip install -r requirements.txt")
    print()
    
    print("✅ Step 5: Test the Setup")
    print("1. Start the backend: python working_backend.py")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Test the /auth/login endpoint")
    print()

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Creating .env file from template...")
        
        # Copy from env.example if it exists
        example_file = Path("env.example")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created from template")
        else:
            # Create basic .env file
            with open(env_file, 'w') as f:
                f.write("""# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here

# Database
DATABASE_URL=sqlite:///./skills_chatbot.db

# Vector Database
CHROMA_PERSIST_DIR=./chroma_db

# Application Settings
LOG_LEVEL=INFO
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Frontend
STREAMLIT_PORT=8501
""")
            print("✅ Basic .env file created")
    
    # Check for required variables
    required_vars = [
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET", 
        "JWT_SECRET_KEY"
    ]
    
    missing_vars = []
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=your_" in content or f"{var}=" not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or incomplete variables in .env: {', '.join(missing_vars)}")
        print("Please update your .env file with the actual values")
        return False
    else:
        print("✅ All required environment variables are configured")
        return True

def generate_jwt_secret():
    """Generate a random JWT secret key"""
    import secrets
    return secrets.token_urlsafe(32)

def main():
    """Main setup function"""
    print_setup_instructions()
    
    print("🔍 Checking current configuration...")
    env_configured = check_env_file()
    
    if not env_configured:
        print()
        print("💡 Quick Setup:")
        print("1. Get your Google OAuth credentials from the Google Cloud Console")
        print("2. Update your .env file with the actual values")
        print("3. Run this script again to verify")
        print()
        
        # Generate JWT secret
        jwt_secret = generate_jwt_secret()
        print(f"🔑 Generated JWT Secret (add to .env):")
        print(f"JWT_SECRET_KEY={jwt_secret}")
        print()
        
        # Ask if user wants to open Google Console
        try:
            response = input("🌐 Open Google Cloud Console? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                webbrowser.open("https://console.cloud.google.com/apis/credentials")
                print("✅ Opened Google Cloud Console")
        except KeyboardInterrupt:
            print("\n👋 Setup cancelled")
    else:
        print()
        print("🎉 Google OAuth is configured!")
        print("🚀 You can now start the backend with authentication enabled")
        print("   python working_backend.py")

if __name__ == "__main__":
    main()
