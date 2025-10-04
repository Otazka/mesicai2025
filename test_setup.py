#!/usr/bin/env python3
"""
Test script to verify the AI Skills Development Chatbot setup
"""

import sys
import os
import json
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "uvicorn"),
        ("langchain", "langchain"),
        ("openai", "openai"),
        ("chromadb", "chromadb"),
        ("streamlit", "streamlit"),
        ("plotly", "plotly"),
        ("sqlalchemy", "sqlalchemy"),
        ("pydantic", "pydantic"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("sentence_transformers", "sentence_transformers")
    ]
    
    failed_imports = []
    
    for package, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        "requirements.txt",
        "env.example",
        "README.md",
        "backend/main.py",
        "backend/config.py",
        "backend/models/schemas.py",
        "backend/models/database.py",
        "backend/services/llm_service.py",
        "backend/services/assessment.py",
        "backend/services/gap_analysis.py",
        "backend/services/recommendations.py",
        "backend/services/roadmap_service.py",
        "backend/api/routes.py",
        "backend/data/skill_taxonomy.json",
        "backend/data/questions.json",
        "frontend/app.py",
        "scripts/scrape_roadmap.py",
        "scripts/setup_vectordb.py",
        "run_backend.py",
        "run_frontend.py",
        "setup.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files exist")
    return True

def test_json_files():
    """Test if JSON files are valid"""
    print("\n🧪 Testing JSON files...")
    
    json_files = [
        "backend/data/skill_taxonomy.json",
        "backend/data/questions.json"
    ]
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                json.load(f)
            print(f"  ✅ {json_file}")
        except json.JSONDecodeError as e:
            print(f"  ❌ {json_file}: Invalid JSON - {e}")
            return False
        except FileNotFoundError:
            print(f"  ❌ {json_file}: File not found")
            return False
    
    print("✅ All JSON files are valid")
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🧪 Testing environment configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ .env file exists")
        
        # Check if API key is set
        env_content = env_file.read_text()
        if "OPENAI_API_KEY=your_openai_api_key_here" in env_content:
            print("  ⚠️  OpenAI API key not set (using placeholder)")
        else:
            print("  ✅ OpenAI API key appears to be set")
    else:
        print("  ⚠️  .env file not found (will be created from template)")
    
    # Check directories
    directories = ["backend/data/roadmap_cache", "chroma_db", "logs"]
    for directory in directories:
        if Path(directory).exists():
            print(f"  ✅ Directory exists: {directory}")
        else:
            print(f"  ⚠️  Directory missing: {directory} (will be created)")
    
    return True

def test_python_syntax():
    """Test if Python files have valid syntax"""
    print("\n🧪 Testing Python syntax...")
    
    python_files = [
        "backend/main.py",
        "backend/config.py",
        "backend/models/schemas.py",
        "backend/models/database.py",
        "backend/services/llm_service.py",
        "backend/services/assessment.py",
        "backend/services/gap_analysis.py",
        "backend/services/recommendations.py",
        "backend/services/roadmap_service.py",
        "backend/api/routes.py",
        "frontend/app.py",
        "scripts/scrape_roadmap.py",
        "scripts/setup_vectordb.py",
        "run_backend.py",
        "run_frontend.py",
        "setup.py"
    ]
    
    syntax_errors = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                compile(f.read(), py_file, 'exec')
            print(f"  ✅ {py_file}")
        except SyntaxError as e:
            print(f"  ❌ {py_file}: Syntax error - {e}")
            syntax_errors.append(py_file)
        except FileNotFoundError:
            print(f"  ❌ {py_file}: File not found")
            syntax_errors.append(py_file)
    
    if syntax_errors:
        print(f"\n❌ Syntax errors in: {', '.join(syntax_errors)}")
        return False
    
    print("✅ All Python files have valid syntax")
    return True

def main():
    """Main test function"""
    print("🧪 AI Skills Development Chatbot - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("File Structure", test_file_structure),
        ("JSON Files", test_json_files),
        ("Environment", test_environment),
        ("Python Syntax", test_python_syntax)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The setup is ready.")
        print("\nNext steps:")
        print("1. Set your OpenAI API key in .env file")
        print("2. Run: python scripts/scrape_roadmap.py")
        print("3. Run: python scripts/setup_vectordb.py")
        print("4. Start the application with: python run_backend.py")
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()
