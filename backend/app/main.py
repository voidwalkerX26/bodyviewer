from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

# Import API routes
from app.api.routes import scan, scans

# Create app
app = FastAPI(title="VoxelFit API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scan.router, prefix="/api/scan", tags=["scan"])
app.include_router(scans.router, prefix="/api/scans", tags=["scans"])

# Create scans directory if it doesn't exist
SCANS_DIR = Path("./scans")
SCANS_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {"message": "VoxelFit API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)