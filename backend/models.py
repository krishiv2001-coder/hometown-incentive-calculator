"""
SQLAlchemy ORM models for database tables
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Index
from datetime import datetime
from .database import Base

class Upload(Base):
    """Uploaded files metadata"""
    __tablename__ = "uploads"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_time = Column(DateTime, nullable=False, default=datetime.now)
    file_size = Column(Integer)

class Job(Base):
    """Processing jobs"""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    file_id = Column(String, ForeignKey("uploads.id"), nullable=False)
    status = Column(String, nullable=False, default="processing")  # processing, completed, failed
    progress = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    total_transactions = Column(Integer, nullable=True)
    total_incentives = Column(Float, nullable=True)
    employees_count = Column(Integer, nullable=True)
    stores_count = Column(Integer, nullable=True)

class Transaction(Base):
    """Individual sales transactions"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    store_code = Column(String)
    store_name = Column(String)
    sales_doc = Column(String)
    sales_date = Column(String)
    lob = Column(String)
    bill_no = Column(String)
    salesman = Column(String)
    net_sales_value = Column(Float)
    sales_without_gst = Column(Float)
    sm = Column(String)
    dm = Column(String)
    ince_amt = Column(Float)
    pe_inc_amt = Column(Float)
    sm_inc_amt = Column(Float)
    dm_inc_amt = Column(Float)

    __table_args__ = (
        Index('idx_transactions_job', 'job_id'),
        Index('idx_transactions_store_lob', 'store_code', 'lob'),
    )

class EmployeeSummary(Base):
    """Aggregated employee incentive summary"""
    __tablename__ = "employee_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    store_code = Column(String)
    store_name = Column(String)
    employee = Column(String)
    role = Column(String)
    furniture_points = Column(Float)
    homeware_points = Column(Float)
    total_points = Column(Float)

    __table_args__ = (
        Index('idx_summary_job', 'job_id'),
    )

class QualifierTracker(Base):
    """Store performance vs targets"""
    __tablename__ = "qualifier_tracker"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    store_code = Column(String)
    store_name = Column(String)
    lob = Column(String)
    actual_aov = Column(Integer)
    target_aov = Column(Integer)
    aov_achievement = Column(Float)
    actual_bills = Column(Integer)
    target_bills = Column(Integer)
    bills_achievement = Column(Float)
    status = Column(String)  # met_both, aov_met, bills_met, both_short

    __table_args__ = (
        Index('idx_tracker_job', 'job_id'),
    )
