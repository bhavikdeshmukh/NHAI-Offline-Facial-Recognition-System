# Setup Guide

## Current Status

This repository contains a submission-ready browser prototype and supporting technical documentation for the NHAI Hackathon 7.0 offline facial recognition challenge.

The browser prototype demonstrates the complete offline workflow: camera-based enrollment, three-sample local template creation, offline unlock verification, local audit logging, and simulated Datalake 3.0 sync recovery. The final native production path is documented for React Native integration using MobileFaceNet INT8, passive liveness, active liveness, encrypted SQLite storage, and an offline-to-online sync/purge mechanism.

## Requirements

Planned implementation requirements:

- Node.js LTS
- React Native or Expo
- Python 3.10+
- OpenCV
- Lightweight face recognition model
- Mobile liveness detection model

## Repository Setup

Clone the repository:

```powershell
git clone https://github.com/bhavikdeshmukh/NHAI-Offline-Facial-Recognition-System.git
cd "NHAI-Offline-Facial-Recognition-System"
```

## Open Current Prototype

The current demo is a static browser prototype. Open this file directly:

```txt
index.html
```

No dependency installation is required for the prototype.

For phone camera testing, open the GitHub Pages HTTPS URL on the phone. Browser camera access usually requires HTTPS or localhost.

Vercel can also host the same static prototype. Import the GitHub repository in Vercel and keep the default static settings. The included `vercel.json` sets a camera permission policy header for the demo.

The Vercel deployment includes `/api/sync`, a small serverless endpoint used by the Sync Queue demo.

Current phone-demo flow:

1. Open Enroll.
2. Start camera.
3. Capture center sample.
4. Look slightly left and capture left sample.
5. Look slightly right and capture right sample.
6. If the frame is blurry or lighting is poor, the app asks you to retake.
7. Open Verify.
8. Start camera.
9. Tap Analyze and Unlock to recapture and unlock.
10. Open Sync Queue to show the locally queued event.
11. Tap Simulate Online Sync to show offline-to-online recovery.

The local enrollment is saved in browser storage on that phone. Clearing browser site data removes it.

Install dependencies after the app scaffold is added:

```powershell
npm install
```

Run the mobile app after the React Native or Expo setup is added:

```powershell
npm start
```

## Native React Native Implementation Path

1. Replace browser camera access with `react-native-vision-camera`.
2. Move CLAHE preprocessing into a native frame processor or OpenCV bridge.
3. Add BlazeFace or SCRFD-lite for face detection and aligned 112x112 crops.
4. Replace the temporary browser embedding with `mobilefacenet_int8.tflite`.
5. Add passive anti-spoofing with a lightweight FASNet/Silent-Face style model.
6. Add an active challenge prompt such as blink, head turn, or smile.
7. Store embeddings and verification logs in encrypted SQLite.
8. Sync queued logs to Datalake 3.0/AWS after network recovery and purge synced records by retention policy.

## Troubleshooting

If folders do not appear after pulling from GitHub, make sure each empty folder has a `.gitkeep` file. Git tracks files, not empty folders.
