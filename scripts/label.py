import cv2
import os

path = "dataset/raw"
files = os.listdir(path)

for f in files:
    img = cv2.imread(os.path.join(path,f))
    cv2.imshow("img", img)

    key = cv2.waitKey(0)

    if key == ord('c'):
        label = "crimp"
    elif key == ord('s'):
        label = "sloper"
    elif key == ord('p'):
        label = "pinch"
    elif key == ord('n'):
        label = 'None'
    elif key == ord('q'):
        break

    dst = os.path.join("dataset", label, f)

    if os.path.exists(dst):
        name, ext = os.path.splitext(f)
        dst = os.path.join("data", label, name + "_1" + ext)

    os.rename(os.path.join(path, f), dst)