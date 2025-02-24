import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import subprocess
from moviepy.editor import VideoFileClip
import numpy as np
import os

def select_video():
    global video_path
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi")])
    video_label.config(text=f"Selected: {os.path.basename(video_path)}")

def select_watermark():
    global watermark_path
    watermark_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg")])
    watermark_label.config(text=f"Selected: {os.path.basename(watermark_path)}")

def select_output():
    global output_path
    output_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI Video", "*.avi")])
    output_label.config(text=f"Save to: {os.path.basename(output_path)}")

def watermark_bitstream(image_path, binarize=True, threshold=128):
    grayscale_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary_image = cv2.threshold(grayscale_image, threshold, 255, cv2.THRESH_BINARY) if binarize else (None, grayscale_image)
    bitstream = ''.join('1' if bit == 255 else '0' for bit in binary_image.flatten())
    return bitstream

def extract_audio(input_video, output_audio):
    subprocess.run(["ffmpeg", "-i", input_video, "-q:a", "0", "-map", "a", output_audio], check=True)

def merge_audio_video(watermarked_video, extracted_audio, output_video):
    subprocess.run(["ffmpeg", "-i", watermarked_video, "-i", extracted_audio, "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", output_video], check=True)

def read_video_as_frames_rgb(video_path):
    frames = []
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def write_frames_to_video_rgb(frames, output_path, fps):
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()

def embed_watermark_across_frames(frames, W):
    height, width, _ = frames[0].shape
    num_frames = len(frames)
    w_index = 0
    for row in range(height):
        for col in range(width):
            for frame_index in range(num_frames):
                for channel in range(3):
                    if w_index >= len(W):
                        return frames, True
                    pixel_binary = f'{frames[frame_index][row, col, channel]:08b}'
                    frames[frame_index][row, col, channel] = int(pixel_binary[:-1] + W[w_index], 2)
                    w_index += 1
    return frames, False

def process_watermarking():
    if not video_path or not watermark_path or not output_path:
        messagebox.showerror("Error", "Please select all required files.")
        return
    
    W = watermark_bitstream(watermark_path)
    extracted_audio = "temp_audio.aac"
    video_without_audio = "temp_video.avi"
    
    frames = read_video_as_frames_rgb(video_path)
    frames, _ = embed_watermark_across_frames(frames, W)
    write_frames_to_video_rgb(frames, video_without_audio, fps=16)
    extract_audio(video_path, extracted_audio)
    merge_audio_video(video_without_audio, extracted_audio, output_path)
    os.remove(video_without_audio)
    os.remove(extracted_audio)
    messagebox.showinfo("Success", "Watermarking completed!")

# GUI Setup
root = tk.Tk()
root.title("Video Watermarking Tool")
root.geometry("400x300")

video_label = tk.Label(root, text="No video selected")
video_label.pack()
video_button = tk.Button(root, text="Select Video", command=select_video)
video_button.pack()

watermark_label = tk.Label(root, text="No watermark selected")
watermark_label.pack()
watermark_button = tk.Button(root, text="Select Watermark", command=select_watermark)
watermark_button.pack()

output_label = tk.Label(root, text="No output selected")
output_label.pack()
output_button = tk.Button(root, text="Select Output", command=select_output)
output_button.pack()

process_button = tk.Button(root, text="Start Watermarking", command=process_watermarking)
process_button.pack()

root.mainloop()
