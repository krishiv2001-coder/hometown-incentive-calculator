"""
Frontend configuration
"""
import os

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

# UI Configuration
PAGE_TITLE = "Hometown Incentive Calculator"
PAGE_ICON = "🏠"
