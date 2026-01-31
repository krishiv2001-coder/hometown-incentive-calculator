"""
API Client for communicating with FastAPI backend
"""
import requests
from typing import Optional, Dict, List
import pandas as pd
from io import BytesIO

class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/v1"):
        self.base_url = base_url

    def upload(self, file) -> str:
        """Upload a file and return file_id"""
        files = {"file": (file.name, file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = requests.post(f"{self.base_url}/upload", files=files)
        response.raise_for_status()
        return response.json()["file_id"]

    def process(self, file_id: str) -> str:
        """Trigger processing and return job_id"""
        response = requests.post(f"{self.base_url}/process/{file_id}")
        response.raise_for_status()
        return response.json()["job_id"]

    def get_status(self, job_id: str) -> dict:
        """Get job status"""
        response = requests.get(f"{self.base_url}/jobs/{job_id}")
        response.raise_for_status()
        return response.json()

    def get_summary(self, job_id: str, **filters) -> pd.DataFrame:
        """Get employee summary data"""
        params = {"job_id": job_id, **filters}
        response = requests.get(f"{self.base_url}/data/summary", params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return pd.DataFrame(data)
        return pd.DataFrame()

    def get_tracker(self, job_id: str) -> pd.DataFrame:
        """Get qualifier tracker data"""
        response = requests.get(f"{self.base_url}/data/tracker", params={"job_id": job_id})
        response.raise_for_status()
        data = response.json()
        if data:
            return pd.DataFrame(data)
        return pd.DataFrame()

    def get_transactions(self, job_id: str, limit: int = 100, offset: int = 0) -> pd.DataFrame:
        """Get transaction data"""
        params = {"job_id": job_id, "limit": limit, "offset": offset}
        response = requests.get(f"{self.base_url}/data/transactions", params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return pd.DataFrame(data)
        return pd.DataFrame()

    def get_statistics(self, job_id: str) -> dict:
        """Get aggregate statistics"""
        response = requests.get(f"{self.base_url}/data/statistics", params={"job_id": job_id})
        response.raise_for_status()
        return response.json()

    def download(self, job_id: str) -> bytes:
        """Download output Excel file"""
        response = requests.get(f"{self.base_url}/download/{job_id}")
        response.raise_for_status()
        return response.content

    def get_history(self, limit: int = 10, offset: int = 0) -> List[dict]:
        """Get upload history"""
        params = {"limit": limit, "offset": offset}
        response = requests.get(f"{self.base_url}/history", params=params)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> bool:
        """Check if API is accessible"""
        try:
            response = requests.get(f"{self.base_url.replace('/api/v1', '')}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
