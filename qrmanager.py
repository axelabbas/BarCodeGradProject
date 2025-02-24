import cv2
import numpy as np
import pyqrcode
from PIL import Image
from pyzbar.pyzbar import decode

class qrcoder:
    
    @staticmethod
    def image_to_qr(image_path, output_path):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        binary_string = "".join("1" if pixel > 127 else "0" for pixel in image.flatten())
        qr = pyqrcode.create(binary_string)
        qr.png(output_path, scale=2)
    
    @staticmethod
    def decode_qr_from_image(image_path):
        image = Image.open(image_path).convert("RGB")
        image_np = np.array(image)
        decoded_objects = decode(image_np)
        qr_data = []
        for obj in decoded_objects:
            qr_data.append(obj.data.decode('utf-8'))
        
        return qr_data

if __name__ == "__main__":
    qrcoder.image_to_qr("input/smallwm.png", "input/qr.png")
    print(qrcoder.decode_qr_from_image("extracted/original_watermark.png"))

