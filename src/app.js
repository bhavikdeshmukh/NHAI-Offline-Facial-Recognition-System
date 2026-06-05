const tabs = document.querySelectorAll(".nav-tab");
const screens = document.querySelectorAll(".screen");
const title = document.querySelector("#screen-title");
const actionButtons = document.querySelectorAll("[data-go]");

const verifyCamera = document.querySelector("#verify-camera");
const enrollCamera = document.querySelector("#enroll-camera");
const verifyStage = document.querySelector("#verify .camera-stage");
const verifyStatus = document.querySelector("#verify-status");
const enrollStatus = document.querySelector("#enroll-status");
const storedPreview = document.querySelector("#stored-preview");
const pendingSyncCount = document.querySelector("#pending-sync-count");
const syncQueueList = document.querySelector("#sync-queue-list");
const resultIcon = document.querySelector("#result-icon");
const resultTitle = document.querySelector("#result-title");
const resultMessage = document.querySelector("#result-message");
const matchScore = document.querySelector("#match-score");
const templateState = document.querySelector("#template-state");
const captureEnrollmentButton = document.querySelector("#capture-enrollment");
const qualityMeterFill = document.querySelector("#quality-meter-fill");
const sampleProgress = document.querySelectorAll("#sample-progress span");
const metricEnrollment = document.querySelector("#metric-enrollment");
const metricLatency = document.querySelector("#metric-latency");
const lockStateTitle = document.querySelector("#lock-state-title");

const STORAGE_KEY = "nhai.offlineFaceTemplate.v1";
const SYNC_QUEUE_KEY = "nhai.pendingSyncQueue.v1";
const MATCH_THRESHOLD = 0.86;
const MIN_SHARPNESS = 0.026;
const MIN_BRIGHTNESS = 0.18;
const MAX_BRIGHTNESS = 0.88;
const ENROLLMENT_POSES = ["Center", "Left", "Right"];

let cameraStream = null;
let enrollmentSamples = [];
let isUnlocked = false;

const screenTitles = {
  verify: "Offline Verification",
  enroll: "Officer Enrollment",
  result: "Verification Result",
  sync: "Pending Sync Queue",
};

function showScreen(id) {
  screens.forEach((screen) => {
    screen.classList.toggle("active", screen.id === id);
  });

  tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.step === id);
  });

  title.textContent = screenTitles[id];
  refreshUiState();
}

function getStoredTemplate() {
  const raw = localStorage.getItem(STORAGE_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setStoredTemplate(template) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(template));
}

function clearStoredTemplate() {
  localStorage.removeItem(STORAGE_KEY);
  enrollmentSamples = [];
}

function getSyncQueue() {
  const raw = localStorage.getItem(SYNC_QUEUE_KEY);
  return raw ? JSON.parse(raw) : [];
}

function setSyncQueue(rows) {
  localStorage.setItem(SYNC_QUEUE_KEY, JSON.stringify(rows));
}

async function simulateOnlineSync() {
  const queue = getSyncQueue();
  let backendSyncedAt = new Date().toISOString();

  try {
    const pendingEvents = queue.filter((row) => row.status !== "Synced");
    const response = await fetch("/api/sync", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ events: pendingEvents }),
    });
    if (response.ok) {
      const payload = await response.json();
      backendSyncedAt = payload.syncedAt || backendSyncedAt;
    }
  } catch (error) {
    console.info("Backend sync unavailable; using local fallback.", error);
  }

  const syncedQueue = queue.map((row) => ({
    ...row,
    status: "Synced",
    syncedAt: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    backendSyncedAt,
  }));
  setSyncQueue(syncedQueue);
  renderSyncQueue();
}

function addSyncEvent(event) {
  const queue = getSyncQueue();
  queue.unshift({
    id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
    timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    ...event,
    status: "Pending",
  });
  setSyncQueue(queue.slice(0, 8));
}

async function startCamera(videoElement) {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error("Camera API is not available. Use HTTPS or localhost.");
  }

  if (!cameraStream) {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user",
        width: { ideal: 720 },
        height: { ideal: 960 },
      },
      audio: false,
    });
  }

  videoElement.srcObject = cameraStream;
  await videoElement.play();

  if (videoElement === verifyCamera) {
    verifyStage.classList.add("camera-on");
  }
}

function captureFrame(videoElement, size = 112) {
  if (!videoElement.videoWidth || !videoElement.videoHeight) {
    throw new Error("Camera is not ready yet.");
  }

  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d", { willReadFrequently: true });

  const sourceSide = Math.min(videoElement.videoWidth, videoElement.videoHeight);
  const sourceX = (videoElement.videoWidth - sourceSide) / 2;
  const sourceY = (videoElement.videoHeight - sourceSide) / 2;
  context.drawImage(videoElement, sourceX, sourceY, sourceSide, sourceSide, 0, 0, size, size);

  return {
    imageData: context.getImageData(0, 0, size, size),
    preview: canvas.toDataURL("image/jpeg", 0.75),
  };
}

function evaluateFrameQuality(imageData) {
  const { data, width, height } = imageData;
  const grayscale = new Float32Array(width * height);
  let brightness = 0;

  for (let index = 0; index < grayscale.length; index += 1) {
    const pixelIndex = index * 4;
    const value =
      (0.299 * data[pixelIndex] + 0.587 * data[pixelIndex + 1] + 0.114 * data[pixelIndex + 2]) /
      255;
    grayscale[index] = value;
    brightness += value;
  }

  brightness /= grayscale.length;

  let edgeEnergy = 0;
  let count = 0;
  for (let y = 1; y < height - 1; y += 1) {
    for (let x = 1; x < width - 1; x += 1) {
      const center = grayscale[y * width + x] * 4;
      const neighbors =
        grayscale[y * width + x - 1] +
        grayscale[y * width + x + 1] +
        grayscale[(y - 1) * width + x] +
        grayscale[(y + 1) * width + x];
      edgeEnergy += Math.abs(center - neighbors);
      count += 1;
    }
  }

  const sharpness = edgeEnergy / count;
  const score = Math.max(
    0,
    Math.min(
      100,
      Math.round(
        (sharpness / MIN_SHARPNESS) * 55 +
          (1 - Math.abs(brightness - 0.52) / 0.52) * 45,
      ),
    ),
  );

  return {
    brightness,
    sharpness,
    score,
    isGood:
      sharpness >= MIN_SHARPNESS &&
      brightness >= MIN_BRIGHTNESS &&
      brightness <= MAX_BRIGHTNESS,
  };
}

function normalizeVector(vector) {
  const norm = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
  return norm === 0 ? vector : vector.map((value) => value / norm);
}

function createTemporaryEmbedding(imageData) {
  const { data, width } = imageData;
  const grayscale = new Float32Array(width * width);

  for (let index = 0; index < grayscale.length; index += 1) {
    const pixelIndex = index * 4;
    grayscale[index] =
      (0.299 * data[pixelIndex] + 0.587 * data[pixelIndex + 1] + 0.114 * data[pixelIndex + 2]) / 255;
  }

  const values = [];
  const blockSize = width / 8;

  for (let blockY = 0; blockY < 8; blockY += 1) {
    for (let blockX = 0; blockX < 8; blockX += 1) {
      let total = 0;
      for (let y = blockY * blockSize; y < (blockY + 1) * blockSize; y += 1) {
        for (let x = blockX * blockSize; x < (blockX + 1) * blockSize; x += 1) {
          total += grayscale[y * width + x];
        }
      }
      values.push(total / (blockSize * blockSize));
    }
  }

  for (let blockY = 0; blockY < 8; blockY += 1) {
    for (let blockX = 0; blockX < 8; blockX += 1) {
      let total = 0;
      for (let y = blockY * blockSize; y < (blockY + 1) * blockSize; y += 1) {
        for (let x = blockX * blockSize; x < (blockX + 1) * blockSize; x += 1) {
          const current = grayscale[y * width + x];
          const right = grayscale[y * width + Math.min(width - 1, x + 1)];
          const bottom = grayscale[Math.min(width - 1, y + 1) * width + x];
          total += Math.hypot(right - current, bottom - current);
        }
      }
      values.push(total / (blockSize * blockSize));
    }
  }

  return normalizeVector(values);
}

function calculateCosineSimilarity(vectorA, vectorB) {
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let index = 0; index < vectorA.length; index += 1) {
    dotProduct += vectorA[index] * vectorB[index];
    normA += vectorA[index] * vectorA[index];
    normB += vectorB[index] * vectorB[index];
  }

  if (normA === 0 || normB === 0) {
    return 0;
  }

  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

function averageEmbeddings(embeddings) {
  const length = embeddings[0].length;
  const average = Array.from({ length }, () => 0);
  embeddings.forEach((embedding) => {
    embedding.forEach((value, index) => {
      average[index] += value;
    });
  });
  return normalizeVector(average.map((value) => value / embeddings.length));
}

function updateEnrollmentProgress() {
  sampleProgress.forEach((item, index) => {
    item.classList.toggle("done", index < enrollmentSamples.length);
    item.classList.toggle("active", index === enrollmentSamples.length);
  });

  const nextPose = ENROLLMENT_POSES[enrollmentSamples.length] || "Complete";
  captureEnrollmentButton.textContent =
    enrollmentSamples.length >= ENROLLMENT_POSES.length
      ? "Enrollment Complete"
      : `Capture ${nextPose} Sample`;
  metricEnrollment.textContent = `${Math.min(enrollmentSamples.length, 3)}/3`;
}

async function enrollCurrentFace() {
  await startCamera(enrollCamera);
  const capture = captureFrame(enrollCamera);
  const quality = evaluateFrameQuality(capture.imageData);
  qualityMeterFill.style.width = `${quality.score}%`;

  if (!quality.isGood) {
    const reason =
      quality.sharpness < MIN_SHARPNESS
        ? "Frame too blurry. Hold phone steady and retake."
        : "Lighting is not balanced. Face a softer light source.";
    enrollStatus.textContent = `${reason} Sharpness ${quality.sharpness.toFixed(3)}, brightness ${quality.brightness.toFixed(2)}.`;
    return;
  }

  const embedding = createTemporaryEmbedding(capture.imageData);
  const pose = ENROLLMENT_POSES[enrollmentSamples.length];
  enrollmentSamples.push({
    pose,
    embedding,
    preview: capture.preview,
    quality,
  });

  if (enrollmentSamples.length < ENROLLMENT_POSES.length) {
    enrollStatus.textContent = `${pose} sample accepted. Now look ${ENROLLMENT_POSES[enrollmentSamples.length].toLowerCase()} and capture again.`;
    updateEnrollmentProgress();
    return;
  }

  setStoredTemplate({
    officerId: "NHAI-FIELD-2048",
    embedding: averageEmbeddings(enrollmentSamples.map((sample) => sample.embedding)),
    samples: enrollmentSamples,
    preview: enrollmentSamples[0].preview,
    createdAt: new Date().toISOString(),
    method: "temporary-browser-embedding-3-sample-average",
  });

  enrollStatus.textContent = "3-sample local enrollment saved in this browser cache.";
  refreshUiState();
}

async function verifyCurrentFace() {
  const template = getStoredTemplate();
  if (!template) {
    verifyStatus.textContent = "No local enrollment found. Open Enroll and save a template first.";
    showScreen("enroll");
    return;
  }

  await startCamera(verifyCamera);
  const start = performance.now();
  verifyStatus.textContent = "Analyzing live face locally...";

  const attempts = [];
  for (let index = 0; index < 3; index += 1) {
    await new Promise((resolve) => setTimeout(resolve, index === 0 ? 0 : 120));
    const capture = captureFrame(verifyCamera);
    const quality = evaluateFrameQuality(capture.imageData);
    const liveEmbedding = createTemporaryEmbedding(capture.imageData);
    const score = calculateCosineSimilarity(liveEmbedding, template.embedding);
    attempts.push({ score, quality });
  }

  const validAttempts = attempts.filter((attempt) => attempt.quality.brightness >= MIN_BRIGHTNESS);
  if (!validAttempts.length) {
    verifyStatus.textContent = "Verification lighting is poor. Move to softer light and retake.";
    return;
  }

  const bestAttempt = validAttempts.reduce((best, attempt) =>
    attempt.score > best.score ? attempt : best,
  );
  const score = bestAttempt.score;
  const elapsedMs = Math.round(performance.now() - start);
  const isMatch = score >= MATCH_THRESHOLD;
  isUnlocked = isMatch;

  addSyncEvent({
    officerId: template.officerId,
    decision: isMatch ? "Unlocked offline" : "Locked - verification failed",
    score: score.toFixed(4),
    elapsedMs,
  });

  resultIcon.textContent = isMatch ? "OK" : "NO";
  resultIcon.style.background = isMatch ? "var(--green)" : "var(--red)";
  resultTitle.textContent = isMatch ? "System Unlocked Offline" : "System Remains Locked";
  resultMessage.textContent = isMatch
    ? `Best-of-three local analysis passed in ${elapsedMs} ms. Event saved to pending sync queue.`
    : `Best-of-three local analysis failed. Recenter your face and tap unlock again.`;
  matchScore.textContent = `${Math.round(score * 100)}%`;
  metricLatency.textContent = `${elapsedMs} ms`;
  templateState.textContent = "Saved";
  verifyStatus.textContent = isMatch ? "Unlocked using local browser template." : "Locked. Tap Analyze and Unlock to recapture.";
  refreshUiState();
  showScreen("result");
}

function renderSyncQueue() {
  const queue = getSyncQueue();
  const pendingCount = queue.filter((row) => row.status !== "Synced").length;
  pendingSyncCount.textContent = `${pendingCount} pending sync${pendingCount === 1 ? "" : "s"}`;

  if (!queue.length) {
    syncQueueList.innerHTML = '<p class="inline-status">No pending local events yet.</p>';
    return;
  }

  syncQueueList.innerHTML = queue
    .map(
      (row) => `
        <div class="queue-row">
          <span>${row.timestamp}</span>
          <strong>${row.decision}<br><small>${row.score} | ${row.elapsedMs} ms${row.syncedAt ? ` | synced ${row.syncedAt}` : ""}</small></strong>
          <em>${row.status}</em>
        </div>
      `,
    )
    .join("");
}

function refreshUiState() {
  const template = getStoredTemplate();
  if (template) {
    enrollStatus.textContent = `3-sample template saved for ${template.officerId}. Stored only on this browser.`;
    storedPreview.src = template.preview;
    storedPreview.classList.add("visible");
    templateState.textContent = "Saved";
    metricEnrollment.textContent = `${template.samples?.length || 1}/3`;
  } else {
    storedPreview.removeAttribute("src");
    storedPreview.classList.remove("visible");
    templateState.textContent = "Missing";
    metricEnrollment.textContent = `${enrollmentSamples.length}/3`;
  }

  lockStateTitle.textContent = isUnlocked ? "System Unlocked" : "System Locked";
  updateEnrollmentProgress();
  renderSyncQueue();
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => showScreen(tab.dataset.step));
});

actionButtons.forEach((button) => {
  button.addEventListener("click", () => showScreen(button.dataset.go));
});

document.querySelector("#start-verify-camera").addEventListener("click", async () => {
  try {
    await startCamera(verifyCamera);
    verifyStatus.textContent = "Camera ready. Capture to unlock.";
  } catch (error) {
    verifyStatus.textContent = error.message;
  }
});

document.querySelector("#start-enroll-camera").addEventListener("click", async () => {
  try {
    await startCamera(enrollCamera);
    enrollStatus.textContent = "Camera ready. Capture enrollment sample.";
  } catch (error) {
    enrollStatus.textContent = error.message;
  }
});

document.querySelector("#capture-enrollment").addEventListener("click", async () => {
  try {
    await enrollCurrentFace();
  } catch (error) {
    enrollStatus.textContent = error.message;
  }
});

document.querySelector("#capture-verification").addEventListener("click", async () => {
  try {
    await verifyCurrentFace();
  } catch (error) {
    verifyStatus.textContent = error.message;
  }
});

document.querySelector("#clear-enrollment").addEventListener("click", () => {
  clearStoredTemplate();
  enrollStatus.textContent = "Local template cleared.";
  refreshUiState();
});

document.querySelector("#sync-now").addEventListener("click", async () => {
  await simulateOnlineSync();
});

refreshUiState();
