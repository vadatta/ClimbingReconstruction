import cv2
import mediapipe as mp

LEFT_WRIST = 15
RIGHT_WRIST = 16


def estimate_palm_from_hand(hand_results):
    palm_x = (hand_results[0].x + hand_results[5].x + hand_results[9].x
              + hand_results[13].x + hand_results[17].x) / 5
    palm_y = (hand_results[0].y + hand_results[5].y + hand_results[9].y
              + hand_results[13].y + hand_results[17].y) / 5

    return palm_x, palm_y


def initialize_hand_roi(frame, wrist, hand_landmarker, frame_index, width, height):
    cx = int(wrist.x * width)
    cy = int(wrist.y * height)

    size = 30

    # create roi frame
    x1 = max(0, cx - size)
    x2 = min(width, cx + size)

    y1 = max(0, cy - size)
    y2 = min(height, cy + size)

    roi_frame = frame[y1:y2, x1:x2]
    roi_frame = cv2.resize(roi_frame, (512, 512))
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imwrite("roi_debug.png", frame)
    print("ROI center:", cx, cy)
    print("ROI frame:", frame_index)



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

    crop_w = x2 - x1
    crop_h = y2 - y1

    px = palm_x * crop_w + x1
    py = palm_y * crop_h + y1

    hand_roi = {
        "cx": int(px),
        "cy": int(py),
        "confidence": 1
    }

    hand_data = []

    for lm in lms:
        gx = (lm.x * crop_w + x1) / width
        gy = (lm.y * crop_h + y1) / height

        hand_data.append({
            "x": gx,
            "y": gy,
            "z": lm.z
        })

    return hand_roi, hand_data


def compute_roi(hand_roi, frame, hand_landmarker, height, width, frame_index):
    size = 30

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
