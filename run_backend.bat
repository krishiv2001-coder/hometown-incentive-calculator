@echo off
echo ========================================
echo  Hometown Incentive Calculator - Backend
echo ========================================
echo.
echo Starting FastAPI server...
echo.
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
pause
