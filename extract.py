import cv2
import numpy as np
from qrmanager import qrcoder

def read_video_as_frames_rgb(video_path):
    frames = []
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)  # Keep original BGR format
    cap.release()
    return frames

def write_frames_to_video_rgb(frames, output_path, fps):
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()
def extract_watermark_from_frames(frames, watermark_size):
    height, width, _ = frames[0].shape
    w_index = 0
    lsb = ""
    for row in range(height):
        for col in range(width):
            for frame_index in range(len(frames)):
                for channel in range(3):  # Iterate over B, G, R channels
                    frame = frames[frame_index]
                    if w_index >= watermark_size:
                        return lsb, True  # Return if watermark is fully extaracted
                    pixel_binary = f'{frame[row, col, channel]:08b}'
                    pixel_lsb = pixel_binary[-1]

                    lsb += str(pixel_lsb)
                    w_index += 1
    return lsb, False  # Continue if watermark is not fully embedded
def saveBinaryStrToImg(binary_data, savepath):
    num_bits = len(binary_data)
    size = int(np.sqrt(num_bits))
    print(num_bits)
    print(size)
    bits = []
    for bit in binary_data:
        bits.append(255 if bit == '1' else 0)

    pixel_values = np.array(bits)
    pixel_values = pixel_values.reshape((size, size)).astype(np.uint8)

    cv2.imwrite(savepath,pixel_values)

def extract_rgb():
    watermarked_video = "watermarked/video_with_audio.avi"
    qr_path = "extracted/original_qr.png"
    # Read video frames
    frames = read_video_as_frames_rgb(watermarked_video)
    qrcode_size = 338*338
    # Embed watermark bits across frames
    qrcode_bits, qr_completed = extract_watermark_from_frames(frames, watermark_size=qrcode_size)

    if qr_completed:
        print("bits have been fully extracted")
    else:
        print("Watermark embedding ended prematurely (not enough capacity).")

    saveBinaryStrToImg(qrcode_bits, qr_path)
    watermark_string = qrcoder.decode_qr_from_image(qr_path)[0]
    saveBinaryStrToImg(watermark_string, "extracted/original_watermark.png")


extract_rgb()