import cv2
import easyocr
import torch

class PlateDetector:
    #def __init__(self):
        # Activamos la GPU si está disponible
        #self.reader = easyocr.Reader(['en'], gpu=True)  # Cambiar a gpu=True
        #self.reader = easyocr.Reader(['en'], gpu=False)
    def __init__(self):
        # Verificar si la GPU está disponible
        if torch.cuda.is_available():
            print("✅ GPU disponible: EasyOCR usará GPU.")
            print("GPU disponible, utilizando GPU para EasyOCR.")
            self.reader = easyocr.Reader(['en'], gpu=True)  # Usar GPU si está disponible
        else:
            print("⚠️ GPU no disponible: EasyOCR usará CPU.")
            print("GPU no disponible, utilizando CPU para EasyOCR.")
            self.reader = easyocr.Reader(['en'], gpu=False)  # Usar CPU si no hay GPU



    def detect_plate(self, frame):
        results = []

        # Convertir a escala de grises si es necesario
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        # Mejora de imagen
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(gray, 30, 200)

        # Detección de contornos
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.018 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4:  # Posible forma de placa
                x, y, w, h = cv2.boundingRect(approx)
                plate_img = gray[y:y+h, x:x+w]

                # Aplicar OCR a la región
                ocr_results = self.reader.readtext(plate_img)
                for (_, text, confidence) in ocr_results:
                    clean_text = text.strip().upper()
                    if 4 <= len(clean_text) <= 8:
                        results.append((clean_text, f"{confidence*100:.2f}%"))
                        # Dibujar rectángulo sobre la placa detectada
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        return results, frame
