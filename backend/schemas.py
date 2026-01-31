"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Upload schemas
class UploadResponse(BaseModel):
    file_id: str
    filename: str
    upload_time: datetime
    file_size: int

    class Config:
        from_attributes = True

# Job schemas
class JobCreate(BaseModel):
    file_id: str

class JobResult(BaseModel):
    total_transactions: int
    total_incentives: float
    employees_count: int
    stores_count: int

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    result: Optional[JobResult] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True

# Data schemas
class EmployeeSummaryItem(BaseModel):
    store_code: str
    store_name: str
    employee: str
    role: str
    furniture_points: float
    homeware_points: float
    total_points: float

    class Config:
        from_attributes = True

class TransactionItem(BaseModel):
    store_code: Optional[str]
    store_name: Optional[str]
    sales_doc: Optional[str]
    sales_date: Optional[str]
    lob: Optional[str]
    bill_no: Optional[str]
    salesman: Optional[str]
    net_sales_value: Optional[float]
    sales_without_gst: Optional[float]
    sm: Optional[str]
    dm: Optional[str]
    ince_amt: Optional[float]
    pe_inc_amt: Optional[float]
    sm_inc_amt: Optional[float]
    dm_inc_amt: Optional[float]

    class Config:
        from_attributes = True

class QualifierTrackerItem(BaseModel):
    store_code: Optional[str]
    store_name: Optional[str]
    lob: Optional[str]
    actual_aov: Optional[int]
    target_aov: Optional[int]
    aov_achievement: Optional[float]
    actual_bills: Optional[int]
    target_bills: Optional[int]
    bills_achievement: Optional[float]
    status: Optional[str]

    class Config:
        from_attributes = True

class HistoryItem(BaseModel):
    job_id: str
    filename: str
    upload_time: datetime
    status: str
    total_incentives: Optional[float] = None
    total_transactions: Optional[int] = None
    employees_count: Optional[int] = None
    stores_count: Optional[int] = None
    file_size: Optional[int] = None

    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    total_sales: float
    total_incentives: float
    total_transactions: int
    employees_count: int
    stores_count: int
    stores: List[str]
    lobs: List[str]

    class Config:
        from_attributes = True
