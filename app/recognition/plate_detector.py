import cv2
import easyocr
import torch

class PlateDetector:
    def __init__(self):
        if torch.cuda.is_available():
            print("✅ GPU disponible: EasyOCR usará GPU.")
            self.reader = easyocr.Reader(['en'], gpu=True)
        else:
            print("⚠️ GPU no disponible: EasyOCR usará CPU.")
            self.reader = easyocr.Reader(['en'], gpu=False)

    def detect_plate(self, frame):
        results = []

        # 📸 Copia de seguridad en color para dibujar resultados
        if len(frame.shape) == 2 or frame.shape[2] == 1:
            frame_color = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        else:
            frame_color = frame.copy()

        # 🎨 Conversión a escala de grises para procesamiento
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()

        # 🔍 Mejora y detección de bordes
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(gray, 30, 200)

        # 🔲 Buscar contornos y filtrar los más grandes
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        for cnt in contours:
            # 🔷 Aproximar contorno a forma de placa (4 lados)
            approx = cv2.approxPolyDP(cnt, 0.018 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4:
                # 📌 Coordenadas del contorno detectado
                x, y, w, h = cv2.boundingRect(approx)

                # 🧠 Aplicar OCR sobre la región recortada
                plate_img = gray[y:y+h, x:x+w]
                ocr_results = self.reader.readtext(plate_img)

                for (_, text, confidence) in ocr_results:
                    clean_text = text.strip().upper()
                    if 4 <= len(clean_text) <= 8:
                        confidence_percent = confidence * 100
                        results.append((clean_text, f"{confidence_percent:.2f}%", (x, y, w, h)))

                        # 🎨 Color del rectángulo según confianza
                        if confidence_percent > 85:
                            color = (0, 255, 0)      # Verde
                        elif confidence_percent > 60:
                            color = (0, 255, 255)    # Amarillo
                        else:
                            color = (0, 0, 255)      # Rojo

                        # 🟥 Dibujar rectángulo y texto sobre frame_color
                        cv2.rectangle(frame_color, (x, y), (x + w, y + h), color, 2)
                        label = f"{clean_text} ({confidence_percent:.1f}%)"
                        cv2.putText(frame_color, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 📤 Devolver resultados y frame con anotaciones
        return results, frame_color
