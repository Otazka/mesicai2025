#!/usr/bin/env python3
"""
Script to run the Streamlit frontend
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit frontend"""
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down Streamlit...")
        sys.exit(0)

if __name__ == "__main__":
    main()
