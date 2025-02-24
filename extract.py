import cv2
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import numpy as np


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
def save_originalWatermark(binary_data, savepath):
    num_bits = len(binary_data)
    size = int(np.sqrt(num_bits))  
    pixel_values = np.array([255 if bit == '1' else 0 for bit in binary_data])
    pixel_values = pixel_values.reshape((size, size)).astype(np.uint8)

    cv2.imwrite(savepath,pixel_values)

def extract_rgb():
    watermarked_video = "watermarked/video_with_audio.avi"
    watermark_path = "extracted/original_watermark.png"
    # Read video frames
    frames = read_video_as_frames_rgb(watermarked_video)
    watermark_size = 150*150
    # Embed watermark bits across frames
    watermark_bits, watermark_completed = extract_watermark_from_frames(frames, watermark_size=watermark_size)

    if watermark_completed:
        print("Watermark bits have been fully embedded across frames.")
    else:
        print("Watermark embedding ended prematurely (not enough capacity).")

    save_originalWatermark(watermark_bits, watermark_path)
extract_rgb()