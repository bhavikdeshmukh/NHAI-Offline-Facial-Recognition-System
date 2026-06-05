# Master Implementation Plan

## Project

NHAI Offline Facial Recognition and Liveness Detection System

## Objective

Build a lightweight, accurate, and entirely offline facial recognition and liveness detection system that can be integrated into the Datalake 3.0 mobile workflow for secure field authentication in zero-network zones.

## Winning Position

This project should not be presented as a generic face recognition app. It should be presented as a field-ready NHAI authentication module.

The strongest differentiators are:

- Offline-first identity verification
- CLAHE preprocessing for harsh Indian lighting conditions
- Two-layer liveness detection
- Encrypted local biometric template storage
- Pending sync queue for Datalake 3.0
- Explainable AI outputs for examiner trust

## User Story

An NHAI field officer reaches a remote site with no reliable internet. The officer opens the Datalake-integrated verification module, captures a face, and receives a trusted verification result locally. The event is stored securely on-device. When the network returns, the app syncs logs automatically.

## Core Modules

### 1. Mobile Camera Capture

Purpose:
Capture face frames from the device camera with real-time quality feedback.

Expected behavior:

- Detect whether a face is present
- Reject multiple faces
- Warn for poor lighting or blur
- Guide the user to hold still

Success criteria:

- Smooth capture experience
- Clear visual feedback
- No confusing user states

### 2. Face Preprocessing

Purpose:
Improve face image quality before recognition.

Pipeline:

1. Face detection
2. Landmark detection
3. Face alignment
4. CLAHE lighting normalization
5. Resize and normalize input tensor

Why this matters:
NHAI usage may happen under sunlight, shadows, and low-quality mobile cameras. CLAHE gives the project a strong field-readiness story.

### 3. Face Recognition

Purpose:
Generate compact face embeddings and compare them against locally stored enrolled templates.

Recommended approach:

- Use a lightweight mobile-friendly embedding model
- Store embeddings, not raw images
- Use cosine similarity for matching
- Define a threshold for verified, rejected, and uncertain cases

Decision states:

- Verified
- Rejected
- Low confidence
- Poor image quality

### 4. Liveness Detection

Purpose:
Prevent spoof attacks using photos, screens, or replay videos.

Layer 1: Passive liveness

- Detect spoof patterns from texture, reflection, flatness, or screen artifacts
- Runs silently in the background

Layer 2: Active liveness

- Ask for a randomized action such as blink, turn head, or look left/right
- Prevents simple static image attacks

Why two layers:
Blink-only liveness can be fooled by replay video. Passive plus active liveness is a stronger hackathon argument.

### 5. Offline Storage

Purpose:
Allow verification without internet.

Local data:

- Encrypted face embeddings
- User identifier
- Verification logs
- Liveness result
- Timestamp
- Sync status

Avoid:

- Storing raw face images unless explicitly required for debugging or audit

### 6. Sync Queue

Purpose:
Make offline behavior visible and trustworthy.

Expected behavior:

- Store events locally when offline
- Mark each event as pending, synced, or failed
- Retry sync when network returns
- Preserve audit order and timestamps

UI requirement:
Show "Offline Mode Active" and "Pending Syncs" clearly so offline mode feels intentional, not broken.

### 7. Explainability

Purpose:
Increase examiner trust.

Planned features:

- Grad-CAM style heatmap for liveness model
- Confidence score display for internal/debug mode
- Decision reason summary

Example:

- "Rejected: liveness score below threshold"
- "Retry: poor lighting detected"
- "Verified: face match and liveness passed"

## MVP Scope

The first working demo should include:

1. Enrollment screen
2. Offline verification screen
3. Liveness pass/fail simulation or prototype
4. Local verification result
5. Pending sync queue UI
6. Professional README with screenshots and architecture

## Final Hackathon Demo Flow

1. Open app in offline mode
2. Enroll or select a registered user
3. Perform face verification
4. Show liveness check passing
5. Show verified result under one second
6. Attempt spoof demo using a photo or screen
7. Show spoof rejection
8. Show pending sync queue
9. Turn network back on
10. Show sync completion

## Documentation Plan

Required files:

- `README.md`: public storefront
- `docs/MASTER_PLAN.md`: complete strategy and execution roadmap
- `docs/ARCHITECTURE.md`: technical design
- `docs/SETUP.md`: how to run locally
- `docs/MODEL_CARD.md`: model choices, limits, and fairness notes
- `docs/SECURITY.md`: privacy and data handling

## Repository Quality Plan

Branching:

- `main`: stable branch
- `codex/docs-polish`: documentation upgrades
- `codex/mobile-ui`: app interface
- `codex/liveness-pipeline`: anti-spoofing work
- `codex/offline-storage`: database and sync queue

Commit style:

- `docs(readme): add hackathon submission overview`
- `docs(plan): add master implementation roadmap`
- `feat(ui): add offline verification screen`
- `feat(liveness): add active challenge flow`
- `feat(storage): add encrypted pending sync queue`
- `fix(camera): improve low-light capture handling`

## Evaluation Metrics

| Area | Metric |
|---|---|
| Speed | Verification under 1 second target |
| Offline | Full verification without network |
| Security | No raw image storage by default |
| Liveness | Detect photo and replay attacks |
| Usability | Clear capture and result feedback |
| Field readiness | Handles sunlight, shadows, and poor camera input |

## Risks and Mitigation

| Risk | Mitigation |
|---|---|
| Model too heavy for mobile | Use quantized lightweight model |
| Low-light failures | Use CLAHE and quality feedback |
| Spoof replay attack | Add passive plus active liveness |
| Network unavailable | Use local queue with retry sync |
| Examiner cannot run project | Provide setup guide, screenshots, and demo video |

## Day-by-Day Execution

### Day 1

- Finalize README
- Add master plan
- Add architecture diagram
- Commit clean repo structure

### Day 2

- Build app UI prototype
- Add enrollment and verification screens
- Add offline mode and sync queue UI

### Day 3

- Implement or simulate recognition pipeline
- Add preprocessing module
- Add liveness challenge flow

### Day 4

- Add storage and sync queue logic
- Add benchmark table
- Add screenshots and demo GIF

### Day 5

- Polish documentation
- Record final demo
- Create release
- Prepare pitch script

## Final Pitch

This project enables NHAI to perform secure facial verification even when internet connectivity is unavailable. It is designed for real field constraints, not ideal lab conditions. By combining offline recognition, lighting normalization, two-layer liveness detection, encrypted storage, and delayed sync, the system supports uninterrupted Datalake 3.0 operations in zero-network zones.

