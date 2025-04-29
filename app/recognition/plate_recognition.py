import cv2
import easyocr

class PlateRecognizer:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def recognize_plate(self, frame):
        # Convertir la imagen a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detectar texto en la imagen
        results = self.reader.readtext(gray)
        plates = []
        for (bbox, text, prob) in results:
            # Filtrar resultados según la probabilidad y longitud del texto
            if prob > 0.5 and len(text) >= 5:
                plates.append((text, prob))
        return plates
