import cv2

def crop_plate_region(image):
    height, width = image.shape[:2]
    return image[int(height*0.4):int(height*0.6), int(width*0.3):int(width*0.7)]
