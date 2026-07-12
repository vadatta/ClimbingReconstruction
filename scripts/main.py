import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import json
import numpy as np
import sys
from roi_tracker import initialize_hand_roi
from config import CONFIG
from model import GripResNet

BONES = [
    (0, 1), (1, 2), (2, 3),  # right leg
    (0, 4), (4, 5), (5, 6),  # left leg
    (0, 7), (7, 8), (8, 9), (9, 10),  # spine/head
    (8, 11), (11, 12), (12, 13),  # left arm
    (8, 14), (14, 15), (15, 16)  # right arm
]

labels = {0: "Crimp", 1: "None", 2: "Pinch", 3: "Sloper"}
model = GripResNet(num_classes=len(labels)).to(CONFIG["device"])
model.eval()

LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_ELBOW = 13
RIGHT_ElBOW = 14


def setup_landmarker(pose_path, hand_path):
    # Base model options
    base_options = python.BaseOptions(
        model_asset_path=pose_path,
        delegate=python.BaseOptions.Delegate.CPU
    )

    # Pose-specific options
    pose_options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,  # one climber
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=True  # optional
    )

    pose_landmarker = vision.PoseLandmarker.create_from_options(
        pose_options
    )

    hand_base = python.BaseOptions(
        model_asset_path=hand_path,
        delegate=python.BaseOptions.Delegate.CPU
    )

    hand_options = vision.HandLandmarkerOptions(
        base_options=hand_base,
        running_mode=vision.RunningMode.VIDEO,
        min_hand_detection_confidence=0.3,
        min_tracking_confidence=0.3,
        num_hands=1
    )

    left_hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)
    right_hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)

    return pose_landmarker, left_hand_landmarker, right_hand_landmarker

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


def process_video(video_path, attempt_id, board_homography):
    left_grip_label = "Unknown"
    right_grip_label = "Unknown"

    frame_index = 0

    pose_landmarker, left_hand_landmarker, right_hand_landmarker = setup_landmarker(
        "./models/pose_landmarker_lite.task", "./models/hand_landmarker.task")

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        print(f"Error: Could not open video file '{video_path}'")
        return None

    frames = []

    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break
        height, width, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )
        pose_results = pose_landmarker.detect_for_video(image, frame_index)

        if pose_results.pose_landmarks:
            pose_landmarks = pose_results.pose_landmarks[0]
            frame_data = {
                "t": frame_index / 1000.0,
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

            left_wrist = pose_landmarks[LEFT_WRIST]
            right_wrist = pose_landmarks[RIGHT_WRIST]
            left_elbow = pose_landmarks[LEFT_ELBOW]
            right_elbow = pose_landmarks[RIGHT_ElBOW]

            if frame_index % 10 == 0:
                left_hand_roi = initialize_hand_roi(frame, left_wrist, left_elbow, width, height)
                right_hand_roi = initialize_hand_roi(frame, right_wrist, right_elbow, width, height)

                if left_hand_roi is not None:
                    left_grip = model(left_hand_roi)
                    left_grip_label = labels[left_grip.argmax(dim=1).item()]
                    #left_hand_data = getGripData(left_class, True)
                if right_hand_roi is not None:
                    right_grip = model(right_hand_roi)
                    right_grip_label = labels[right_grip.argmax(dim=1).item()]
                    #right_hand_data = getGripData(right_class, False)

            #frame_data["LeftHand"] = left_hand_data
            #frame_data["RightHand"] = right_hand_data
            frame_data["LeftGrip"] = left_grip_label
            frame_data["RightGrip"] = right_grip_label
            frames.append(frame_data)
        frame_index += 1

    capture.release()
    pose_landmarker.close()
    left_hand_landmarker.close()
    right_hand_landmarker.close()
    cv2.destroyAllWindows()

    return {
        "id": attempt_id,
        "source_video": video_path,
        "fps": 30,
        "frame_count": len(frames),
        "frames": frames
    }


def main(video_paths):
    video_paths = video_paths[:MAX_ATTEMPTS]
    board_homography = create_board_homography(SESSION_METADATA)
    attempts = []

    for index, video_path in enumerate(video_paths, start=1):
        attempt = process_video(video_path, f"attempt_{index}", board_homography)
        if attempt is not None:
            attempts.append(attempt)

    output = {
        "session": SESSION_METADATA,
        "attempt_count": len(attempts),
        "attempts": attempts
    }

    with open("./data/climb_attempts.json", "w") as f:
        json.dump(output, f)

    if attempts:
        legacy_output = {
            "fps": attempts[0]["fps"],
            "frame_count": attempts[0]["frame_count"],
            "frames": attempts[0]["frames"]
        }

        with open("./data/climb_motion.json", "w") as f:
            json.dump(legacy_output, f)


if __name__ == "__main__":
    video_paths = sys.argv[1:] or DEFAULT_VIDEO_PATHS
    main(video_paths)
