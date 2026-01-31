"""
File upload API endpoint
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from pathlib import Path
from datetime import datetime
from ..database import get_db
from ..models import Upload
from ..schemas import UploadResponse
from ..config import UPLOAD_DIR

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload an Excel file for processing"""
    # Validate file type
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed")

    # Generate file ID
    file_id = str(uuid.uuid4())

    # Save file
    upload_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
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
    db.refresh(db_upload)

    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        upload_time=db_upload.upload_time,
        file_size=len(content)
    )
