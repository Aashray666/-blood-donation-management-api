#!/usr/bin/env python3
"""
Simple startup script for Blood Donation Management API
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Main startup function"""
    print("Blood Donation Management API")
    print("=" * 35)
    
    # Check if database exists
    db_file = Path("blood_donation.db")
    if not db_file.exists():
        print("Initializing database...")
        try:
            subprocess.run([sys.executable, "init_db.py"], check=True)
            print("[SUCCESS] Database ready!")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Database setup failed: {e}")
            return False
    else:
        print("[SUCCESS] Database found")
    
    print("\nStarting server...")
    print("Access points:")
    print("  - Web Dashboard: http://localhost:8000")
    print("  - API Docs: http://localhost:8000/docs")
    print("  - Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Start the server
        subprocess.run([sys.executable, "main.py"])
        return True
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
        return True
    except Exception as e:
        print(f"[ERROR] Server failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)