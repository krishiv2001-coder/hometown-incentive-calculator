"""
File processing API endpoints
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from pathlib import Path
from ..database import get_db
from ..models import Job, Upload, Transaction, EmployeeSummary, QualifierTracker
from ..schemas import JobStatusResponse, JobResult
from ..calculator import process_incentives
from ..config import OUTPUT_DIR
import pandas as pd

router = APIRouter()

@router.post("/process/{file_id}")
async def process_file(file_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger processing of an uploaded file"""
    # Validate file exists
    upload = db.query(Upload).filter(Upload.id == file_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="File not found")

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
    """Background task for processing incentives"""
    try:
        # Update progress
        job = db.query(Job).filter(Job.id == job_id).first()
        job.progress = 10
        db.commit()

        # Load and process data
        df, summary_df, tracker_df, targets_df = process_incentives(file_path)
        job.progress = 50
        db.commit()

        # Save to database - Transactions
        for _, row in df.iterrows():
            transaction = Transaction(
                job_id=job_id,
                store_code=str(row['Store Code']),
                store_name=row['Name'],
                sales_doc=str(row['Sales_Doc']),
                sales_date=str(row['Sales Date']),
                lob=row['LOB'],
                bill_no=str(row['Bill No']),
                salesman=row['Salesman'],
                net_sales_value=float(row['Sum of NET SALES VALUE']),
                sales_without_gst=float(row['Sum of Sales value Without GST']),
                sm=row['SM'],
                dm=row['DM'],
                ince_amt=float(row['Ince Amt']),
                pe_inc_amt=float(row['PE Inc amt']),
                sm_inc_amt=float(row['SM Inc Amt']),
                dm_inc_amt=float(row['DM Inc Amt'])
            )
            db.add(transaction)

        job.progress = 60
        db.commit()

        # Save Employee Summary
        for _, row in summary_df.iterrows():
            summary = EmployeeSummary(
                job_id=job_id,
                store_code=str(row['Store Code']),
                store_name=row['Store Name'],
                employee=row['Employee'],
                role=row['Role'],
                furniture_points=float(row['Furniture Points']),
                homeware_points=float(row['Homeware Points']),
                total_points=float(row['Total Points'])
            )
            db.add(summary)

        job.progress = 70
        db.commit()

        # Save Qualifier Tracker
        for _, row in tracker_df.iterrows():
            tracker = QualifierTracker(
                job_id=job_id,
                store_code=str(row['Store Code']),
                store_name=row['Store Name'],
                lob=row['LOB'],
                actual_aov=int(row['Actual AOV']),
                target_aov=int(row['Target AOV']),
                aov_achievement=float(row['AOV Achievement %']),
                actual_bills=int(row['Actual Bills']),
                target_bills=int(row['Target Bills']),
                bills_achievement=float(row['Bills Achievement %']),
                status=row['Qualifier Status']
            )
            db.add(tracker)

        job.progress = 80
        db.commit()

        # Generate output Excel
        output_path = OUTPUT_DIR / f"{job_id}_Hometown_Incentives.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detailed Transactions', index=False)
            summary_df.to_excel(writer, sheet_name='Employee Points Summary', index=False)
            tracker_df.to_excel(writer, sheet_name='Daily Qualifier Tracker', index=False)
            targets_df.to_excel(writer, sheet_name='Monthly Targets', index=False)

        job.progress = 90
        db.commit()

        # Update job status
        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.now()
        job.total_transactions = len(df)
        job.total_incentives = float(df['Ince Amt'].sum())
        job.employees_count = len(summary_df)
        job.stores_count = int(df['Name'].nunique())
        db.commit()

    except Exception as e:
        job = db.query(Job).filter(Job.id == job_id).first()
        job.status = "failed"
        job.error = str(e)
        job.progress = 0
        db.commit()

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Get status of a processing job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress
    }

    if job.status == "completed":
        response["result"] = JobResult(
            total_transactions=job.total_transactions,
            total_incentives=job.total_incentives,
            employees_count=job.employees_count,
            stores_count=job.stores_count
        )
    elif job.status == "failed":
        response["error"] = job.error

    return response
