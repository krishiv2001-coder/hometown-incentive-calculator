"""
Setup Verification Script
Run this to check if your environment is properly configured
"""
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8 or higher is required")
        return False

def check_packages():
    """Check if all required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'streamlit',
        'pandas',
        'openpyxl',
        'plotly',
        'requests'
    ]

    print("\nChecking required packages:")
    all_installed = True

    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            all_installed = False

    if all_installed:
        print("\n✅ All required packages are installed")
    else:
        print("\n❌ Some packages are missing. Run: pip install -r requirements.txt")

    return all_installed

def check_directory_structure():
    """Check if required directories exist"""
    print("\nChecking directory structure:")

    required_dirs = [
        'backend',
        'backend/api',
        'frontend',
        'frontend/pages',
        'frontend/components',
        'frontend/services',
        'data',
        'data/uploads',
        'data/outputs',
        'data/database'
    ]

    all_exist = True
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ - MISSING")
            all_exist = False

    if all_exist:
        print("\n✅ All required directories exist")
    else:
        print("\n⚠️ Some directories are missing (will be auto-created)")

    return True  # Non-critical

def check_required_files():
    """Check if required files exist"""
    print("\nChecking required files:")

    required_files = [
        'backend/main.py',
        'backend/calculator.py',
        'backend/database.py',
        'backend/models.py',
        'frontend/app.py',
        'frontend/services/api_client.py',
        'requirements.txt',
        'run_backend.bat',
        'run_frontend.bat'
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_exist = False

    if all_exist:
        print("\n✅ All required files exist")
    else:
        print("\n❌ Some required files are missing")

    return all_exist

def test_imports():
    """Test if backend modules can be imported"""
    print("\nTesting module imports:")

    try:
        from backend import database
        print("  ✅ backend.database")
    except Exception as e:
        print(f"  ❌ backend.database - {e}")
        return False

    try:
        from backend import models
        print("  ✅ backend.models")
    except Exception as e:
        print(f"  ❌ backend.models - {e}")
        return False

    try:
        from backend import calculator
        print("  ✅ backend.calculator")
    except Exception as e:
        print(f"  ❌ backend.calculator - {e}")
        return False

    try:
        from frontend.services import api_client
        print("  ✅ frontend.services.api_client")
    except Exception as e:
        print(f"  ❌ frontend.services.api_client - {e}")
        return False

    print("\n✅ All modules can be imported successfully")
    return True

def test_database_init():
    """Test if database can be initialized"""
    print("\nTesting database initialization:")

    try:
        from backend.database import init_db, engine
        from backend.models import Base

        # Try to create tables
        Base.metadata.create_all(bind=engine)
        print("  ✅ Database tables created successfully")

        # Check if database file exists
        db_path = Path("data/database/hometown.db")
        if db_path.exists():
            print(f"  ✅ Database file created: {db_path}")

        return True
    except Exception as e:
        print(f"  ❌ Database initialization failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("="*60)
    print("  HOMETOWN INCENTIVE CALCULATOR - SETUP VERIFICATION")
    print("="*60)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_packages),
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_required_files),
        ("Module Imports", test_imports),
        ("Database Initialization", test_database_init)
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Error during {name} check: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*60)
    print("  VERIFICATION SUMMARY")
    print("="*60)
    print()

    all_passed = all(results.values())

    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:.<40} {status}")

    print()

    if all_passed:
        print("="*60)
        print("  ✅ ALL CHECKS PASSED - SETUP IS COMPLETE!")
        print("="*60)
        print()
        print("Next steps:")
        print("1. Start backend:  run_backend.bat")
        print("2. Start frontend: run_frontend.bat")
        print("3. Open browser:   http://localhost:8501")
        print()
    else:
        print("="*60)
        print("  ⚠️ SOME CHECKS FAILED - PLEASE FIX ISSUES")
        print("="*60)
        print()
        print("Common solutions:")
        print("- Install Python 3.8+: https://www.python.org/downloads/")
        print("- Install packages: pip install -r requirements.txt")
        print("- Check file structure matches the project layout")
        print()
        print("See SETUP_GUIDE.md for detailed instructions")
        print()

if __name__ == "__main__":
    main()
