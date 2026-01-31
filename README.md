# Hometown Incentive Calculator

Web-based automation system for calculating employee sales incentives.

## Features

- **File Upload**: Upload sales data Excel files
- **Automated Processing**: Calculate incentives based on sales slabs and roles
- **Interactive Dashboard**: View analytics, charts, and performance metrics
- **Upload History**: Track all past uploads and download results
- **Database Storage**: Full history of all calculations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Backend Server

**Windows:**
```bash
run_backend.bat
```

**Or manually:**
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The backend API will be available at: http://127.0.0.1:8000

API Documentation: http://127.0.0.1:8000/docs

### 3. Start the Frontend Dashboard

**In a new terminal**, run:

**Windows:**
```bash
run_frontend.bat
```

**Or manually:**
```bash
streamlit run frontend/app.py --server.port 8501
```

The frontend will open automatically at: http://localhost:8501

## Usage

1. **Upload**: Go to the Upload page (📤) and upload your Excel file
   - File must have sheet: `Sales Report - Hometown (2)`
   - Required columns will be validated automatically

2. **Process**: Click "Process File" and wait for completion
   - Progress bar shows processing status
   - Download results when complete

3. **Dashboard**: View analytics (📊)
   - KPI cards showing totals
   - Charts: Store performance, LOB breakdown, top performers
   - Qualifier tracker showing target achievements
   - Filterable employee summary table

4. **History**: Browse past uploads (📜)
   - View all previous uploads
   - Download any past results
   - Navigate to dashboard for detailed analysis

## Project Structure

```
hometown-incentive-frontend/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   ├── calculator.py       # Core calculation logic
│   ├── database.py         # Database setup
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   └── main.py             # FastAPI app
│
├── frontend/               # Streamlit frontend
│   ├── pages/              # Multi-page app
│   ├── components/         # Reusable UI components
│   ├── services/           # API client
│   └── app.py              # Main app
│
├── data/                   # Data storage
│   ├── uploads/            # Uploaded files
│   ├── outputs/            # Generated Excel files
│   └── database/           # SQLite database
│
├── requirements.txt        # Python dependencies
├── run_backend.bat         # Start backend (Windows)
├── run_frontend.bat        # Start frontend (Windows)
└── README.md               # This file
```

## Calculation Logic

### Furniture Incentive Slabs
- < ₹20,000: 0%
- ₹20,000 - ₹40,000: 0.2%
- ₹40,000 - ₹80,000: 0.6%
- > ₹80,000: 1.0%

### Homeware Incentive Slabs
- ≤ ₹5,000: 0.5%
- ₹5,000 - ₹10,000: 0.8%
- > ₹10,000: 1.0%

### Role Distribution
- **With DM**: PE=60%, SM=15%, DM=25%
- **Without DM**: PE=70%, SM=30%

## Requirements

- Python 3.8 or higher
- Windows (or modify batch scripts for Linux/Mac)
- 10GB free disk space (for database and file storage)

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Make sure all dependencies are installed
- Check Python version: `python --version`

### Frontend won't start
- Make sure backend is running first
- Check if port 8501 is available
- Verify API_BASE_URL in `.env` file

### "Cannot connect to backend API"
- Ensure backend server is running
- Check firewall settings
- Verify URL in `frontend/config.py`

## Support

For issues or questions, refer to the implementation documentation:
- IMPLEMENTATION_PLAN.md
- HOMETOWN_INCENTIVE_AUTOMATION_DOCUMENTATION.md

## Version

1.0.0 - Initial MVP Release
