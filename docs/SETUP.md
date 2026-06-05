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
