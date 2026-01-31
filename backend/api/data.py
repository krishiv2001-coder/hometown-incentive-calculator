"""
Data query API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from ..database import get_db
from ..models import Job, Upload, EmployeeSummary, Transaction, QualifierTracker
from ..schemas import (
    EmployeeSummaryItem, TransactionItem, QualifierTrackerItem,
    HistoryItem, StatisticsResponse
)
from ..config import OUTPUT_DIR

router = APIRouter()

@router.get("/data/summary", response_model=List[EmployeeSummaryItem])
async def get_summary(
    job_id: str,
    store_code: Optional[str] = None,
    lob: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get employee summary data with optional filters"""
    query = db.query(EmployeeSummary).filter(EmployeeSummary.job_id == job_id)

    if store_code:
        query = query.filter(EmployeeSummary.store_code == store_code)
    if role:
        query = query.filter(EmployeeSummary.role == role)

    results = query.all()
    return results

@router.get("/data/tracker", response_model=List[QualifierTrackerItem])
async def get_tracker(job_id: str, db: Session = Depends(get_db)):
    """Get qualifier tracker data"""
    results = db.query(QualifierTracker).filter(QualifierTracker.job_id == job_id).all()
    return results

@router.get("/data/transactions", response_model=List[TransactionItem])
async def get_transactions(
    job_id: str,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get transaction data with pagination"""
    results = db.query(Transaction).filter(
        Transaction.job_id == job_id
    ).offset(offset).limit(limit).all()
    return results

@router.get("/data/statistics", response_model=StatisticsResponse)
async def get_statistics(job_id: str, db: Session = Depends(get_db)):
    """Get aggregate statistics for a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get total sales
    total_sales = db.query(func.sum(Transaction.sales_without_gst)).filter(
        Transaction.job_id == job_id
    ).scalar() or 0

    # Get unique stores and LOBs
    stores = db.query(Transaction.store_name).filter(
        Transaction.job_id == job_id
    ).distinct().all()
    stores = [s[0] for s in stores]

    lobs = db.query(Transaction.lob).filter(
        Transaction.job_id == job_id
    ).distinct().all()
    lobs = [l[0] for l in lobs]

    return StatisticsResponse(
        total_sales=float(total_sales),
        total_incentives=float(job.total_incentives or 0),
        total_transactions=job.total_transactions or 0,
        employees_count=job.employees_count or 0,
        stores_count=job.stores_count or 0,
        stores=stores,
        lobs=lobs
    )

@router.get("/download/{job_id}")
async def download_output(job_id: str, db: Session = Depends(get_db)):
    """Download processed output file"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    output_path = OUTPUT_DIR / f"{job_id}_Hometown_Incentives.xlsx"
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        path=output_path,
        filename=f"Hometown_Incentives_{job_id[:8]}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/history", response_model=List[HistoryItem])
async def get_history(
    limit: int = Query(10, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get upload history"""
    # Join uploads and jobs
    results = db.query(
        Job.id.label('job_id'),
        Upload.filename,
        Upload.upload_time,
        Upload.file_size,
        Job.status,
        Job.total_incentives,
        Job.total_transactions,
        Job.employees_count,
        Job.stores_count
    ).join(Upload, Upload.id == Job.file_id).order_by(
        Upload.upload_time.desc()
    ).offset(offset).limit(limit).all()

    return [
        HistoryItem(
            job_id=r.job_id,
            filename=r.filename,
            upload_time=r.upload_time,
            status=r.status,
            total_incentives=r.total_incentives,
            total_transactions=r.total_transactions,
            employees_count=r.employees_count,
            stores_count=r.stores_count,
            file_size=r.file_size
        ) for r in results
    ]
