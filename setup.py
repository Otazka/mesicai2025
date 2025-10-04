#!/usr/bin/env python3
"""
Setup script for the AI Skills Development Chatbot
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "backend/data/roadmap_cache",
        "chroma_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Set up environment file"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file and add your OpenAI API key")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("❌ env.example file not found")

def main():
    """Main setup function"""
    print("🚀 Setting up AI Skills Development Chatbot")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Set up environment
    setup_environment()
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Check if OpenAI API key is set
    env_file = Path(".env")
    if env_file.exists():
        env_content = env_file.read_text()
        if "OPENAI_API_KEY=your_openai_api_key_here" in env_content:
            print("⚠️  Please set your OpenAI API key in the .env file")
            print("   Get your API key from: https://platform.openai.com/api-keys")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python scripts/scrape_roadmap.py")
    print("3. Run: python scripts/setup_vectordb.py")
    print("4. Start backend: python run_backend.py")
    print("5. Start frontend: python run_frontend.py")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
