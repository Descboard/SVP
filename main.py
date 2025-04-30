import cv2
import csv
import os
import time
from datetime import datetime
import concurrent.futures  # Para multihilo

from app.camera.camera import Camera
from app.recognition.plate_detector import PlateDetector
from app.config import settings

# Inicialización de cámara y detector
print(settings.CAMERA_INDEX)
cam = Camera(settings.CAMERA_INDEX, settings.FRAME_WIDTH, settings.FRAME_HEIGHT)
detector = PlateDetector()  # Este ya incluye verificación de GPU
cam.start()
print("Procesando... Presiona 'q' para salir.")

# Función para registrar la placa en un archivo CSV
def registrar_placa(placa_texto, confianza):
    archivo = "registros.csv"
    encabezado = ['Fecha', 'Hora', 'Placa', 'Certeza']
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    # Crear el archivo si no existe
    archivo_existe = os.path.exists(archivo)
    with open(archivo, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not archivo_existe:
            writer.writerow(encabezado)  # Escribir encabezado solo si es un archivo nuevo
        confianza_limpia = confianza.replace('porcentaje de certeza: ', '').replace('%', '')
        writer.writerow([fecha, hora, placa_texto, confianza_limpia])

# Función que procesa el frame, detecta placas y registra resultados
def procesar_frame(frame):
    plates, frame_with_rectangles = detector.detect_plate(frame)
    if plates:
        for plate_text, confidence_str in plates:
            print(f"PPU detectada: {plate_text} ({confidence_str})")
            registrar_placa(plate_text, confidence_str)
    return frame_with_rectangles

# Ejecutamos el bucle principal con procesamiento multihilo
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    try:
        while True:
            frame = cam.get_frame()
            if frame is not None:
                # Enviar frame a un hilo para procesamiento
                future = executor.submit(procesar_frame, frame)
                # Obtener frame procesado con rectángulos (bloquea hasta que esté listo)
                frame_with_rectangles = future.result()

                # Mostrar la imagen con detecciones
                cv2.imshow('Detección de Placas', frame_with_rectangles)

                # Salir con 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Pequeña pausa para evitar sobrecarga
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
    finally:
        cam.stop()
        cv2.destroyAllWindows()
        print("Finalizado.")
