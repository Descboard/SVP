import cv2
from app.camera.camera import Camera
from app.recognition.plate_recognition import PlateRecognizer

def main():
    camera = Camera()
    recognizer = PlateRecognizer()
    try:
        camera.start()
        while True:
            frame = camera.get_frame()
            plates = recognizer.recognize_plate(frame)
            for plate, prob in plates:
                print(f"Placa detectada: {plate} (Confianza: {prob:.2f})")
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
