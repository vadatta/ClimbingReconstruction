import math

import cv2


LEFT_WRIST = 15
RIGHT_WRIST = 16

def initialize_hand_roi(frame, wrist, elbow, width, height):
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

    return hand_roi
