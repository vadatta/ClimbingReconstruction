import numpy as np
import cv2

def compute_velocity(curr, prev, dt=1):
    if prev is None:
        return 0

    return np.linalg.norm(np.array(curr) - np.array(prev)) / dt


def compute_entropy(image):

    hist = cv2.calcHist([image], [0], None, [256], [0,256])
    hist = hist / hist.sum()

    hist = hist[hist > 0]

    entropy = -np.sum(hist * np.log2(hist))

    return float(entropy)


