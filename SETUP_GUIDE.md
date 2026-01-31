# Setup Guide - Hometown Incentive Calculator

## Prerequisites

### 1. Install Python 3.8 or Higher

**Download from**: https://www.python.org/downloads/

**During installation:**
- ✅ Check "Add Python to PATH"
- ✅ Check "Install pip"

**Verify installation:**
```bash
python --version
pip --version
```

Should show Python 3.8+ and pip version.

## Installation Steps

### Step 1: Install Dependencies

Open Command Prompt or PowerShell in the project directory:

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (backend framework)
- Uvicorn (ASGI server)
- SQLAlchemy (database ORM)
- Streamlit (frontend framework)
- Pandas, Plotly (data processing and visualization)
- And other required packages

**Note**: This may take 5-10 minutes depending on your internet connection.

### Step 2: Verify Installation

Run the verification script:

```bash
python verify_setup.py
```

This will check:
- ✅ Python version
- ✅ All required packages installed
- ✅ Directory structure created
- ✅ Database can be initialized

### Step 3: Initialize Database

The database will be created automatically when you first start the backend, but you can initialize it manually:

```bash
python -c "from backend.database import init_db; init_db(); print('Database initialized!')"
```

## Running the Application

### Option 1: Using Batch Files (Windows - Recommended)

**Terminal 1 - Start Backend:**
```bash
run_backend.bat
```

**Terminal 2 - Start Frontend:**
```bash
run_frontend.bat
```

### Option 2: Manual Commands

**Terminal 1 - Start Backend:**
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run frontend/app.py --server.port 8501
```

### Access the Application

- **Frontend Dashboard**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## First Time Usage

1. Backend will automatically create the database on first run
2. Directory structure (`data/uploads`, `data/outputs`, `data/database`) will be created automatically
3. Upload the sample file `IncentiveWorking_Krishiv.xlsx` to test

## Common Issues and Solutions

### Issue: "Python was not found"

**Solution:**
1. Install Python from python.org
2. Make sure to check "Add Python to PATH" during installation
3. Restart Command Prompt after installation

### Issue: "pip: command not found"

**Solution:**
```bash
python -m ensurepip --upgrade
```

### Issue: "Port 8000 already in use"

**Solution:**
Either:
- Stop the other process using port 8000
- Or change the port in `.env` file:
  ```
  API_PORT=8001
  ```

### Issue: "Module not found" errors

**Solution:**
Make sure you're in the project root directory and run:
```bash
pip install -r requirements.txt
```

### Issue: "Cannot connect to backend API" in frontend

**Solution:**
1. Make sure backend is running first
2. Check backend URL in `frontend/config.py`
3. Verify backend is accessible: http://127.0.0.1:8000/health

### Issue: Database errors

**Solution:**
Delete the database and let it recreate:
```bash
# Windows
del data\database\hometown.db

# Then restart backend - it will recreate the database
```

## Testing

### Test Backend API

Open browser to: http://localhost:8000/docs

Try these endpoints:
1. GET `/` - Should return API info
2. GET `/health` - Should return {"status": "healthy"}

### Test File Upload

1. Go to frontend: http://localhost:8501
2. Click on "Upload" page
3. Upload `IncentiveWorking_Krishiv.xlsx`
4. Click "Process File"
5. Wait for completion
6. Verify results match expected totals:
   - Total: ₹5,23,929.52
   - Transactions: 8,535
   - Employees: 147
   - Stores: 14

### Test Dashboard

1. After processing a file, go to "Dashboard" page
2. Verify charts are displayed
3. Test filters (Store, Role)
4. Check employee summary table

### Test History

1. Go to "History" page
2. Verify upload is listed
3. Click "Download" to download results
4. Open Excel file and verify 4 sheets:
   - Detailed Transactions
   - Employee Points Summary
   - Daily Qualifier Tracker
   - Monthly Targets

## Advanced Configuration

### Change Ports

Edit `.env` file:
```bash
API_PORT=8001        # Backend port
STREAMLIT_PORT=8502  # Frontend port
```

### Change Database Location

Edit `.env` file:
```bash
DATABASE_URL=sqlite:///C:/path/to/your/database.db
```

### Enable Debug Mode

For backend:
```bash
python -m uvicorn backend.main:app --reload --log-level debug
```

For frontend:
```bash
streamlit run frontend/app.py --server.port 8501 --logger.level=debug
```

## Project Structure

```
Frontend/
├── backend/                    # FastAPI Backend
│   ├── api/
│   │   ├── upload.py          # File upload endpoint
│   │   ├── process.py         # Processing endpoint
│   │   └── data.py            # Data query endpoints
│   ├── calculator.py          # Core calculation logic
│   ├── config.py              # Configuration
│   ├── database.py            # Database setup
│   ├── models.py              # Database models
│   ├── schemas.py             # API schemas
│   └── main.py                # FastAPI app
│
├── frontend/                   # Streamlit Frontend
│   ├── pages/
│   │   ├── 1_📤_Upload.py    # Upload page
│   │   ├── 2_📊_Dashboard.py # Dashboard page
│   │   └── 3_📜_History.py   # History page
│   ├── components/
│   │   └── charts.py          # Chart components
│   ├── services/
│   │   └── api_client.py      # API client
│   ├── config.py              # Frontend config
│   └── app.py                 # Main app
│
├── data/                       # Data storage (auto-created)
│   ├── uploads/               # Uploaded Excel files
│   ├── outputs/               # Generated Excel files
│   └── database/              # SQLite database
│
├── requirements.txt           # Python dependencies
├── .env                       # Configuration file
├── run_backend.bat            # Start backend (Windows)
├── run_frontend.bat           # Start frontend (Windows)
├── verify_setup.py            # Setup verification script
├── README.md                  # Quick start guide
└── SETUP_GUIDE.md            # This file (detailed setup)
```

## Next Steps

After successful setup:
1. Process the sample file to verify everything works
2. Review the calculation logic in `backend/calculator.py`
3. Update target values in the database as needed
4. Customize charts in `frontend/components/charts.py` if needed

## Support

If you encounter issues not covered here:
1. Check the error message carefully
2. Verify all dependencies are installed
3. Make sure both backend and frontend are running
4. Check the console logs for detailed error messages
