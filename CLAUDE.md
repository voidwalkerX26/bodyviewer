# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project: VoxelFit

Web-based 3D body scanning and measurement application. Users upload front + side profile photos; the backend generates a 3D body mesh and extracts circumference measurements.

See `ARCHITECTURE.md` for full tech stack details and `IMPLEMENTATION_PLAN.md` for phased task tracking.

## Structure

| Path                    | Purpose                                 |
| ----------------------- | --------------------------------------- |
| `frontend/`             | Next.js 14+ app (App Router, TypeScript, Tailwind) |
| `frontend/src/app/`     | Page routes                             |
| `frontend/src/components/` | React components (ui, scan, viewer, dashboard) |
| `backend/app/`          | FastAPI ML inference service            |
| `backend/app/api/routes/` | API endpoints                         |
| `backend/app/ml/`       | ML models and inference logic           |
| `backend/app/services/` | Business logic                          |
| `backend/app/core/`     | Config, logging                         |
| `shared/`               | Shared types/schemas (optional)         |

## Commands

### Frontend

```
cd frontend && npm install        # Install deps
cd frontend && npm run dev        # Dev server
cd frontend && npm run build      # Production build
cd frontend && npm run lint       # ESLint
```

### Backend

```
cd backend && python -m venv .venv && source .venv/bin/activate
cd backend && pip install -r requirements.txt
cd backend && uvicorn app.main:app --reload   # Dev server
```

## Key Decisions

- **ML Pipeline**: Two-image approach (front + side). MediaPipe Pose → Segmentation → SMPL-X or visual hull mesh fitting → circumference extraction via cross-section slicing.
- **Async Processing**: ML inference takes 10–60s. Use background tasks + polling. Never block the upload request.
- **3D Rendering**: React Three Fiber + drei on the frontend. Backend returns `.glb` mesh + measurement JSON.
- **Storage**: S3-compatible object storage for images/meshes. Access via short-lived presigned URLs.
- **Database**: PostgreSQL + Prisma ORM.
- **Privacy**: Uploaded images are optionally deleted after mesh generation. Meshes encrypted at rest.

## Implementation Status

Phases 1–5 outlined in `IMPLEMENTATION_PLAN.md`. Currently at scaffolding stage — planning docs and directory structure created, no production code written yet.
