# Hometown Incentive Calculator - Frontend Implementation Plan

**Project**: Build Streamlit + FastAPI frontend for existing Python incentive calculator
**Approach**: MVP-first (2 weeks), Local deployment, Full upload history
**Current Status**: Backend complete and 100% validated

---

## Overview

Transform the existing command-line Python script into a user-friendly web application with:
- **Frontend**: Streamlit dashboard (file upload, interactive charts, data exploration)
- **Backend**: FastAPI REST API (wraps existing calculation logic)
- **Database**: SQLite (track upload history, enable filtering/search)
- **Users**: Management + Store Managers (view-only access to reports)

**Key Constraint**: Maintain 100% accuracy of existing calculation logic (₹5,23,929.52 validated)

---

## Architecture

```
┌─────────────────────────────────────┐
│  Streamlit Frontend (Port 8501)     │
│  - File Upload Page                 │
│  - Dashboard (Charts + KPIs)        │
│  - Upload History Browser           │
└─────────────────────────────────────┘
            ↕ HTTP REST API
┌─────────────────────────────────────┐
│  FastAPI Backend (Port 8000)        │
│  - /upload (save file)              │
│  - /process (run calculations)      │
│  - /data/* (query results)          │
└─────────────────────────────────────┘
            ↕
┌─────────────────────────────────────┐
│  Core Calculator Module             │
│  (existing hometown_incentive_      │
│   calculator.py - REUSE AS-IS)      │
└─────────────────────────────────────┘
            ↕
┌─────────────────────────────────────┐
│  SQLite Database (hometown.db)      │
│  - uploads, jobs, transactions,     │
│    employee_summary, tracker        │
└─────────────────────────────────────┘
```

---

## MVP Feature Scope (2 Weeks)

### Week 1: Backend + Database Foundation
**Goal**: Working API that processes files and stores results

**Features**:
1. ✅ File upload endpoint (accepts .xlsx)
2. ✅ Processing endpoint (runs existing calculator)
3. ✅ SQLite database setup (5 tables)
4. ✅ Data query endpoints (summary, tracker, transactions)
5. ✅ File storage system (uploads/, outputs/)

**Skip for MVP**:
- ❌ WebSocket real-time updates (use polling instead)
- ❌ Authentication (add later)
- ❌ Advanced caching (keep simple)

### Week 2: Frontend Dashboard
**Goal**: User-friendly interface for upload and viewing results

**Features**:
1. ✅ Upload page (drag-drop, file validation, process trigger)
2. ✅ Dashboard page (KPI cards + 3-4 key charts)
3. ✅ History page (view past uploads, download results)
4. ✅ Basic filtering (by store, LOB, role)

**Skip for MVP**:
- ❌ Advanced employee search (add in Phase 2)
- ❌ Real-time qualifier tracker page (show in dashboard instead)
- ❌ Custom target editing UI (edit in database or Excel for now)

---

## Project Structure

```
hometown-incentive-frontend/
│
├── backend/
│   ├── main.py                    # FastAPI app entry
│   ├── config.py                  # Settings (ports, paths)
│   ├── database.py                # SQLAlchemy setup
│   ├── models.py                  # ORM models (5 tables)
│   ├── schemas.py                 # Pydantic schemas
│   ├── calculator.py              # Refactored from existing script
│   └── api/
│       ├── upload.py              # POST /api/upload
│       ├── process.py             # POST /api/process/{file_id}
│       └── data.py                # GET /api/data/*
│
├── frontend/
│   ├── app.py                     # Main Streamlit entry
│   ├── config.py                  # API URL config
│   ├── pages/
│   │   ├── 1_📤_Upload.py        # Upload page
│   │   ├── 2_📊_Dashboard.py     # Analytics dashboard
│   │   └── 3_📜_History.py       # Upload history
│   ├── components/
│   │   └── charts.py              # Plotly chart functions
│   └── services/
│       └── api_client.py          # API communication
│
├── data/
│   ├── uploads/                   # User-uploaded files
│   ├── outputs/                   # Generated Excel files
│   └── database/
│       └── hometown.db            # SQLite database
│
├── requirements.txt               # All dependencies
├── .env                           # Configuration
├── run_backend.bat                # Start FastAPI (Windows)
├── run_frontend.bat               # Start Streamlit (Windows)
└── README.md                      # Setup instructions
```

---

## API Endpoints (FastAPI)

### 1. Upload File
```
POST /api/v1/upload
Content-Type: multipart/form-data

Request:
  - file: Excel file (.xlsx)

Response:
  {
    "file_id": "uuid",
    "filename": "IncentiveWorking.xlsx",
    "upload_time": "2026-01-31T10:30:00Z",
    "file_size": 1880730
  }
```

### 2. Process File
```
POST /api/v1/process/{file_id}

Response:
  {
    "job_id": "uuid",
    "status": "processing"
  }
```

### 3. Check Status
```
GET /api/v1/jobs/{job_id}

Response:
  {
    "job_id": "uuid",
    "status": "completed",  // or "processing", "failed"
    "progress": 100,
    "result": {
      "total_transactions": 8535,
      "total_incentives": 523929.52,
      "employees_count": 147,
      "stores_count": 14
    }
  }
```

### 4. Get Data
```
GET /api/v1/data/summary?store_code=6098&lob=Furniture

Response:
  {
    "data": [
      {
        "store_code": "6098",
        "store_name": "HT - GUWAHATI",
        "employee": "NAKUL GOGOI",
        "role": "DM",
        "furniture_points": 9937.10,
        "homeware_points": 0.00,
        "total_points": 9937.10
      },
      ...
    ]
  }

GET /api/v1/data/tracker?job_id={job_id}
GET /api/v1/data/transactions?job_id={job_id}
GET /api/v1/data/statistics?job_id={job_id}
```

### 5. Download Output
```
GET /api/v1/download/{job_id}

Response:
  Excel file download
```

### 6. List Uploads
```
GET /api/v1/history?limit=10&offset=0

Response:
  {
    "uploads": [
      {
        "job_id": "uuid",
        "filename": "IncentiveWorking.xlsx",
        "upload_time": "2026-01-31T10:30:00Z",
        "total_incentives": 523929.52,
        "status": "completed"
      },
      ...
    ]
  }
```

---

## Database Schema (SQLite)

### Table: uploads
```sql
CREATE TABLE uploads (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    upload_time TIMESTAMP NOT NULL,
    file_size INTEGER
);
```

### Table: jobs
```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    file_id TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'processing', 'completed', 'failed'
    progress INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT,
    total_transactions INTEGER,
    total_incentives REAL,
    employees_count INTEGER,
    stores_count INTEGER,
    FOREIGN KEY (file_id) REFERENCES uploads(id)
);
```

### Table: transactions
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    store_code TEXT,
    store_name TEXT,
    sales_doc TEXT,
    sales_date DATE,
    lob TEXT,
    bill_no TEXT,
    salesman TEXT,
    net_sales_value REAL,
    sales_without_gst REAL,
    sm TEXT,
    dm TEXT,
    ince_amt REAL,
    pe_inc_amt REAL,
    sm_inc_amt REAL,
    dm_inc_amt REAL,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE INDEX idx_transactions_job ON transactions(job_id);
CREATE INDEX idx_transactions_store_lob ON transactions(store_code, lob);
```

### Table: employee_summary
```sql
CREATE TABLE employee_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    store_code TEXT,
    store_name TEXT,
    employee TEXT,
    role TEXT,
    furniture_points REAL,
    homeware_points REAL,
    total_points REAL,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE INDEX idx_summary_job ON employee_summary(job_id);
```

### Table: qualifier_tracker
```sql
CREATE TABLE qualifier_tracker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    store_code TEXT,
    store_name TEXT,
    lob TEXT,
    actual_aov INTEGER,
    target_aov INTEGER,
    aov_achievement REAL,
    actual_bills INTEGER,
    target_bills INTEGER,
    bills_achievement REAL,
    status TEXT,  -- 'met_both', 'aov_met', 'bills_met', 'both_short'
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE INDEX idx_tracker_job ON qualifier_tracker(job_id);
```

---

## Frontend Pages

### Page 1: Upload (1_📤_Upload.py)

**UI Components**:
```python
st.title("📤 Upload Sales Data")

# File uploader
uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=['xlsx'],
    help="Upload BI export (Sales Report - Hometown (2) sheet)"
)

if uploaded_file:
    # Show file info
    st.info(f"{uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)")

    # Validate columns
    preview = pd.read_excel(uploaded_file, nrows=5)
    required_cols = ['Store Code', 'Name', 'Sales_Doc', ...]

    if all(col in preview.columns for col in required_cols):
        st.success("✅ File validated")

        # Preview table
        with st.expander("Preview (5 rows)"):
            st.dataframe(preview)

        # Process button
        if st.button("🚀 Process File", type="primary"):
            # 1. Upload to API
            file_id = api_client.upload(uploaded_file)

            # 2. Trigger processing
            job_id = api_client.process(file_id)

            # 3. Poll status
            progress = st.progress(0)
            while True:
                status = api_client.get_status(job_id)
                progress.progress(status['progress'])

                if status['status'] == 'completed':
                    st.success("✅ Complete!")

                    # Show summary
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Transactions", status['result']['total_transactions'])
                    col2.metric("Incentives", f"₹{status['result']['total_incentives']:,.2f}")
                    col3.metric("Employees", status['result']['employees_count'])
                    col4.metric("Stores", status['result']['stores_count'])

                    # Download button
                    st.download_button(
                        "📥 Download Results",
                        data=api_client.download(job_id),
                        file_name=f"Hometown_Incentives_{datetime.now():%Y%m%d}.xlsx"
                    )

                    # Link to dashboard
                    st.info("👉 View results in Dashboard")
                    break

                elif status['status'] == 'failed':
                    st.error(f"Error: {status['error']}")
                    break

                time.sleep(1)
    else:
        st.error("Missing required columns")
```

### Page 2: Dashboard (2_📊_Dashboard.py)

**Layout**:
```python
st.title("📊 Analytics Dashboard")

# Get latest job (or select from dropdown)
jobs = api_client.get_history(limit=10)
selected_job = st.selectbox("Select Upload", jobs, format_func=lambda x: f"{x['filename']} - {x['upload_time']}")

if selected_job:
    # Fetch data
    stats = api_client.get_statistics(selected_job['job_id'])
    summary = api_client.get_summary(selected_job['job_id'])
    tracker = api_client.get_tracker(selected_job['job_id'])

    # KPI Cards
    st.subheader("Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Sales", f"₹{stats['total_sales']:,.0f}")
    col2.metric("Total Incentives", f"₹{stats['total_incentives']:,.2f}")
    col3.metric("Transactions", f"{stats['total_transactions']:,}")
    col4.metric("Employees", stats['employees_count'])
    col5.metric("Stores", stats['stores_count'])

    # Filters
    with st.sidebar:
        st.header("Filters")
        selected_stores = st.multiselect("Store", stats['stores'])
        selected_lob = st.selectbox("LOB", ["All", "Furniture", "Homeware"])
        selected_role = st.multiselect("Role", ["PE", "SM", "DM"])

    # Apply filters
    filtered_summary = apply_filters(summary, selected_stores, selected_lob, selected_role)

    # Charts
    st.subheader("Performance Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Store Performance Bar Chart
        fig1 = px.bar(
            filtered_summary.groupby('store_name')['total_points'].sum().reset_index(),
            x='store_name',
            y='total_points',
            title='Total Incentives by Store',
            labels={'total_points': 'Incentives (₹)', 'store_name': 'Store'}
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # LOB Breakdown Pie Chart
        lob_data = filtered_summary.groupby('lob')[['furniture_points', 'homeware_points']].sum()
        fig2 = px.pie(
            values=[lob_data['furniture_points'].sum(), lob_data['homeware_points'].sum()],
            names=['Furniture', 'Homeware'],
            title='Incentive Split by LOB',
            hole=0.4
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # Top 10 Employees
        top_10 = filtered_summary.nlargest(10, 'total_points')
        fig3 = px.bar(
            top_10,
            x='total_points',
            y='employee',
            color='role',
            orientation='h',
            title='Top 10 Performers'
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Qualifier Status
        tracker_counts = tracker['status'].value_counts()
        fig4 = px.bar(
            x=tracker_counts.index,
            y=tracker_counts.values,
            title='Qualifier Status',
            labels={'x': 'Status', 'y': 'Count'}
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Qualifier Tracker Table
    st.subheader("Qualifier Tracker")
    st.dataframe(
        tracker,
        use_container_width=True,
        column_config={
            "actual_aov": st.column_config.NumberColumn("Actual AOV", format="₹%d"),
            "target_aov": st.column_config.NumberColumn("Target AOV", format="₹%d"),
            "aov_achievement": st.column_config.ProgressColumn("AOV %", min_value=0, max_value=200),
            "bills_achievement": st.column_config.ProgressColumn("Bills %", min_value=0, max_value=200)
        }
    )

    # Employee Summary Table
    st.subheader("Employee Summary")
    st.dataframe(
        filtered_summary,
        use_container_width=True,
        column_config={
            "furniture_points": st.column_config.NumberColumn("Furniture", format="₹%.2f"),
            "homeware_points": st.column_config.NumberColumn("Homeware", format="₹%.2f"),
            "total_points": st.column_config.NumberColumn("Total", format="₹%.2f")
        }
    )
```

### Page 3: History (3_📜_History.py)

**UI Components**:
```python
st.title("📜 Upload History")

# Fetch all uploads
history = api_client.get_history(limit=50)

if history:
    # Summary stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Uploads", len(history))
    col2.metric("Total Processed", sum(1 for h in history if h['status'] == 'completed'))
    col3.metric("Latest Upload", history[0]['upload_time'])

    # History table
    st.subheader("All Uploads")

    for upload in history:
        with st.expander(f"{upload['filename']} - {upload['upload_time']}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Job ID**: {upload['job_id'][:8]}...")
                st.write(f"**Status**: {upload['status']}")
                st.write(f"**Upload Time**: {upload['upload_time']}")
                st.write(f"**File Size**: {upload['file_size']/1024:.1f} KB")

                if upload['status'] == 'completed':
                    st.write(f"**Total Incentives**: ₹{upload['total_incentives']:,.2f}")
                    st.write(f"**Transactions**: {upload['total_transactions']:,}")
                    st.write(f"**Employees**: {upload['employees_count']}")

            with col2:
                if upload['status'] == 'completed':
                    if st.button("📥 Download", key=f"dl_{upload['job_id']}"):
                        file_data = api_client.download(upload['job_id'])
                        st.download_button(
                            "Save File",
                            file_data,
                            file_name=f"Hometown_Incentives_{upload['job_id'][:8]}.xlsx"
                        )

                    if st.button("📊 View Dashboard", key=f"view_{upload['job_id']}"):
                        st.session_state.selected_job = upload['job_id']
                        st.switch_page("pages/2_📊_Dashboard.py")
else:
    st.info("No uploads yet. Go to Upload page to get started.")
```

---

## Implementation Steps

### Step 1: Project Setup
```bash
# Create project directory
mkdir hometown-incentive-frontend
cd hometown-incentive-frontend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Create project structure
mkdir backend frontend data data\uploads data\outputs data\database
mkdir backend\api frontend\pages frontend\components frontend\services

# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic python-multipart
pip install streamlit plotly pandas openpyxl requests
pip freeze > requirements.txt
```

### Step 2: Backend Implementation

**File: backend/calculator.py**
- Copy existing `hometown_incentive_calculator (1).py`
- Refactor into reusable functions (no `if __name__ == "__main__"`)
- Keep all calculation logic identical (100% accuracy critical)

**File: backend/database.py**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./data/database/hometown.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**File: backend/models.py**
- Define 5 SQLAlchemy ORM models (uploads, jobs, transactions, employee_summary, qualifier_tracker)
- Match schema defined above

**File: backend/schemas.py**
- Define Pydantic models for API requests/responses
- Example: `UploadResponse`, `JobStatus`, `EmployeeSummary`, etc.

**File: backend/api/upload.py**
```python
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import uuid
from pathlib import Path
from datetime import datetime
from ..database import get_db
from ..models import Upload

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Generate file ID
    file_id = str(uuid.uuid4())

    # Save file
    upload_path = Path(f"data/uploads/{file_id}_{file.filename}")
    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Store metadata in database
    db_upload = Upload(
        id=file_id,
        filename=file.filename,
        file_path=str(upload_path),
        upload_time=datetime.now(),
        file_size=len(content)
    )
    db.add(db_upload)
    db.commit()

    return {
        "file_id": file_id,
        "filename": file.filename,
        "upload_time": db_upload.upload_time,
        "file_size": len(content)
    }
```

**File: backend/api/process.py**
```python
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
import uuid
from ..database import get_db
from ..models import Job, Upload, Transaction, EmployeeSummary, QualifierTracker
from ..calculator import load_sales_data, process_calculations, create_employee_summary, create_qualifier_tracker, create_dummy_targets
import pandas as pd

router = APIRouter()

@router.post("/process/{file_id}")
async def process_file(file_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Validate file exists
    upload = db.query(Upload).filter(Upload.id == file_id).first()
    if not upload:
        return {"error": "File not found"}, 404

    # Create job
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        file_id=file_id,
        status="processing",
        progress=0,
        started_at=datetime.now()
    )
    db.add(job)
    db.commit()

    # Process in background
    background_tasks.add_task(process_incentives_background, job_id, upload.file_path, db)

    return {"job_id": job_id, "status": "processing"}

def process_incentives_background(job_id: str, file_path: str, db: Session):
    try:
        # Update progress
        job = db.query(Job).filter(Job.id == job_id).first()
        job.progress = 10
        db.commit()

        # Load data
        df = load_sales_data(file_path)
        job.progress = 30
        db.commit()

        # Calculate incentives
        df = process_calculations(df)
        job.progress = 50
        db.commit()

        # Create summaries
        summary_df = create_employee_summary(df)
        targets_df = create_dummy_targets(sorted(df['Name'].unique()))
        tracker_df = create_qualifier_tracker(df, targets_df)
        job.progress = 70
        db.commit()

        # Save to database
        for _, row in df.iterrows():
            transaction = Transaction(
                job_id=job_id,
                store_code=row['Store Code'],
                store_name=row['Name'],
                # ... all other fields
            )
            db.add(transaction)

        for _, row in summary_df.iterrows():
            summary = EmployeeSummary(
                job_id=job_id,
                # ... fields
            )
            db.add(summary)

        for _, row in tracker_df.iterrows():
            tracker = QualifierTracker(
                job_id=job_id,
                # ... fields
            )
            db.add(tracker)

        job.progress = 90
        db.commit()

        # Generate output Excel
        output_path = f"data/outputs/{job_id}_Hometown_Incentives.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detailed Transactions', index=False)
            summary_df.to_excel(writer, sheet_name='Employee Points Summary', index=False)
            tracker_df.to_excel(writer, sheet_name='Daily Qualifier Tracker', index=False)
            targets_df.to_excel(writer, sheet_name='Monthly Targets', index=False)

        # Update job status
        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.now()
        job.total_transactions = len(df)
        job.total_incentives = df['Ince Amt'].sum()
        job.employees_count = len(summary_df)
        job.stores_count = df['Name'].nunique()
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        db.commit()
```

**File: backend/api/data.py**
- Implement GET endpoints for summary, tracker, transactions, statistics
- Use SQLAlchemy queries with filters

**File: backend/main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import upload, process, data
from .database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hometown Incentive API", version="1.0")

# CORS (allow Streamlit to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(process.router, prefix="/api/v1", tags=["process"])
app.include_router(data.router, prefix="/api/v1", tags=["data"])

@app.get("/")
def root():
    return {"message": "Hometown Incentive API", "version": "1.0"}
```

### Step 3: Frontend Implementation

**File: frontend/services/api_client.py**
```python
import requests
from typing import Optional

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url

    def upload(self, file) -> str:
        files = {"file": (file.name, file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = requests.post(f"{self.base_url}/upload", files=files)
        response.raise_for_status()
        return response.json()["file_id"]

    def process(self, file_id: str) -> str:
        response = requests.post(f"{self.base_url}/process/{file_id}")
        response.raise_for_status()
        return response.json()["job_id"]

    def get_status(self, job_id: str) -> dict:
        response = requests.get(f"{self.base_url}/jobs/{job_id}")
        response.raise_for_status()
        return response.json()

    def get_summary(self, job_id: str, **filters) -> dict:
        response = requests.get(f"{self.base_url}/data/summary", params={"job_id": job_id, **filters})
        response.raise_for_status()
        return response.json()

    # ... other methods
```

**File: frontend/components/charts.py**
- Implement Plotly chart functions (4-5 key charts)
- Keep consistent styling (colors, fonts)

**File: frontend/pages/1_📤_Upload.py, 2_📊_Dashboard.py, 3_📜_History.py**
- Implement as detailed in "Frontend Pages" section above

**File: frontend/app.py**
```python
import streamlit as st

st.set_page_config(
    page_title="Hometown Incentive Calculator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 Hometown Incentive Calculator")

st.markdown("""
Welcome to the Hometown Sales Incentive Automation System.

**Quick Start:**
1. 📤 **Upload**: Upload your sales data Excel file
2. 📊 **Dashboard**: View analytics and performance metrics
3. 📜 **History**: Browse past uploads and download results

---

**Current Status**: Ready to process files
""")

# Quick stats from latest upload (if any)
from services.api_client import APIClient

api_client = APIClient()

try:
    history = api_client.get_history(limit=1)
    if history:
        latest = history[0]
        st.info(f"Latest upload: {latest['filename']} ({latest['upload_time']})")

        if latest['status'] == 'completed':
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Incentives", f"₹{latest['total_incentives']:,.2f}")
            col2.metric("Transactions", f"{latest['total_transactions']:,}")
            col3.metric("Employees", latest['employees_count'])
            col4.metric("Stores", latest['stores_count'])
except:
    st.warning("Backend API not running. Start with: python -m uvicorn backend.main:app")
```

### Step 4: Configuration & Launch

**File: .env**
```
# Backend
API_HOST=127.0.0.1
API_PORT=8000
DATABASE_URL=sqlite:///./data/database/hometown.db

# Frontend
STREAMLIT_PORT=8501
API_BASE_URL=http://127.0.0.1:8000/api/v1
```

**File: run_backend.bat** (Windows)
```batch
@echo off
call venv\Scripts\activate
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
pause
```

**File: run_frontend.bat** (Windows)
```batch
@echo off
call venv\Scripts\activate
streamlit run frontend\app.py --server.port 8501
pause
```

**File: requirements.txt**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
pandas==2.1.3
openpyxl==3.1.2
streamlit==1.30.0
plotly==5.18.0
requests==2.31.0
```

---

## Critical Files to Modify

1. **c:\Users\User\OneDrive - Florintree Managers Pvt. Ltd\Desktop\Frontend\hometown_incentive_calculator (1).py**
   - Refactor into `backend/calculator.py`
   - Remove `if __name__ == "__main__"` block
   - Keep all calculation logic identical
   - Export functions: `load_sales_data`, `process_calculations`, `create_employee_summary`, `create_qualifier_tracker`, `create_dummy_targets`

2. **backend/main.py** (NEW)
   - FastAPI application setup
   - Router registration
   - CORS middleware

3. **backend/api/process.py** (NEW)
   - Core processing endpoint
   - Background task for incentive calculation
   - Database persistence

4. **frontend/pages/2_📊_Dashboard.py** (NEW)
   - Primary user interface
   - KPI cards, charts, tables
   - Most complex UI component

5. **frontend/services/api_client.py** (NEW)
   - API communication layer
   - Handles all HTTP requests
   - Error handling

---

## Verification & Testing

### Test Plan

**Test 1: Backend API**
```bash
# Start backend
python -m uvicorn backend.main:app --reload

# Test upload (using curl or Postman)
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@IncentiveWorking_Krishiv.xlsx"

# Verify response contains file_id
```

**Test 2: Processing Accuracy**
```python
# After processing completes, verify total incentives match
# Expected: ₹5,23,929.52 (from documentation)

import requests
response = requests.get(f"http://localhost:8000/api/v1/jobs/{job_id}")
assert response.json()['result']['total_incentives'] == 523929.52
```

**Test 3: Frontend Integration**
```bash
# Start frontend
streamlit run frontend/app.py

# Manual test:
# 1. Upload IncentiveWorking_Krishiv.xlsx
# 2. Wait for processing
# 3. Verify totals match documentation:
#    - Total: ₹5,23,929.52
#    - PE: ₹3,20,448.04
#    - SM: ₹87,724.92
#    - DM: ₹1,15,756.56
# 4. Download output Excel
# 5. Verify 4 sheets present
```

**Test 4: Database Persistence**
```sql
-- Check data saved correctly
sqlite3 data/database/hometown.db

SELECT COUNT(*) FROM transactions;  -- Should be 8535
SELECT SUM(ince_amt) FROM transactions;  -- Should be 523929.52
SELECT COUNT(DISTINCT employee) FROM employee_summary;  -- Should be 147
```

---

## Success Criteria

✅ **Accuracy**: Total incentives match existing Excel (₹5,23,929.52)
✅ **Functionality**: All 3 pages working (Upload, Dashboard, History)
✅ **Performance**: Process 8,535 transactions in < 10 seconds
✅ **Persistence**: All uploads saved to database with full history
✅ **Usability**: Non-technical user can upload file and view results without help

---

## Known Limitations (MVP)

1. **No Authentication** - Anyone with access can use (OK for local development)
2. **No Advanced Search** - Basic filtering only (add in Phase 2)
3. **No Real-time Updates** - Uses polling instead of WebSocket (simpler for MVP)
4. **No Target Editing UI** - Edit targets in database or Excel manually
5. **Local Only** - Not deployed to cloud (intentional for MVP)

---

## Next Steps After MVP

**Phase 2 (Post-MVP Enhancements)**:
1. Add advanced employee search page
2. Implement real-time qualifier tracker with WebSocket
3. Add target editing UI
4. Implement simple authentication (password protection)
5. Add data export to multiple formats (CSV, PDF reports)
6. Create comparison view (month-over-month analysis)

**Phase 3 (Production Deployment)**:
1. Deploy to cloud (Streamlit Cloud + Railway)
2. Implement proper user authentication
3. Add role-based access control
4. Integrate with N8N for automation
5. Add email notifications for processing completion

---

## Questions Before Starting?

Before implementing, verify:
- [ ] Existing script location confirmed: `hometown_incentive_calculator (1).py`
- [ ] Sample data file available: `IncentiveWorking_Krishiv.xlsx`
- [ ] Python 3.8+ installed
- [ ] Comfortable with command line (running .bat files)
- [ ] Have ~10GB free disk space (for database + file storage)

**Ready to proceed with implementation?**
