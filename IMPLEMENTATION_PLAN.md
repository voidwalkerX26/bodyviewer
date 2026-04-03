# VoxelFit Implementation Plan

Track progress by checking off tasks `[ ]` → `[x]`.

---

## Phase 1 — Repo Setup & UI Shell

- [ ] Initialize monorepo root with `ARCHITECTURE.md` and `IMPLEMENTATION_PLAN.md` ✅ (complete)
- [ ] Set up `frontend/` with Next.js 14+ (App Router), TypeScript, Tailwind CSS
- [ ] Configure ESLint, Prettier, and `tsconfig.json` paths
- [ ] Set up project-wide `.gitignore` (node_modules, .env, model weights, etc.)
- [ ] Create root `package.json` (workspaces or turbo if monorepo tooling desired)
- [ ] Implement layout shell: navigation bar, sidebar, dark/light theme
- [ ] Create empty dashboard page shell (table placeholder)
- [ ] Create empty scan page shell (upload area placeholder)
- [ ] Add basic component library: `Button`, `Card`, `Input`, `Modal`

---

## Phase 2 — ML Inference API

- [ ] Initialize `backend/` with FastAPI, uvicorn, virtualenv
- [ ] Create `Dockerfile` for backend (CUDA base image for GPU inference)
- [ ] Set up `requirements.txt` / `pyproject.toml` with ML dependencies
- [ ] Create FastAPI entry point with health check endpoint
- [ ] Configure CORS, structured logging, error handling middleware
- [ ] Implement image upload endpoint (`POST /api/scan/upload`)
  - Accept multipart form (front + side images)
  - Validate image format, size, resolution
  - Store uploads to S3/local temp storage
- [ ] Implement pose estimation module
  - MediaPipe Pose extraction
  - 3D joint triangulation from two views
- [ ] Implement body segmentation module
  - Silhouette extraction for front and side views
- [ ] Implement mesh reconstruction module
  - SMPL-X fitting OR visual hull reconstruction
  - Generate .glb mesh output
- [ ] Implement circumference measurement module
  - Cross-section slicing at standard body heights
  - Perimeter calculation
- [ ] Create scan status endpoint (`GET /api/scan/{id}/status`)
- [ ] Create scan results endpoint (`GET /api/scan/{id}/results`)
  - Returns: measurements JSON, mesh download URL
- [ ] Implement async pipeline processing (Celery/RQ task queue or FastAPI background tasks)
- [ ] Set up PostgreSQL database with Prisma
- [ ] Wire database: create scan records, store measurement results
- [ ] Add basic input validation and error responses (blur detection, poor framing)

---

## Phase 3 — WebGL Rendering (Frontend 3D Viewer)

- [ ] Install Three.js, React Three Fiber, Drei
- [ ] Create `BodyViewer` component: load and render .glb mesh from S3 URL
- [ ] Add OrbitControls for rotation, pan, zoom
- [ ] Add Environment lighting for realistic rendering
- [ ] Create measurement annotation overlays
  - Clickable measurement points on the 3D model
  - Floating labels showing circumference values at chest, waist, hips, etc.
- [ ] Add loading state and skeleton for mesh loading
- [ ] Implement fallback: 2D silhouette view if WebGL is unsupported
- [ ] Add camera presets (front view, side view, top-down)
- [ ] Add comparison mode: side-by-side or overlaid meshes from different scans

---

## Phase 4 — Integration

- [ ] Connect frontend upload form to backend `/api/scan/upload`
- [ ] Implement polling or WebSocket for scan status updates
- [ ] Display scan progress UI (uploading → processing → complete)
- [ ] Wire measurement results dashboard to backend `/api/measurements`
- [ ] Render 3D viewer alongside measurement cards
- [ ] Implement scan history table with date, status, and key metrics
- [ ] Add progress tracking: chart comparing measurement changes across scans
- [ ] Implement export functionality (PDF report, CSV download)
- [ ] Handle error states gracefully: upload failures, processing failures
- [ ] End-to-end test the full pipeline: upload → ML inference → 3D render → measurement display

---

## Phase 5 — Polish & Production Prep

- [ ] Responsive mobile layouts (image capture guidance, condensed dashboard)
- [ ] Performance optimization: lazy loading, image optimization, mesh LOD
- [ ] Error boundaries and Sentry/Rollbar integration
- [ ] API rate limiting and request validation middleware
- [ ] Basic test coverage:
  - Backend: pytest for ML pipeline (mock models), API route tests
  - Frontend: component unit tests, integration test for upload flow
- [ ] Docker Compose for local dev (backend + DB + storage)
- [ ] Environment configuration templates (`.env.example` for both frontend and backend)
- [ ] Deployment configs:
  - `vercel.json` or Vercel project for frontend
  - Fly.io / AWS ECS config for backend with GPU support
- [ ] README.md with local setup instructions

---

## Notes & Decisions

- **Monorepo tool**: Start with a simple flat structure (`frontend/` + `backend/`). Add Turborepo later if needed for DX improvements.
- **ML model selection**: Default to MediaPipe Pose (fast, CPU-capable) + custom visual hull for mesh. SMPL-X can be added later for higher accuracy but requires a license and heavier GPU inference.
- **Privacy**: Uploaded images are processed and then optionally deleted. Meshes are stored with encryption at rest. Presigned URLs with short TTL for all downloads.
- **Async processing**: Image to mesh conversion is slow (10–60s). Use background tasks (FastAPI `BackgroundTasks` or Celery) with polling from the frontend. Don't block the upload request.
