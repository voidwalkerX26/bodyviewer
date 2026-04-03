# VoxelFit Architecture

Web-based 3D body scanning and measurement application. Users upload front and side profile photos, and the system generates a 3D body mesh with circumference measurements.

---

## Tech Stack Overview

| Layer            | Technology                                  |
| ---------------- | ------------------------------------------- |
| Frontend UI      | Next.js 14+ (App Router), React 19          |
| 3D Rendering     | Three.js + React Three Fiber + Drei         |
| Styling          | Tailwind CSS                                |
| Backend API      | Python FastAPI                              |
| ML Inference     | MediaPipe (pose), Segment Anything (seg), SMPL-X (mesh reconstruction) |
| ORM              | Prisma                                      |
| Database         | PostgreSQL 15+                              |
| Object Storage   | S3-compatible (AWS S3 / Cloudflare R2 / MinIO) |
| Containerization | Docker + Docker Compose                     |
| Deployment       | Vercel (frontend), Fly.io / AWS ECS (backend) |

---

## Frontend Architecture

### Structure

```
frontend/src/
  app/                  # Next.js App Router pages
    layout.tsx          # Root layout + providers (theme)
    page.tsx            # Landing page
    dashboard/          # Scan history + measurement trends
    scan/               # Active scan flow (upload → processing → results)
  components/
    ui/                 # Base UI primitives (Button, Card, Input)
    scan/               # Scan-related components (ImageUploader, PoseGuide, ProcessingSpinner)
    viewer/             # 3D viewer components (BodyViewer, MeasurementLabels)
    dashboard/          # Progress charts, measurement cards
  lib/
    api.ts              # API client utilities
    utils.ts            # Shared helpers
  types/
    index.ts            # TypeScript type definitions
```

### 3D Rendering Stack

- **React Three Fiber** — React bindings for Three.js, declarative 3D scenes
- **@react-three/drei** — Helper components (OrbitControls, Environment, loaders for .glb/.obj/.ply)
- **Pipeline**: Backend returns a .glb mesh file + measurement JSON. Frontend downloads and renders the mesh with annotated measurement points (chest, waist, hips, etc.)

---

## Backend / ML Pipeline Architecture

### API Structure

```
backend/app/
  main.py               # FastAPI entrypoint, CORS, middleware
  api/
    routes/
      scan.py           # Upload, status, results endpoints
      measurements.py   # Measurement retrieval, history
  ml/
    models/             # Downloaded model weights (git-ignored)
    pose_estimator.py   # MediaPipe Pose estimation
    segmenter.py        # Segmentation model
    mesh_reconstructor.py # SMPL-X mesh fitting from 2D keypoints + silhouettes
    measurement.py      # Circumference calculation from mesh cross-sections
  services/
    scan_service.py     # Orchestrates the scan pipeline
    storage_service.py  # S3 upload/download helpers
  core/
    config.py           # Settings (env vars, model paths)
    logging.py          # Structured logging setup
```

### ML Pipeline (Two-Image Approach)

1. **Input**: Front + side profile images (JPEG/PNG)
2. **Validation**: Minimum resolution, blur detection, pose alignment check
3. **Pose Estimation** (MediaPipe Pose): Extract 33 body landmarks per view, triangulate approximate 3D joints
4. **Body Segmentation** (Segment Anything / DeepLabV3+): Extract body silhouette from each view
5. **Mesh Reconstruction**: Fit a parametric body model (SMPL-X) to the 2D keypoints and silhouettes. Alternative lighter approach: visual hull reconstruction from silhouettes → point cloud → mesh smoothing
6. **Circumference Extraction**: Slice the mesh at standard body landmark heights (C7 vertebra for chest, navel for waist, etc.) and compute perimeter lengths
7. **Output**: Textured 3D mesh (.glb) + JSON with measurements

### API Endpoints

| Method | Path                      | Description                              |
| ------ | ------------------------- | ---------------------------------------- |
| POST   | `/api/scan/upload`        | Upload front + side images, start pipeline |
| GET    | `/api/scan/{id}/status`   | Poll pipeline status                     |
| GET    | `/api/scan/{id}/results`  | Get measurements + mesh URL              |
| GET    | `/api/measurements`       | List all historical measurements         |
| GET    | `/api/measurements/{id}`  | Get single scan measurements             |
| DELETE | `/api/scan/{id}`          | Delete scan and associated data          |

---

## Database Schema

### Tables

**scans**
- `id` (UUID, PK)
- `status` (enum: pending, processing, completed, failed)
- `mesh_url` (S3 key to .glb file)
- `front_image_url`, `side_image_url` (S3 keys)
- `created_at`, `completed_at`

**measurements**
- `id` (UUID, PK)
- `scan_id` (FK → scans)
- `chest_cm` (FLOAT)
- `waist_cm` (FLOAT)
- `hips_cm` (FLOAT)
- `left_thigh_cm`, `right_thigh_cm` (FLOAT)
- `left_bicep_cm`, `right_bicep_cm` (FLOAT)
- `neck_cm`, `inseam_cm`, `shoulder_width_cm` (FLOAT)
- `height_cm`, `weight_kg` (FLOAT, user-reported)

### Prisma Schema (sketch)

```prisma
model Scan {
  id           String        @id @default(uuid())
  status       ScanStatus    @default(PENDING)
  meshUrl      String?
  measurements Measurement?
  createdAt    DateTime      @default(now())
  completedAt  DateTime?
}

model Measurement {
  id             String  @id @default(uuid())
  scanId         String  @unique
  scan           Scan    @relation(fields: [scanId], references: [id])    @relation(fields: [scanId], references: [id])
  chestCm        Float
  waistCm        Float
  hipsCm         Float
  leftThighCm    Float
  rightThighCm   Float
  leftBicepCm    Float
  rightBicepCm   Float
  neckCm         Float
  inseamCm       Float?
  shoulderWidthCm Float
}

enum ScanStatus {
  PENDING
  PROCESSING
  COMPLETED
  FAILED
}
```

---

## Storage Model

- **Object Storage (S3/R2/MinIO)** for: uploaded images, generated 3D meshes (.glb), thumbnails
- **Folder structure**: `scans/{scan_id}/` containing `front.jpg`, `side.jpg`, `mesh.glb`, `thumbnail.png`
- Access is controlled via presigned URLs (short-lived), never direct public access
- Images should be deleted after mesh generation for privacy-conscious workflows (configurable retention)

---

## Feature Scope: MVP

### Core Features

- [x] **Image Upload**: Front + side photo upload with pose guide overlay and quality validation (blur check, framing)
- [x] **ML Processing Pipeline**: Pose estimation, body segmentation, mesh reconstruction
- [x] **3D Body Viewer**: Interactive WebGL viewer with orbit controls, rotation, zoom
- [x] **Circumference Measurements**: chest, waist, hips, thigh (L/R), bicep (L/R), neck, shoulder width
- [x] **Scan Results Dashboard**: View measurements as cards, see 3D body, download as PDF/CSV
- [x] **Progress Tracking**: Compare measurements across scans over time, trend charts
- [x] **Export**: Download measurement report (PDF), CSV data export

### Out of Scope (Post-MVP)

- Real-time camera capture guidance (pose matching in-browser)
- Full-body texture mapping on the 3D mesh
- Multi-user sharing / social features
- Garment/size recommendation integration
- Apple Health / Google Fit sync
- Multi-angle support (> 2 photos)
- Video-based scanning
