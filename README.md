# NHAI Offline Facial Recognition & Liveness Detection System

Offline-first facial recognition and liveness detection system designed for NHAI field operations, zero-network zones, and Datalake 3.0 integration.

![Status](https://img.shields.io/badge/status-submission%20prototype-blue)
![Mode](https://img.shields.io/badge/mode-offline--first-success)
![Target](https://img.shields.io/badge/target-Datalake%203.0-orange)
![Platform](https://img.shields.io/badge/platform-Android%20%7C%20iOS-lightgrey)

## Problem Statement

NHAI field staff may need secure identity verification in locations where network connectivity is weak, delayed, or completely unavailable. This project proposes a lightweight, mobile-ready facial recognition and liveness detection system that can authenticate users offline and sync verification logs when connectivity returns.

The goal is not just face matching. The goal is reliable, explainable, and spoof-resistant identity verification under Indian field conditions such as harsh sunlight, shadows, low-end devices, and zero-network environments.

## Core Advantages

| Capability | Why It Matters for NHAI |
|---|---|
| Offline-first verification | Works in remote toll, road, and construction zones without live internet |
| CLAHE lighting normalization | Improves face quality in harsh sunlight, shadows, and uneven lighting |
| Two-layer liveness detection | Combines passive anti-spoofing with active user challenges |
| Lightweight face embeddings | Enables fast local matching on mid-range mobile devices |
| Encrypted local storage | Keeps biometric templates and logs secure on-device |
| Pending sync queue | Stores events locally and syncs with Datalake 3.0 when network returns |
| Explainability support | Grad-CAM style visual reasoning helps examiners trust model decisions |

## Prototype Demo

Open `index.html` in a browser to view the current offline verification prototype. It demonstrates the planned user flow:

1. Offline verification dashboard
2. Officer enrollment using the device camera
3. Local browser-cache template storage
4. Locked verification screen with analyze-and-unlock recapture
5. Pending Datalake 3.0 sync queue

The same static demo can be deployed on GitHub Pages or Vercel. No backend server is required for the presentation prototype.

On Vercel, the demo also exposes a small `/api/sync` serverless endpoint to simulate pushing pending offline events to a backend.

## System Architecture

```mermaid
flowchart LR
    A[Mobile Camera] --> B[Face Detection]
    B --> C[CLAHE Lighting Normalization]
    C --> D[Face Alignment and Crop]
    D --> E[Face Embedding Model]
    D --> F[Liveness Detection]
    F --> F1[Passive Anti-Spoof Check]
    F --> F2[Active Challenge Check]
    E --> G[Local Similarity Matching]
    F1 --> H[Decision Engine]
    F2 --> H
    G --> H
    H --> I[Verified or Rejected Result]
    I --> J[Encrypted Local Log]
    J --> K[Offline Sync Queue]
    K --> L[Datalake 3.0 Sync]
```

## Offline Verification Flow

1. User opens the mobile verification screen.
2. Camera captures face frames locally.
3. System applies lighting normalization and face alignment.
4. Face embedding is generated on-device.
5. Liveness check verifies that the input is a real person, not a photo or screen replay.
6. Local encrypted template database performs similarity matching.
7. Result is shown instantly.
8. Verification event is stored in the pending sync queue.
9. When network returns, logs are synced to Datalake 3.0.

## Liveness Detection Strategy

This project uses a two-layer anti-spoofing plan:

| Layer | Method | Purpose |
|---|---|---|
| Passive liveness | Lightweight FASNet-style model | Detects printed photo, screen replay, and flat texture attacks |
| Active liveness | Blink, head turn, or randomized prompt | Confirms real-time human presence |

This combination is stronger than using only blink detection because blink-only systems can be fooled by replay videos. The passive layer catches visual spoof artifacts, while the active layer prevents static-image attacks.

## Tackling Indian Field Conditions

NHAI field environments are not clean office environments. The system is designed around real deployment constraints:

- Harsh sunlight near roads and toll plazas
- Deep shadows from helmets, vehicles, and roadside structures
- Dusty or blurred camera input
- Mid-range mobile hardware
- Delayed or unavailable network connectivity
- Need for fast verification without server round trips

CLAHE preprocessing improves local contrast before recognition, making the face pipeline more robust under uneven lighting.

## Security and Privacy

- Raw face images should not be stored by default.
- Face embeddings are stored locally in encrypted form.
- Verification logs are queued locally when offline.
- Sync payloads can be signed and timestamped.
- Failed spoof attempts are logged for audit review.

## Performance Targets

| Metric | Target |
|---|---|
| Verification mode | Fully offline |
| Recognition latency | Under 1 second on mid-range devices |
| Model size | Lightweight mobile-ready model |
| Sync behavior | Automatic retry with pending queue |
| Liveness | Passive plus active anti-spoofing |
| Storage | Encrypted local database |

Measured development results are tracked in [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md). Prototype numbers stay there until they are validated on real mobile hardware.

Current evidence includes synthetic lighting samples and consented real-image CLAHE comparisons under `assets/evidence/`.

The first face-crop baseline is also available under `assets/evidence/face_detection_real/`; it is a temporary OpenCV desktop baseline before the final BlazeFace/SCRFD-lite mobile detector.

The browser demo can capture a live camera frame, save a local enrollment template in browser storage, and verify a new camera capture offline. It uses a temporary deterministic 128-number vector only to validate the offline cosine-similarity flow. It is not real recognition accuracy and will be replaced by MobileFaceNet INT8 for final recognition.

Enrollment requires three usable samples: center, left, and right. Blurry or poorly lit frames are rejected before the local template is saved.

The separate liveness screen was removed from the web demo to keep the presentation focused on the working lock/unlock flow. Liveness remains in the final native pipeline design as FASNet passive anti-spoofing plus active challenge.

Model choice, licensing notes, and expected model filenames are tracked in [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md).

The final hackathon scoring map is available in [`docs/FINAL_EVALUATION_MAP.md`](docs/FINAL_EVALUATION_MAP.md).

## Repository Structure

```txt
NHAI-Offline-Facial-Recognition-System/
|-- models/
|   `-- .gitkeep
|-- python-scripts/
|   |-- README.md
|   |-- benchmark_pipeline.py
|   |-- clahe_preprocess.py
|   `-- create_sample_images.py
|-- src/
|   |-- components/
|   |-- screens/
|   |-- services/
|   |-- app.js
|   |-- styles.css
|   `-- utils/
|-- docs/
|   |-- MASTER_PLAN.md
|   |-- ARCHITECTURE.md
|   |-- BENCHMARKS.md
|   |-- DEVELOPMENT_CHECKLIST.md
|   |-- FINAL_EVALUATION_MAP.md
|   |-- SUBMISSION_PROPOSAL.md
|   `-- SETUP.md
|-- assets/
|   |-- evidence/
|   |-- architecture-diagram.png
|   `-- demo.gif
|-- benchmarks/
|   `-- results/
|-- samples/
|   `-- README.md
|-- .gitignore
|-- index.html
`-- README.md
```

## Hackathon Impact

This solution is designed to help NHAI continue secure digital operations in places where internet connectivity cannot be guaranteed. It reduces dependency on cloud authentication, improves field reliability, and adds anti-spoofing safeguards needed for trust-sensitive identity verification.

