from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from datetime import datetime

router = APIRouter()

# Scans directory
SCANS_DIR = Path("./scans")
SCANS_DIR.mkdir(exist_ok=True)

@router.get("")
async def list_scans():
    """
    List all scan directories
    """
    scans = []

    if not SCANS_DIR.exists():
        return {"scans": []}

    for scan_dir in SCANS_DIR.iterdir():
        if scan_dir.is_dir():
            scan_id = scan_dir.name

            # Try to get timestamp from directory name or metadata
            try:
                # Assuming format: scan_YYYYMMDD_HHMMSS
                if scan_id.startswith("scan_"):
                    timestamp_str = scan_id[5:]  # Remove "scan_" prefix
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    timestamp_iso = timestamp.isoformat()
                else:
                    # Fallback to directory modification time
                    timestamp = datetime.fromtimestamp(scan_dir.stat().st_mtime)
                    timestamp_iso = timestamp.isoformat()
            except:
                # Fallback to directory modification time
                timestamp = datetime.fromtimestamp(scan_dir.stat().st_mtime)
                timestamp_iso = timestamp.isoformat()

            # Determine status
            has_mesh = (scan_dir / "mesh.glb").exists()
            has_measurements = (scan_dir / "measurements.json").exists()
            has_front = (scan_dir / "front.jpg").exists()
            has_side = (scan_dir / "side.jpg").exists()

            if has_mesh and has_measurements:
                status = "completed"
            elif has_front and has_side:
                status = "uploaded"
            else:
                status = "unknown"

            scans.append({
                "id": scan_id,
                "timestamp": timestamp_iso,
                "status": status
            })

    # Sort by timestamp descending (newest first)
    scans.sort(key=lambda x: x["timestamp"], reverse=True)

    return {"scans": scans}