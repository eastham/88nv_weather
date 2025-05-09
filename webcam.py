"""This module captures frames from a webcam and saves them to disk."""

import time
import argparse
import cv2
import subprocess

class Webcam:
    """Class to capture frame from webcam and save it to file."""
    def __init__(self, camera_index=0):
        """Initialize the WordpressWebcam object. camera_index specifies
        which camera to use."""
        self.camera_index = camera_index


    def capset(self, cap, prop, value):
        ret = cap.set(prop, value)
        time.sleep(1)
        print(f"Set {prop} to {value}, returned {ret}")

    def capture_frame(self):
        cap = cv2.VideoCapture(self.camera_index)

        # enable auto exposure -- doesn't work on all cameras
        #self.capset(cap, cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)

        # set manual exposure level - also doesn't work on all cameras
        #self.capset(cap, cv2.CAP_PROP_EXPOSURE, -6)

        # set resolution
        self.capset(cap, cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capset(cap, cv2.CAP_PROP_FRAME_HEIGHT, 720)

        ret, frame = cap.read()
        cap.release()

        if ret:
            print("Frame captured")
            return frame

        print("Error: Unable to capture frame")
        return None

    def save_frame(self, frame, filename, text_prefix=""):
        """Annotate the image and save to disk."""
        text = text_prefix + time.ctime() + " " + time.tzname[time.daylight]

        # Add text in black and white to cover all background cases
        cv2.putText(frame, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        cv2.imwrite(filename, frame)


def main(time_interval=1, fname_prefix='frame'):
    webcam = Webcam()
    while True:
        frame = webcam.capture_frame()
        fname = fname_prefix + time.strftime("%Y%m%d_%H%M%S") + ".jpg"

        webcam.save_frame(frame, fname)

        subprocess.run(["open", fname])

        time.sleep(time_interval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--time_interval", type=int,
                        help="Time interval in seconds", default=10)
    args = parser.parse_args()

    main(args.time_interval, "./image")
