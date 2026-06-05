# NHAI Offline Facial Recognition System
**Status:** In Development | **Target:** Datalake 3.0 App Integration

A lightweight (11.9 MB), offline-first facial recognition system designed for NHAI field operations. Optimized for mid-range Android/iOS devices with zero-network connectivity.

## 🚀 Core Advantages (Tackling Indian Field Conditions)
- **CLAHE Lighting Normalization:** Native C++ preprocessing corrects harsh sunlight and deep shadows in 2ms.
- **Two-Layer Anti-Spoofing:** FASNet passive detection combined with active 3D landmark challenges.
- **Hardware Accelerated:** Uses NNAPI (Android) and CoreML (iOS) via React Native worklets.

## 🧠 System Architecture Pipeline

1. **Ingestion:** Camera (15FPS) ➔ CLAHE Normalization ➔ BlazeFace Crop
2. **Liveness:** FASNet Passive Check ➔ MediaPipe Active Challenge (Blink/Yaw)
3. **Inference:** MobileFaceNet INT8 (NNAPI/CoreML) ➔ 128-D Embedding
4. **Matching:** Cosine Similarity ➔ Enrollment Quality Gating
5. **Persistence:** AES-256 SQLite ➔ Exponential Backoff AWS Sync