# Climb Motion

Climb Motion is a prototype for reconstructing and reviewing board-climbing
movement from fixed-camera video. It combines MediaPipe pose estimation, a
ResNet-based grip classifier, board-normalized coordinates, temporal smoothing,
and a Three.js viewer.

The current product flow focuses on one attempt. A user can choose a video,
board, angle, and climb in the browser, then open the existing reconstructed
motion in the viewer. Browser uploads are UI-only for now; Python preprocessing
is still run locally from the command line.

## Current Features

- MP4 selection from the frontend
- Board selection for:
  - Kilterboard
  - Tension Board 1
  - Tension Board 2 Spray Layout
  - Tension Board 2 Mirror Layout
- Angle selection from 30 to 60 degrees in 5-degree increments
- Board-filtered climb autocomplete using prototype fixture data
- MediaPipe Pose Landmarker processing with 33 body landmarks
- Perspective transformation into normalized board coordinates
- Left and right grip labels sampled every tenth video frame
- Cylinder-based Three.js skeleton visualization
- One Euro landmark filtering and smoothed bone orientation
- Processing latency metrics in the combined attempt output

## Project Structure

```text
scripts/
  main.py             Video processing and JSON generation
  model.py            GripResNet model definition
  dataCleaning.py     Training transforms, splits, and data loaders
  train.py            Training, evaluation, and blur experiments
  config.py           Training and runtime configuration
  roi_tracker.py      Hand-region extraction from pose landmarks

src/
  main.js             Frontend entry point
  ui/                 Attempt setup workflow and climb fixtures
  scene/              Three.js scene and reference helpers
  skeleton/           Pose and hand visualization modules
  animation/          Frame playback and bone updates
  filters/            One Euro filter implementation
```

Local videos, datasets, generated JSON, and model assets live in ignored
directories:

```text
data/
dataset/
models/
```

## Frontend

Install JavaScript dependencies and start Vite:

```bash
npm install
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173/`.

The setup form validates one video, board, angle, and climb. Selecting
**Analyze attempt** currently loads `data/climb_motion.json`; the selected video
is not uploaded or processed by the browser yet.

Climb names are temporary fixtures in
`src/ui/climbFixtures.js`. They are intentionally separated from the UI so a
BoardLib-backed catalog can replace them later.

To verify a production build:

```bash
npx vite build
```

## Python Setup

Use the project's virtual environment:

```bash
source venv/bin/activate
```

The processing and training code requires Python 3, OpenCV, MediaPipe, NumPy,
PyTorch, Torchvision, and Pillow. The expected model assets are:

```text
models/pose_landmarker_lite.task
models/hand_landmarker.task
```

The current optimized processing path only initializes the pose model. The hand
model asset remains reserved for future landmark-based hand reconstruction.

## Process Video

Process one video:

```bash
venv/bin/python scripts/main.py data/moonboard.mp4
```

The Python entry point still accepts up to three paths for pipeline experiments:

```bash
venv/bin/python scripts/main.py \
  data/attempt-1.mp4 \
  data/attempt-2.mp4 \
  data/attempt-3.mp4
```

It produces:

- `data/climb_attempts.json`: session metadata and distinctly separated attempts
- `data/climb_motion.json`: legacy frontend payload containing the first attempt

Each attempt includes the source FPS, pose frames, regular landmarks,
board-normalized landmarks, grip labels, and processing metrics.

Board metadata and placeholder calibration corners currently live in
`scripts/main.py`. Update the image corners to match the fixed camera view before
comparing board-relative movement.

## Timing Metrics

The pipeline reports:

- Total processing time and throughput
- Average, median, and p95 frame latency
- Average MediaPipe pose latency
- Average batched grip-classification latency
- Decoded and successfully reconstructed frame counts

On the development Apple M2 machine, `data/moonboard.mp4` produced the following
representative result:

| Metric | Result |
| --- | ---: |
| Source video | 631 frames at 29.97 FPS |
| Full process wall time | 13.76 s |
| Full-process throughput | 45.86 FPS |
| Average frame latency | 16.55 ms |
| Median frame latency | 13.95 ms |
| p95 frame latency | 33.95 ms |
| Average pose latency | 9.76 ms |
| Average grip batch latency | 24.68 ms |

These values depend on hardware, video resolution, model cache state, and pose
visibility. The same pipeline took 20.00 seconds before unused hand landmarkers,
segmentation masks, gradient tracking, and redundant grip inference were
removed.

## Train the Grip Classifier

Training uses an 80/20 seeded split, ImageNet normalization, random rotations,
color jitter, and a Gaussian blur sweep:

```bash
venv/bin/python scripts/train.py
```

The best measured validation result so far was approximately **87.63%** with a
Gaussian blur kernel of 3.

Important: training currently reports accuracy but does not save a model
checkpoint, and video processing does not load trained grip-classifier weights.
Checkpoint saving/loading must be added before the live grip labels represent
the measured validation model.

## Prototype Limitations

- Browser-selected videos are not sent to Python yet.
- The viewer currently displays only the first generated attempt.
- Climb search uses fixture data rather than BoardLib.
- Board calibration is hardcoded per session.
- Start-hold detection and attempt synchronization are not implemented.
- Pose depth is not reliable enough for accurate off-wall swing measurement.
- Grip classifier checkpoints are not persisted or loaded.

The next practical milestone is a local upload API that accepts the setup form,
runs `scripts/main.py`, and returns a generated attempt payload to the viewer.
