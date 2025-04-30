import cv2
import threading
import logging

class Camera:
    def __init__(self, camera_index=0, width=640, height=480):
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        logging.basicConfig(level=logging.INFO)

    def start(self):
        self.running = True
        thread = threading.Thread(target=self.update, daemon=True)
        thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                with self.lock:
                    self.frame = gray

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        self.cap.release()
