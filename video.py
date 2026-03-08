import cv2 as cv
import numpy as np

class Video:
    def __init__(self):
        self.cap = cv.VideoCapture(0)

        # manual exposure
        self.cap.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to receive frame")

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # smooth first frame to remove edges
        self.prev_frame = cv.GaussianBlur(gray, (9,9), 0)

    def get_quantum_bits(self):

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to receive frame")

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # difference between frames
        diff = cv.absdiff(gray, self.prev_frame)

        # amplify small noise so it becomes visible
        diffnorm = diff.astype(np.float32) * 25
        condition = diffnorm > 100
        noise_metric = float(diffnorm[condition].mean()) if np.any(condition) else float(np.mean(diffnorm))
        ret, diffnorm = cv.threshold(diffnorm, 100, 0, cv.THRESH_TOZERO_INV)
        diffnorm = np.clip(diffnorm, 0, 255).astype(np.uint8)
        print('iteration')
        #cv.imwrite("nonedges.png", non_edges)
        cv.imwrite("frame.png", gray)
        cv.imwrite("diff.png", diff)
        cv.imwrite("diffnorm.png", diffnorm)

        # compute noise metric
        noise_metric = float(np.mean(diff))
        print("noise metric:", noise_metric)
        # update frame history
        self.prev_frame = gray

        return noise_metric


def main():
    video = Video()
    while True:
        val = video.get_quantum_bits()
        print("Noise metric:", val)

if __name__ == "__main__":
    main()