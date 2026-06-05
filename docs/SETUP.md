# Setup Guide

## Current Status

This repository is currently in the planning and scaffolding stage. The documentation, folder structure, and architecture are being prepared first so the implementation can be built cleanly.

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

Current phone-demo flow:

1. Open Enroll.
2. Start camera.
3. Capture center sample.
4. Look slightly left and capture left sample.
5. Look slightly right and capture right sample.
6. If the frame is blurry or lighting is poor, the app asks you to retake.
7. Open Verify.
8. Start camera.
9. Capture and unlock.
10. Open Sync Queue to show the locally queued event.

The local enrollment is saved in browser storage on that phone. Clearing browser site data removes it.

Install dependencies after the app scaffold is added:

```powershell
npm install
```

Run the mobile app after the React Native or Expo setup is added:

```powershell
npm start
```

## Planned Development Workflow

1. Build UI screens first.
2. Add local mock verification flow.
3. Add camera capture.
4. Add preprocessing and face embedding model.
5. Add liveness detection.
6. Add encrypted local storage.
7. Add offline sync queue.
8. Record final demo.

## Troubleshooting

If folders do not appear after pulling from GitHub, make sure each empty folder has a `.gitkeep` file. Git tracks files, not empty folders.
