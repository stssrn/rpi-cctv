import cv2

from dataclasses import dataclass
from time import sleep


class CaptureError(Exception):
    """Raised when something went wrong during capturing"""


@dataclass
class Camera:
    camera_index: int = 0
    frame_count: int = 0
    framerate: int = 30
    width: int = 1280
    height: int = 720

    def start(self):
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.video_capture = cap

    def frames(self):
        """Camera frame generator"""
        while True:
            sleep(1 / self.framerate)
            success, frame = self.video_capture.read()
            if not success:
                raise CaptureError()

            yield frame
            self.frame_count += 1

    def stop(self):
        self.video_capture.release()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()
