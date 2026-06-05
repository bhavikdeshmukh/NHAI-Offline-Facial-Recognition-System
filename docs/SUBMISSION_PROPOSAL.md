# NHAI Hackathon 7.0 Submission Proposal

## Project Title

NHAI Offline Facial Recognition and Liveness Detection System

## GitHub Repository

https://github.com/bhavikdeshmukh/NHAI-Offline-Facial-Recognition-System

## Challenge Alignment

The NHAI Hackathon 7.0 objective is to build a highly accurate, lightweight, entirely offline facial recognition and liveness detection system that can integrate with the existing Datalake 3.0 app and operate in zero-network zones.

This submission focuses on a practical field-ready architecture for NHAI personnel authentication on standard mid-range Android and iOS devices. The prototype demonstrates the complete user workflow in a browser so it can be reviewed immediately without requiring device builds, while the repository documents the React Native production path.

## Problem Being Solved

NHAI field teams may need secure identity verification at road, toll, construction, and inspection locations where connectivity is weak or unavailable. Cloud-only authentication can fail in these conditions. The proposed system performs enrollment, recognition, liveness decisioning, and audit logging locally, then syncs records to Datalake 3.0 when the network returns.

## Current Prototype Deliverables

- Browser-based working prototype hosted from the repository.
- Camera-based officer enrollment.
- Three-sample capture: center, left, and right.
- Blur and lighting quality checks before saving the local template.
- Offline verification with immediate lock/unlock decision.
- Local browser storage simulating on-device storage.
- Pending audit queue for Datalake 3.0 sync.
- Vercel serverless `/api/sync` endpoint for online sync simulation.
- CLAHE preprocessing evidence for harsh lighting, low light, blur, and real face images.
- Face crop baseline evidence using real consented images.
- Benchmark CSV files for preprocessing, face crop, temporary embedding, and model-size planning.
- Technical documentation: README, architecture guide, setup guide, model card, benchmarks, and final evaluation map.

## Proposed Production Architecture

```txt
React Native Camera
-> Frame Processor
-> CLAHE Lighting Normalization
-> Face Detection and 112x112 Face Crop
-> Passive Liveness Check
-> Active Liveness Challenge
-> MobileFaceNet INT8 Embedding
-> Cosine Similarity Decision
-> Encrypted SQLite Template Store
-> Offline Audit Queue
-> Datalake 3.0 / AWS Sync and Purge
```

## Model Strategy

| Component | Planned Model or Method | Purpose |
|---|---|---|
| Face detection | BlazeFace or SCRFD-lite | Fast mobile face localization |
| Preprocessing | CLAHE | Robustness under harsh sunlight, shadows, and low light |
| Embedding | MobileFaceNet INT8 | Lightweight face vector generation under the model-size budget |
| Matching | Cosine similarity | Fully offline template comparison |
| Passive liveness | FASNet/Silent-Face style anti-spoofing | Detect flat images, print attacks, and screen replay artifacts |
| Active liveness | Blink, head turn, or smile prompt | Confirms live human participation |
| Explainability | Grad-CAM style visual evidence | Helps reviewers understand model attention and trust decisions |

## Evaluation Criteria Mapping

### 1. Innovation Level: 30 Marks

- Uses an edge AI design rather than server-dependent authentication.
- Targets MobileFaceNet INT8 to stay within the approximate 20 MB model footprint.
- Adds CLAHE preprocessing for Indian outdoor lighting conditions.
- Uses both passive and active liveness in the production design, stronger than blink-only liveness.
- Documents explainability through Grad-CAM style evidence.
- Demonstrates real-image preprocessing and face-crop evidence in the repository.

### 2. Feasibility: 30 Marks

- Prototype runs immediately in a browser and works on HTTPS-enabled phone browsers.
- Workflow is compatible with React Native architecture and maps cleanly to native modules.
- Offline cosine matching and local storage are already demonstrated.
- Target runtime is under 1 second on mid-range devices.
- Final production modules are documented for Android 8.0+, iOS 12+, and 3 GB RAM devices.

### 3. Scalability and Sustainability: 20 Marks

- Offline queue stores audit events when network is unavailable.
- Sync simulation shows how records are pushed when connectivity returns.
- Production design includes purge after successful sync.
- Multi-sample enrollment improves robustness across pose variation.
- CLAHE and quality gates improve adaptability to diverse lighting and field conditions.
- Embeddings, not raw images, are the intended stored biometric unit.

### 4. Presentation and Documentation: 20 Marks

- Repository includes clean source organization and focused documentation.
- README explains the problem, architecture, demo, security, evidence, and setup.
- `docs/FINAL_EVALUATION_MAP.md` maps the solution to the official marks.
- `docs/MODEL_CARD.md` records model choices, licensing direction, and deployment plan.
- `docs/BENCHMARKS.md` records measured prototype evidence and avoids unsupported claims.

## Honest Prototype Boundary

The current web demo uses a deterministic temporary embedding to prove the offline enrollment, vector comparison, lock/unlock decision, and sync workflow. It does not claim final MobileFaceNet recognition accuracy. The final recognition layer is designed to replace this temporary embedding with a quantized MobileFaceNet TFLite model in the React Native implementation.

This distinction is intentional: the submission demonstrates a working end-to-end offline flow while documenting a realistic production-grade model path.

## Demo Video Flow

1. Open the GitHub repository and show the README.
2. Open the hosted demo link.
3. Enroll the officer with center, left, and right captures.
4. Show that poor quality frames can be rejected.
5. Return to verification.
6. Show the locked state.
7. Tap Analyze and Unlock.
8. Show App Unlocked and match latency under one second.
9. Open Sync Details.
10. Tap Simulate Online Sync to show recovery after connectivity returns.

## Recommended Submission Contents

- GitHub repository link.
- Final proposal PDF or this Markdown document.
- Demo video.
- Source code zip excluding `.git`, private duplicate files, and local cache files.
- Optional PPT only if the portal explicitly asks for a presentation deck.

## Conclusion

This submission presents a practical offline-first identity verification system for NHAI field conditions. It emphasizes field reliability, lightweight model design, liveness protection, local auditability, and a clear integration path into Datalake 3.0. The working prototype proves the user journey, while the technical documentation describes how the final React Native and edge-AI implementation can be completed using open-source technologies.
