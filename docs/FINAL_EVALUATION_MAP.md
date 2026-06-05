# Final Evaluation Map

This document maps the project directly to the NHAI Hackathon evaluation criteria.

## 1. Innovation Level: 30 Marks

What we show:

- Offline-first edge verification flow.
- CLAHE lighting normalization for Indian outdoor conditions.
- Multi-sample enrollment: center, left, and right.
- Blur and lighting quality gate before saving a template.
- Two-layer liveness design: passive FASNet/Silent-Face plus active challenge.
- MobileFaceNet INT8 target under the 20 MB model budget.
- Grad-CAM explainability planned as offline documentation evidence, not mobile runtime.

Current evidence:

- `assets/evidence/clahe/`
- `assets/evidence/real_clahe/`
- `assets/evidence/face_detection_real/`
- `benchmarks/results/clahe_timings.csv`
- `benchmarks/results/face_crop_baseline_real.csv`

Important honesty note:

The browser demo uses temporary embeddings only for workflow demonstration. Final recognition is designed for MobileFaceNet INT8.

## 2. Feasibility: 30 Marks

What we show:

- Browser demo runs without server dependency.
- Camera enrollment and verification work on HTTPS-hosted web demo.
- Local browser storage simulates on-device storage.
- Cosine matching runs fully offline.
- Python scripts demonstrate preprocessing, face crop, and embedding pipeline.
- React Native integration path is documented through the same module boundaries:
  camera, preprocessing, liveness, embedding, storage, sync.

React Native target architecture:

```txt
react-native-vision-camera
-> frame processor
-> native CLAHE preprocessing
-> BlazeFace/SCRFD-lite face crop
-> FASNet passive liveness
-> active challenge
-> MobileFaceNet INT8
-> SQLite encrypted embedding store
-> NetInfo sync queue
```

Current demo limitation:

The web demo is presentation-ready but not the final native React Native implementation.

## 3. Scalability and Sustainability: 20 Marks

What we show:

- Pending sync queue stores offline verification events.
- Simulated online sync converts pending events into synced events for demo.
- Local-only template avoids dependency on cloud authentication.
- CLAHE and quality gates address lighting diversity.
- Multi-sample enrollment improves robustness across pose variation.
- Raw images are not required for the final architecture; embeddings are the intended stored unit.

Final production direction:

- SQLite for local records.
- AES-256 encryption for templates and logs.
- Exponential backoff for failed sync.
- Purge synced logs by retention policy.
- Audit failed/spoof attempts.

## 4. Presentation and Documentation: 20 Marks

What we show:

- Professional README.
- Master plan.
- Architecture document.
- Setup guide.
- Model card.
- Benchmark document.
- Development checklist.
- Evidence assets and measured CSV outputs.

Recommended demo video order:

1. Show README and architecture.
2. Open live demo.
3. Enroll with center, left, and right samples.
4. Show blur/quality gate if possible.
5. Verify offline and unlock.
6. Open sync queue.
7. Tap simulated online sync.
8. Show evidence folders and benchmark CSVs.
9. State clearly that final recognition target is MobileFaceNet INT8.

