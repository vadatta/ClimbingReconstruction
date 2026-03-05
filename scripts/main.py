import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import json
from roi_tracker import initialize_hand_roi, compute_roi

BONES = [
    (0, 1), (1, 2), (2, 3),  # right leg
    (0, 4), (4, 5), (5, 6),  # left leg
    (0, 7), (7, 8), (8, 9), (9, 10),  # spine/head
    (8, 11), (11, 12), (12, 13),  # left arm
    (8, 14), (14, 15), (15, 16)  # right arm
]

LEFT_WRIST = 15
RIGHT_WRIST = 16

def setup_landmarker(pose_path, hand_path):
    # Base model options
    base_options = python.BaseOptions(
        model_asset_path=pose_path
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
        model_asset_path=hand_path
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



def main(video_path):
    left_hand_roi = None

    right_hand_roi = None

    left_hand_data = None
    right_hand_data = None

    frame_index = 0

    pose_landmarker, left_hand_landmarker, right_hand_landmarker = setup_landmarker("./models/pose_landmarker_lite.task","./models/hand_landmarker.task")

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        print(f"Error: Could not open video file '{video_path}'")
        return

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
            frame_data = {
                "t": frame_index / 1000.0,
                "landmarks": [
                    {
                        "x": lm.x,
                        "y": lm.y,
                        "z": lm.z
                    }
                    for lm in pose_results.pose_landmarks[0]
                ]
            }

            left_wrist = pose_results.pose_landmarks[0][LEFT_WRIST]
            right_wrist = pose_results.pose_landmarks[0][RIGHT_WRIST]

            # initialize LEFT ROI
            # LEFT HAND

            if left_hand_roi is None and left_wrist:

                left_hand_roi, left_hand_data = initialize_hand_roi(
                    frame,
                    left_wrist,
                    left_hand_landmarker,
                    frame_index,
                    width,
                    height
                )

            elif left_hand_roi is not None:

                left_hand_data = compute_roi(
                    left_hand_roi,
                    frame,
                    left_hand_landmarker,
                    height,
                    width,
                    frame_index
                )

                if left_hand_data is None:
                    left_hand_roi = None

            # initialize right ROI
            # LEFT HAND

            if right_hand_roi is None and right_wrist:

                right_hand_roi, right_hand_data = initialize_hand_roi(
                    frame,
                    right_wrist,
                    right_hand_landmarker,
                    frame_index,
                    width,
                    height
                )

            elif right_hand_roi is not None:

                right_hand_data = compute_roi(
                    right_hand_roi,
                    frame,
                    right_hand_landmarker,
                    height,
                    width,
                    frame_index
                )

                if right_hand_data is None:
                    left_hand_roi = None

            frame_data["LeftHand"] = left_hand_data
            frame_data["RightHand"] = right_hand_data
            frames.append(frame_data)
        frame_index += 1

    capture.release()
    pose_landmarker.close()
    left_hand_landmarker.close()
    right_hand_landmarker.close()
    cv2.destroyAllWindows()
    output = {
        "fps": 30,
        "frame_count": len(frames),
        "frames": frames
    }

    with open("./data/climb_motion.json", "w") as f:
        json.dump(output, f)


if __name__ == "__main__":
    main("./data/still.mp4")
