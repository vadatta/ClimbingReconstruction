import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import json
import numpy as np
import sys
import time
import torch
from roi_tracker import initialize_hand_roi
from config import CONFIG
from model import GripResNet

LABELS = {0: "Crimp", 1: "None", 2: "Pinch", 3: "Sloper"}

LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_ELBOW = 13
RIGHT_ELBOW = 14


def setup_landmarker(pose_path):
    base_options = python.BaseOptions(
        model_asset_path=pose_path,
        delegate=python.BaseOptions.Delegate.CPU
    )

    pose_options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False
    )

    return vision.PoseLandmarker.create_from_options(pose_options)

MAX_ATTEMPTS = 3
DEFAULT_VIDEO_PATHS = ["./data/data.mp4"]
SESSION_METADATA = {
    "board": {
        "type": "MoonBoard",
        "angle_degrees": 40
    },
    "climb": {
        "name": "Prototype Climb",
        "grade": "Unknown"
    },
    "calibration": {
        "coordinate_system": "normalized_board_space",
        "image_corners": {
            "bottom_left": [120, 900],
            "bottom_right": [820, 900],
            "top_right": [820, 120],
            "top_left": [120, 120]
        },
        "board_corners": {
            "bottom_left": [0.0, 0.0],
            "bottom_right": [1.0, 0.0],
            "top_right": [1.0, 1.0],
            "top_left": [0.0, 1.0]
        }
    }
}


def ordered_corner_points(corners):
    return np.float32([
        corners["bottom_left"],
        corners["bottom_right"],
        corners["top_right"],
        corners["top_left"]
    ])


def create_board_homography(session_metadata):
    calibration = session_metadata["calibration"]
    image_points = ordered_corner_points(calibration["image_corners"])
    board_points = ordered_corner_points(calibration["board_corners"])

    return cv2.getPerspectiveTransform(image_points, board_points)


def transform_landmarks_to_board_space(landmarks, homography, width, height):
    pixel_points = np.float32([
        [[lm.x * width, lm.y * height]]
        for lm in landmarks
    ])
    board_points = cv2.perspectiveTransform(pixel_points, homography)

    return [
        {
            "x": float(point[0][0]),
            "y": float(point[0][1]),
            "z": lm.z
        }
        for point, lm in zip(board_points, landmarks)
    ]


def classify_grips(frame, pose_landmarks, width, height, grip_model):
    roi_tensors = []
    roi_sides = []

    for side, wrist_index, elbow_index in (
        ("left", LEFT_WRIST, LEFT_ELBOW),
        ("right", RIGHT_WRIST, RIGHT_ELBOW)
    ):
        roi = initialize_hand_roi(
            frame,
            pose_landmarks[wrist_index],
            pose_landmarks[elbow_index],
            width,
            height
        )
        if roi is not None:
            roi_tensors.append(roi)
            roi_sides.append(side)

    predictions = {}
    if roi_tensors:
        batch = torch.cat(roi_tensors, dim=0).to(CONFIG["device"])
        with torch.inference_mode():
            class_indices = grip_model(batch).argmax(dim=1).tolist()

        predictions = {
            side: LABELS[class_index]
            for side, class_index in zip(roi_sides, class_indices)
        }

    return predictions


def process_video(video_path, attempt_id, board_homography, grip_model):
    process_started = time.perf_counter()
    left_grip_label = "Unknown"
    right_grip_label = "Unknown"
    frame_index = 0
    pose_seconds = 0.0
    grip_seconds = 0.0
    grip_batches = 0
    frame_latencies_ms = []
    pose_landmarker = setup_landmarker("./models/pose_landmarker_lite.task")

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        pose_landmarker.close()
        print(f"Error: Could not open video file '{video_path}'")
        return None

    source_fps = capture.get(cv2.CAP_PROP_FPS)
    if source_fps <= 0:
        source_fps = 30.0

    frames = []

    while True:
        frame_started = time.perf_counter()
        ret, frame = capture.read()
        if not ret:
            break

        height, width, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )
        timestamp_ms = round(frame_index * 1000 / source_fps)

        pose_started = time.perf_counter()
        pose_results = pose_landmarker.detect_for_video(image, timestamp_ms)
        pose_seconds += time.perf_counter() - pose_started

        if pose_results.pose_landmarks:
            pose_landmarks = pose_results.pose_landmarks[0]
            frame_data = {
                "t": timestamp_ms / 1000.0,
                "landmarks": [
                    {
                        "x": lm.x,
                        "y": lm.y,
                        "z": lm.z
                    }
                    for lm in pose_landmarks
                ],
                "board_landmarks": transform_landmarks_to_board_space(
                    pose_landmarks,
                    board_homography,
                    width,
                    height
                )
            }

            if frame_index % 10 == 0:
                grip_started = time.perf_counter()
                grip_predictions = classify_grips(
                    frame,
                    pose_landmarks,
                    width,
                    height,
                    grip_model
                )
                grip_seconds += time.perf_counter() - grip_started
                grip_batches += 1
                left_grip_label = grip_predictions.get("left", left_grip_label)
                right_grip_label = grip_predictions.get("right", right_grip_label)

            frame_data["LeftGrip"] = left_grip_label
            frame_data["RightGrip"] = right_grip_label
            frames.append(frame_data)

        frame_latencies_ms.append(
            (time.perf_counter() - frame_started) * 1000
        )
        frame_index += 1

    capture.release()
    pose_landmarker.close()
    process_seconds = time.perf_counter() - process_started

    return {
        "id": attempt_id,
        "source_video": video_path,
        "fps": source_fps,
        "frame_count": len(frames),
        "frames": frames,
        "processing_metrics": {
            "decoded_frames": frame_index,
            "pose_frames": len(frames),
            "processing_seconds": process_seconds,
            "processing_fps": frame_index / process_seconds if process_seconds else 0,
            "average_frame_latency_ms": (
                float(np.mean(frame_latencies_ms)) if frame_latencies_ms else 0
            ),
            "p50_frame_latency_ms": (
                float(np.percentile(frame_latencies_ms, 50))
                if frame_latencies_ms else 0
            ),
            "p95_frame_latency_ms": (
                float(np.percentile(frame_latencies_ms, 95))
                if frame_latencies_ms else 0
            ),
            "average_pose_latency_ms": (
                pose_seconds * 1000 / frame_index if frame_index else 0
            ),
            "average_grip_batch_latency_ms": (
                grip_seconds * 1000 / grip_batches if grip_batches else 0
            ),
            "grip_batches": grip_batches
        }
    }


def main(video_paths):
    pipeline_started = time.perf_counter()
    video_paths = video_paths[:MAX_ATTEMPTS]
    board_homography = create_board_homography(SESSION_METADATA)
    grip_model = GripResNet(num_classes=len(LABELS)).to(CONFIG["device"])
    grip_model.eval()
    attempts = []

    for index, video_path in enumerate(video_paths, start=1):
        attempt = process_video(
            video_path,
            f"attempt_{index}",
            board_homography,
            grip_model
        )
        if attempt is not None:
            attempts.append(attempt)

    output = {
        "session": SESSION_METADATA,
        "attempt_count": len(attempts),
        "attempts": attempts
    }

    with open("./data/climb_attempts.json", "w") as f:
        json.dump(output, f, separators=(",", ":"))

    if attempts:
        legacy_output = {
            "fps": attempts[0]["fps"],
            "frame_count": attempts[0]["frame_count"],
            "frames": attempts[0]["frames"]
        }

        with open("./data/climb_motion.json", "w") as f:
            json.dump(legacy_output, f, separators=(",", ":"))

    pipeline_seconds = time.perf_counter() - pipeline_started
    decoded_frames = sum(
        attempt["processing_metrics"]["decoded_frames"]
        for attempt in attempts
    )
    print(json.dumps({
        "end_to_end_seconds": pipeline_seconds,
        "end_to_end_fps": (
            decoded_frames / pipeline_seconds if pipeline_seconds else 0
        ),
        "attempts": [
            {
                "id": attempt["id"],
                **attempt["processing_metrics"]
            }
            for attempt in attempts
        ]
    }, indent=2))


if __name__ == "__main__":
    video_paths = sys.argv[1:] or DEFAULT_VIDEO_PATHS
    main(video_paths)
