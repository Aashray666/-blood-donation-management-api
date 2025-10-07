"""
Configuration settings for the Blood Donation API
"""

import os
from pathlib import Path

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blood_donation.db")
DATABASE_FILE = "blood_donation.db"

# Application settings
APP_NAME = "Blood Donation Management API"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Directory paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"