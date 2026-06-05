# Development Checklist

This checklist is the working board for building the project one part at a time. README polish can come later; this file is for execution.

## Final Build Direction

Core pipeline:

```txt
Camera frame
-> CLAHE lighting normalization
-> BlazeFace face detection
-> face crop and alignment
-> FASNet passive liveness
-> active liveness challenge
-> MobileFaceNet embedding
-> cosine similarity match
-> encrypted local result
-> pending Datalake sync queue
```

Important corrections:

- Use MobileFaceNet trained with ArcFace loss, not full ArcFace R50.
- Use Grad-CAM only offline for documentation and presentation visuals.
- Do not claim latency, accuracy, or model size until measured.
- Keep iris recognition out of scope for this hackathon.
- Keep CLAHE as a key differentiator for Indian outdoor field conditions.

## Phase A: Project Foundation

- [x] Create repository and folder structure
- [x] Add professional README
- [x] Add master plan
- [x] Add architecture document
- [x] Add setup guide
- [x] Add browser prototype demo
- [ ] Add model card
- [ ] Add benchmark document
- [ ] Add security/privacy document
- [ ] Add Datalake sync design

## Phase B: Python Model Lab

- [x] Create Python scripts folder
- [ ] Add Python requirements
- [x] Add CLAHE preprocessing script
- [x] Add benchmark scaffold
- [x] Add sample image folder
- [ ] Add model download/source notes
- [ ] Add MobileFaceNet conversion script
- [ ] Add FASNet conversion script
- [ ] Add embedding similarity test
- [ ] Add offline Grad-CAM generation script

## Phase C: CLAHE Evidence

- [x] Generate 5 synthetic lighting samples
- [x] Run CLAHE before/after script
- [x] Save before/after images under `assets/evidence/clahe/`
- [x] Measure preprocessing time on synthetic samples
- [x] Add consented real-image CLAHE comparison evidence
- [ ] Decide final CLAHE parameters
- [ ] Add evidence to final docs/presentation

## Phase D: Face Detection

- [ ] Choose BlazeFace source and license
- [ ] Test detection on sample images
- [ ] Save cropped face outputs
- [ ] Compare failure cases
- [ ] Decide if SCRFD-lite comparison is needed
- [ ] Record detection time and model size

## Phase E: Face Recognition

- [ ] Choose MobileFaceNet source and license
- [ ] Export/convert model to mobile format
- [ ] Verify embedding shape
- [ ] Implement cosine similarity
- [ ] Test same-person and different-person pairs
- [ ] Quantize to INT8
- [ ] Compare FP32 vs INT8 quality and speed

## Phase F: Liveness

- [ ] Choose FASNet/Silent-Face source and license
- [ ] Test live face vs printed photo vs screen replay
- [ ] Define spoof threshold from tests
- [ ] Implement blink/head-turn/smile challenge logic
- [ ] Combine passive and active liveness result
- [ ] Save spoof test evidence

## Phase G: Mobile/App Implementation

- [ ] Decide React Native setup approach
- [ ] Add camera capture screen
- [ ] Add enrollment screen
- [ ] Add liveness challenge screen
- [ ] Add verification result screen
- [ ] Add pending sync queue screen
- [ ] Integrate model runtime
- [ ] Add local encrypted storage
- [ ] Add sync retry logic

## Phase H: Final Evidence

- [ ] Benchmark model sizes
- [ ] Benchmark per-stage latency
- [ ] Benchmark end-to-end latency
- [ ] Test offline mode
- [ ] Test spoof rejection
- [ ] Test pending sync queue
- [ ] Record final demo video/GIF
- [ ] Add architecture diagram
- [ ] Add final PPT/presentation content

## Next Immediate Task

Start with CLAHE because it is small, real, and unique to our project. It gives us evidence quickly before the heavy model work.
