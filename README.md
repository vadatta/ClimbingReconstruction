Climbing Reconstruction with Pose Tracking and Grip Classification

A computer vision project for reconstructing a climber’s movement from video by combining full body pose estimation, hand ROI tracking, grip classification, and 3D visualization.

The pipeline takes an input video of someone climbing, reconstructs body pose using MediaPipe, continuously tracks hand regions with ROI tracking, and classifies each tracked hand crop into a specific climbing grip type. These grip predictions are then used to guide hand reconstruction, and the final pose and hand data are combined into a visualization in Three.js. Motion is smoothed using a One Euro Filter for more stable movement. 

This project is still under construction, with the next major step being to run MediaPipe on clean hand pose images for more complete hand reconstruction.

Features

- Video based climbing motion analysis
- Full body pose reconstruction using MediaPipe
- Continuous hand ROI tracking across frames
- Hand grip classification from tracked hand crops
- Grip specific hand reconstruction pipeline
- Combined body and hand visualization in Three.js
- Temporal smoothing with a One Euro Filter

How It Works

1. An input video of a climber is processed frame by frame.
2. MediaPipe extracts body pose landmarks for overall pose reconstruction.
3. Hand ROIs are tracked over time to isolate the climber’s hands.
4. The tracked hand crops are passed into a classification model.
5. The classifier predicts a grip class, where each class corresponds to a specific climbing grip type.
6. Clean reference images for the predicted grip are used as the basis for detailed hand reconstruction.
7. The reconstructed hand information is merged with the body pose data.
8. The final motion is visualized in Three.js and smoothed with a One Euro Filter.
