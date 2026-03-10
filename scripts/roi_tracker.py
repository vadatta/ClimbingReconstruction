import math

import cv2
import mediapipe as mp
import numpy as np

LEFT_WRIST = 15
RIGHT_WRIST = 16


def estimate_palm_from_hand(hand_results):
    palm_x = (hand_results[0].x + hand_results[5].x + hand_results[9].x
              + hand_results[13].x + hand_results[17].x) / 5
    palm_y = (hand_results[0].y + hand_results[5].y + hand_results[9].y
              + hand_results[13].y + hand_results[17].y) / 5

    return palm_x, palm_y


def initialize_hand_roi(frame, wrist, elbow, hand_landmarker, frame_index, width, height, sr):

    global roi_frame
    forearm_x = wrist.x - elbow.x
    forearm_y = wrist.y - elbow.y

    forearm_len = math.sqrt(forearm_x**2 + forearm_y**2)
    if forearm_len < 1e-6:
        return None, None
    x_direc = forearm_x / forearm_len
    y_direc = forearm_y / forearm_len

    px = -y_direc
    py = x_direc

    hand_size = forearm_len * width * 0.8

    forward = hand_size * 1.8
    side = hand_size * 0.9

    wx = wrist.x * width
    wy = wrist.y * height

    fx = x_direc * forward
    fy = y_direc * forward

    sx = px * side
    sy = py * side

    x1 = int(wx - sx)
    y1 = int(wy - sy)

    x2 = int(wx + fx + sx)
    y2 = int(wy + fy + sy)

    x3 = int(wx + sx)
    y3 = int(wy + sy)

    x4 = int(wx + fx - sx)
    y4 = int(wy + fy - sy)

    xmin = max(0, min(x1, x2, x3, x4))
    xmax = min(width, max(x1, x2, x3, x4))

    ymin = max(0, min(y1, y2, y3, y4))
    ymax = min(height, max(y1, y2, y3, y4))

    roi_frame = frame[ymin:ymax, xmin:xmax]
    if frame_index % 8 == 0:
        roi_frame = frame[ymin:ymax, xmin:xmax]
        roi = cv2.resize(roi_frame, (128, 128))

        cv2.imwrite(f"dataset/raw/frameM_{frame_index}.png", roi)



    rgb = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2RGB)

    image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    hand_results = hand_landmarker.detect_for_video(image, frame_index)

    if not hand_results.hand_landmarks:
        return None, None

    lms = hand_results.hand_landmarks[0]

    palm_x, palm_y = estimate_palm_from_hand(lms)

    crop_w = xmax - xmin
    crop_h = ymax - ymin

    px = palm_x * crop_w + xmin
    py = palm_y * crop_h + ymin

    hand_roi = {
        "cx": int(px),
        "cy": int(py),
        "confidence": 1
    }

    hand_data = []

    for lm in lms:
        gx = (lm.x * crop_w + xmin) / width
        gy = (lm.y * crop_h + ymin) / height

        hand_data.append({
            "x": gx,
            "y": gy,
            "z": lm.z
        })

    return hand_roi, hand_data


def compute_roi(hand_roi, frame, hand_landmarker, height, width, frame_index):
    size = 40

    x1 = max(0, hand_roi["cx"] - size)
    x2 = min(width, hand_roi["cx"] + size)

    y1 = max(0, hand_roi["cy"] - size)
    y2 = min(height, hand_roi["cy"] + size)

    roi_frame = frame[y1:y2, x1:x2]
    roi_frame = cv2.resize(roi_frame, (512, 512))

    rgb = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2RGB)

    image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    hand_results = hand_landmarker.detect_for_video(image, frame_index)

    if not hand_results.hand_landmarks:
        return None

    lms = hand_results.hand_landmarks[0]

    # palm center
    cx_local = (lms[0].x + lms[5].x + lms[9].x + lms[13].x + lms[17].x) / 5

    cy_local = (lms[0].y + lms[5].y + lms[9].y + lms[13].y + lms[17].y) / 5

    crop_w = x2 - x1
    crop_h = y2 - y1

    px = cx_local * crop_w + x1
    py = cy_local * crop_h + y1

    # smooth ROI movement
    alpha = 0.3

    hand_roi["cx"] = int((1 - alpha) * hand_roi["cx"] + alpha * px)
    hand_roi["cy"] = int((1 - alpha) * hand_roi["cy"] + alpha * py)

    # convert landmarks back to full frame coordinates
    hand_data = []

    for lm in lms:
        gx = (lm.x * crop_w + x1) / width
        gy = (lm.y * crop_h + y1) / height

        hand_data.append({
            "x": gx,
            "y": gy,
            "z": lm.z
        })

    return hand_data
