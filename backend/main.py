"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import upload, process, data
from .database import init_db
from .config import API_HOST, API_PORT

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Hometown Incentive API",
    description="Backend API for Hometown Sales Incentive Calculator",
    version="1.0.0"
)

# CORS middleware (allow Streamlit to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(process.router, prefix="/api/v1", tags=["process"])
app.include_router(data.router, prefix="/api/v1", tags=["data"])

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Hometown Incentive API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
