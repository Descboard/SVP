import cv2
import csv
import os
import time
from datetime import datetime, timedelta
import concurrent.futures  # Para multihilo

from app.camera.camera import Camera
from app.recognition.plate_detector import PlateDetector
from app.config import settings

# Inicialización
print(f"🟢 Cámara activa (índice: {settings.CAMERA_INDEX})")
cam = Camera(settings.CAMERA_INDEX, settings.FRAME_WIDTH, settings.FRAME_HEIGHT)
detector = PlateDetector()
cam.start()
print("🎥 Procesando... Presiona 'q' para salir.")

# Diccionario para evitar registros duplicados recientes
placas_registradas = {}

# Tiempo mínimo entre registros de la misma placa (en segundos)
TIEMPO_ANTIREP = 1

def registrar_placa(placa_texto, confianza):
    ahora = datetime.now()

    # Control de duplicados recientes
    if placa_texto in placas_registradas:
        ultima_vez = placas_registradas[placa_texto]
        if (ahora - ultima_vez) < timedelta(seconds=TIEMPO_ANTIREP):
            print(f"⚠️ Patente {placa_texto} ignorada por duplicación reciente.")
            return  # Saltar registro duplicado

    placas_registradas[placa_texto] = ahora  # Actualizar timestamp

    archivo = "registros.csv"
    encabezado = ['Fecha', 'Hora', 'Placa', 'Certeza']
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
        print(f"✅ Registro guardado: {placa_texto} ({confianza_limpia}%)")

# Función que procesa el frame, detecta placas y registra resultados
def procesar_frame(frame):
    plates, frame_with_rectangles = detector.detect_plate(frame)
    if plates:
        for plate_text, confidence_str, _ in plates:  # No usamos las coords aquí
            print(f"PPU detectada: {plate_text} ({confidence_str})")
            registrar_placa(plate_text, confidence_str)
    return frame_with_rectangles

# Loop principal
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    try:
        while True:
            frame = cam.get_frame()
            if frame is not None:
                # Enviar frame a un hilo para procesamiento
                future = executor.submit(procesar_frame, frame)
                # Obtener frame procesado con rectángulos (bloquea hasta que esté listo)
                frame_with_rectangles = future.result()

                # Mostrar frame en vivo con las detecciones
                cv2.imshow('🚗 Detección de Patentes - Presiona "q" para salir', frame_with_rectangles)

                # Salir con 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
    finally:
        cam.stop()
        cv2.destroyAllWindows()
        print("Finalizado.")
