# VoxelFit Personal Setup

This is a simplified personal/local version of VoxelFit for individual use.

## What's Included

### Backend (FastAPI)
- `POST /api/scan/upload` - Upload front + side images
- `GET /api/scan/{scan_id}/status` - Check processing status  
- `GET /api/scan/{scan_id}/results` - Get measurements and mesh URL
- `GET /api/scans` - List all scans
- Mock ML processing that generates realistic measurements
- Local file storage in `./scans/` directory

### Frontend (Next.js 14)
- Upload page with front/side image selection
- Dashboard to view scan history
- Basic UI with Tailwind CSS
- Ready for 3D viewer integration (Phase 3)

## Quick Start

### 1. Backend Setup
```bash
cd backend
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend will run on http://localhost:8000

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will run on http://localhost:3000

### 3. Usage
1. Visit http://localhost:3000/scan
2. Upload front and side body photos
3. View results at http://localhost:3000/dashboard

## File Structure
```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── scan.py      # Upload/status/results endpoints
│   │   │   │   └── scans.py     # List scans endpoint
│   │   │   └── __init__.py
│   │   ├── ml/
│   │   │   └── processing.py    # Mock ML processing pipeline
│   │   └── __init__.py
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # For future containerization
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Root layout with nav
│   │   │   ├── scan/
│   │   │   │   └── page.tsx     # Upload page
│   │   │   └── dashboard/
│   │   │       └── page.tsx     # History dashboard
│   │   ├── components/          # Empty for now - ready for 3D viewer
│   │   ├── lib/                 # Empty for now
│   │   ├── types/               # Empty for now
│   │   └── globals.css          # Tailwind base styles
│   ├── package.json             # Next.js + React Three Fiber deps
│   └── tsconfig.json
├── scans/                       # Created automatically - stores uploads/results
└── README_PERSONAL_SETUP.md     # This file
```

## Next Steps (Phase 3+)
Once this basic upload/flow is working:
1. Implement actual MediaPipe pose estimation in `processing.py`
2. Add body segmentation (MediaPipe Selfie Segmentation or similar)
3. Implement simple visual hull or bounding box mesh generation
4. Add real circumference calculations from pose landmarks
5. Create 3D viewer component using React Three Fiber
6. Display measurements on the 3D model

## Notes for Personal Use
- No authentication needed - single user
- No remote database - uses local file system
- No cloud storage - stores everything in `./scans/`
- Images are kept unless manually deleted (add cleanup later if desired)
- Mesh files are currently placeholders - replace with real .glb later

## Troubleshooting
- **Port conflicts**: Change port in `uvicorn.run()` or `next dev` if needed
- **CORS issues**: Backend already allows localhost:3000
- **Missing dependencies**: Run `pip install -r requirements.txt` and `npm install`
- **Module not found**: Make sure you're running from the project root directory

## Privacy
Since this runs locally:
- Your images never leave your computer
- Measurements and meshes are stored locally
- No telemetry or data collection
- You control all data retention/deletion