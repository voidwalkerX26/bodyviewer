from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# Import processing module
from app.ml.processing import process_scan

router = APIRouter()

# Scans directory
SCANS_DIR = Path("./scans")
SCANS_DIR.mkdir(exist_ok=True)

def process_scan_background(scan_id: str, height_cm: float = None):
    """
    Background task to process scan with MediaPipe pose estimation and height calibration
    """
    scan_dir = SCANS_DIR / scan_id
    if not scan_dir.exists():
        return

    # Process the scan with height calibration
    result = process_scan(scan_id, scan_dir, height_cm)
    # Result is already saved to files by process_scan function

@router.post("/upload")
async def upload_scan(
    front: UploadFile = File(...),
    side: UploadFile = File(...),
    height: str = Form(None),
    background_tasks: BackgroundTasks = None
):
    """
    Upload endpoint that stores files, height, and starts background processing
    """
    # Validate file types
    if not front.content_type.startswith("image/") or not side.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Files must be images")

    # Validate height if provided
    height_cm = None
    if height:
        try:
            height_cm = float(height)
            if height_cm <= 0 or height_cm > 300:  # Reasonable human height limits
                raise ValueError("Height out of realistic range")
        except ValueError:
            raise HTTPException(status_code=400, detail="Height must be a valid positive number")

    # Create scan directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scan_id = f"scan_{timestamp}"
    scan_dir = SCANS_DIR / scan_id
    scan_dir.mkdir(exist_ok=True)

    # Save front image
    front_path = scan_dir / "front.jpg"
    with front_path.open("wb") as buffer:
        shutil.copyfileobj(front.file, buffer)

    # Save side image
    side_path = scan_dir / "side.jpg"
    with side_path.open("wb") as buffer:
        shutil.copyfileobj(side.file, buffer)

    # Save height info for reference
    if height_cm:
        height_path = scan_dir / "height.txt"
        with height_path.open("w") as f:
            f.write(str(height_cm))

    # Start background processing
    if background_tasks:
        background_tasks.add_task(process_scan_background, scan_id, height_cm)

    return JSONResponse({
        "scan_id": scan_id,
        "status": "uploaded",
        "message": "Images uploaded successfully, processing started",
        "files": ["front.jpg", "side.jpg", "height.txt" if height_cm else None]
    })

@router.get("/{scan_id}/status")
async def get_scan_status(scan_id: str):
    """
    Get scan processing status
    """
    scan_dir = SCANS_DIR / scan_id
    if not scan_dir.exists():
        raise HTTPException(status_code=404, detail="Scan not found")

    # Check if processing is complete
    has_mesh = (scan_dir / "mesh.ply").exists()  # Changed from .glb to .ply
    has_measurements = (scan_dir / "measurements.json").exists()

    if has_mesh and has_measurements:
        status = "completed"
    elif (scan_dir / "front.jpg").exists() and (scan_dir / "side.jpg").exists():
        status = "processing"  # Changed from uploaded to processing since we start immediately
    else:
        status = "unknown"

    # Estimate progress
    progress = 0
    if status == "completed":
        progress = 100
    elif status == "processing":
        # Check if we have at least one of the output files
        if has_measurements:
            progress = 70
        elif has_mesh:
            progress = 30
        else:
            progress = 10  # Just uploaded

    return {
        "scan_id": scan_id,
        "status": status,
        "progress": progress
    }

@router.get("/{scan_id}/results")
async def get_scan_results(scan_id: str):
    """
    Get scan results (measurements and mesh URL)
    """
    scan_dir = SCANS_DIR / scan_id
    if not scan_dir.exists():
        raise HTTPException(status_code=404, detail="Scan not found")

    # Return actual results if available
    measurements_path = scan_dir / "measurements.json"
    mesh_path = scan_dir / "mesh.ply"  # Changed from .glb to .ply

    measurements = {}
    if measurements_path.exists():
        with measurements_path.open() as f:
            measurements = json.load(f)
    else:
        # Fallback measurements if processing hasn't completed
        measurements = {
            "chest": 0.0,
            "waist": 0.0,
            "hips": 0.0,
            "thigh_left": 0.0,
            "thigh_right": 0.0,
            "bicep_left": 0.0,
            "bicep_right": 0.0,
            "calf_left": 0.0,
            "calf_right": 0.0
        }

    return {
        "scan_id": scan_id,
        "measurements": measurements,
        "mesh_url": f"/scans/{scan_id}/mesh.ply" if mesh_path.exists() else None,
        "status": "completed" if mesh_path.exists() and measurements_path.exists() else "processing"
    }