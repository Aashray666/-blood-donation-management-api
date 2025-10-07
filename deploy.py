#!/usr/bin/env python3
"""
Deployment script for Blood Donation Management API
Automates the setup process for different environments
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path

class DeploymentManager:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_cmd = self.get_python_command()
        self.pip_cmd = "uv pip" if self.check_uv_available() else "pip"
        
    def get_python_command(self):
        """Get the appropriate Python command for the system"""
        for cmd in ['python3', 'python']:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and 'Python 3.' in result.stdout:
                    return cmd
            except FileNotFoundError:
                continue
        raise RuntimeError("Python 3.8+ not found. Please install Python 3.8 or higher.")
    
    def check_uv_available(self):
        """Check if uv is available"""
        try:
            subprocess.run(['uv', '--version'], 
                          capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def run_command(self, command, check=True, shell=False):
        """Run a command and handle errors"""
        print(f"Running: {command}")
        try:
            if isinstance(command, str) and not shell:
                command = command.split()
            result = subprocess.run(command, check=check, shell=shell)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
            return False
        except FileNotFoundError as e:
            print(f"Command not found: {e}")
            return False
    
    def create_virtual_environment(self):
        """Create virtual environment"""
        print("Creating virtual environment...")
        
        if self.check_uv_available():
            return self.run_command("uv venv")
        else:
            return self.run_command(f"{self.python_cmd} -m venv .venv")
    
    def get_activation_command(self):
        """Get the virtual environment activation command"""
        if self.system == "windows":
            return ".venv\\Scripts\\activate"
        else:
            return "source .venv/bin/activate"
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("Installing dependencies...")
        
        # Check if requirements.txt exists
        if not Path("requirements.txt").exists():
            print("Error: requirements.txt not found!")
            return False
        
        if self.check_uv_available():
            return self.run_command("uv pip install -r requirements.txt")
        else:
            return self.run_command("pip install -r requirements.txt")
    
    def initialize_database(self):
        """Initialize the database"""
        print("Initializing database...")
        return self.run_command(f"{self.python_cmd} init_db.py")
    
    def run_tests(self):
        """Run integration tests"""
        print("Running integration tests...")
        return self.run_command(f"{self.python_cmd} test_integration.py")
    
    def start_server(self, host="0.0.0.0", port=8000, reload=False):
        """Start the development server"""
        print(f"Starting server on {host}:{port}...")
        
        if reload:
            cmd = f"uvicorn main:app --reload --host {host} --port {port}"
        else:
            cmd = f"{self.python_cmd} main.py"
        
        print(f"Server will be available at:")
        print(f"  - Web Dashboard: http://localhost:{port}")
        print(f"  - API Documentation: http://localhost:{port}/docs")
        print(f"  - Health Check: http://localhost:{port}/health")
        print("\nPress Ctrl+C to stop the server")
        
        return self.run_command(cmd, shell=True)
    
    def setup_development(self):
        """Complete development setup"""
        print("Setting up development environment...")
        print("=" * 50)
        
        steps = [
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Initializing database", self.initialize_database),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"Failed: {step_name}")
                return False
            print(f"✅ {step_name} completed")
        
        print("\n" + "=" * 50)
        print("🎉 Development setup completed successfully!")
        print("\nNext steps:")
        print(f"1. Activate virtual environment: {self.get_activation_command()}")
        print(f"2. Start the server: {self.python_cmd} main.py")
        print("3. Open http://localhost:8000 in your browser")
        
        return True
    
    def setup_production(self):
        """Setup for production environment"""
        print("Setting up production environment...")
        print("=" * 50)
        
        # Install production dependencies
        if not self.install_dependencies():
            return False
        
        # Install production server
        print("Installing production server (gunicorn)...")
        if self.check_uv_available():
            if not self.run_command("uv pip install gunicorn"):
                return False
        else:
            if not self.run_command("pip install gunicorn"):
                return False
        
        # Initialize database
        if not self.initialize_database():
            return False
        
        print("\n" + "=" * 50)
        print("🎉 Production setup completed!")
        print("\nTo start the production server:")
        print("gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000")
        
        return True
    
    def quick_start(self):
        """Quick start for immediate testing"""
        print("Quick start setup...")
        print("=" * 30)
        
        # Check if database exists, if not initialize it
        if not Path("blood_donation.db").exists():
            print("Database not found, initializing...")
            if not self.initialize_database():
                return False
        
        # Start server immediately
        return self.start_server(reload=True)
    
    def install_uv(self):
        """Install uv package manager"""
        print("Installing uv package manager...")
        try:
            # Try to install uv using pip
            result = subprocess.run([self.python_cmd, "-m", "pip", "install", "uv"], 
                                  check=True, capture_output=True, text=True)
            print("✅ uv installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install uv: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Blood Donation API Deployment Manager")
    parser.add_argument("command", choices=[
        "dev", "development",
        "prod", "production", 
        "start", "server",
        "test", "tests",
        "quick", "quickstart",
        "install-uv"
    ], help="Deployment command")
    
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    manager = DeploymentManager()
    
    try:
        if args.command in ["dev", "development"]:
            success = manager.setup_development()
        elif args.command in ["prod", "production"]:
            success = manager.setup_production()
        elif args.command in ["start", "server"]:
            success = manager.start_server(
                host=args.host, 
                port=args.port, 
                reload=not args.no_reload
            )
        elif args.command in ["test", "tests"]:
            success = manager.run_tests()
        elif args.command in ["quick", "quickstart"]:
            success = manager.quick_start()
        elif args.command == "install-uv":
            success = manager.install_uv()
        else:
            print(f"Unknown command: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()