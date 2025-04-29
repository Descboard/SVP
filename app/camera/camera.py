import cv2

class Camera:
    def __init__(self, source=0):
        self.source = source
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise Exception("No se pudo abrir la cámara.")

    def get_frame(self):
        if self.cap is None:
            raise Exception("La cámara no ha sido iniciada.")
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("No se pudo leer el frame de la cámara.")
        return frame

    def stop(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
 
