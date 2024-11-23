import cv2
from tkinter import filedialog
from moviepy.editor import VideoFileClip
def watermark_bitstream(image_path, binarize=True, threshold=128):
 
    # Load the image in grayscale
    grayscale_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Binarize the image if requested
    if binarize:
        _, binary_image = cv2.threshold(grayscale_image, threshold, 255, cv2.THRESH_BINARY)
    else:
        binary_image = grayscale_image

    # Flatten the binary image to a bitstream
    # Here, we convert to 0 and 1 based on the pixel value being 255 or 0.
    flat_binary_array = binary_image.flatten()
    bitstream = ''.join('1' if bit == 255 else '0' for bit in flat_binary_array)
    
    return bitstream

def add_audio_to_video(input_video_path, video_without_audio_path, output_with_audio_path):
    # Extract audio from the original video
    original_video = VideoFileClip(input_video_path)
    audio = original_video.audio
    
    # Load the video without audio
    video = VideoFileClip(video_without_audio_path)
    
    # Set the extracted audio to the new video and write the final video
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_with_audio_path, codec="libx264")

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
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()
def extract_watermark_from_frame(frame, watermark_size,w_index):
    height, width, _ = frame.shape
    for row in range(height):
        for col in range(width):
            for channel in range(3):  # Iterate over B, G, R channels
                if w_index >= watermark_size:
                    return w_index, pixel_lsb, True  # Return if watermark is fully extaracted
                pixel_binary = bin(frame[row, col, channel])
                pixel_lsb = pixel_binary[-1] 
                w_index += 1
    return w_index, pixel_lsb, False  # Continue if watermark is not fully embedded

# def processing_rgb():
#     inputvidpath = filedialog.askopenfilename()
#     W = watermark_bitstream("input/watermark.png")
#     video_without_audio_path = "watermarked/video_without_audio.mp4"
#     output_with_audio_path = "watermarked/watermarked_video_with_audio.mp4"
    
#     frames = read_video_as_frames_rgb(inputvidpath)
#     w_index = 0
#     watermark_completed = False
    
#     for img_index, frame in enumerate(frames):
#         w_index, watermark_completed = extract_watermark_from_frame(frame, W, w_index)
#         frames[img_index] = frame  # Update frame with modified pixels
#         if watermark_completed:
#             break  # Stop processing if watermark is fully embedded

#     print("Watermark bits have ended")
#     print("Watermarking has finished")

#     write_frames_to_video_rgb(frames, video_without_audio_path, fps=16)
#     add_audio_to_video(inputvidpath, video_without_audio_path, output_with_audio_path)

def read_bitcount_from_frame(frame):
    last_pixel = frame[-1, -1]
    r, g, b = last_pixel
    r_bits = bin(r)[-2:]
    g_bits = bin(g)[-3:]
    b_bits = bin(b)[-3:]
    print(last_pixel)
    bitcount_binary = r_bits + g_bits + b_bits
    bitcount = int(bitcount_binary, 2)
    return bitcount
def extract():
    inputvidpath = "watermarked/watermarked_video_with_audio.mp4"
    frames = read_video_as_frames_rgb(inputvidpath)
    size_of_watermark = 150*150
    w_index = 0
    watermark_bits = ""
    for img_index, frame in enumerate(frames):
        
        print("w_index", w_index)
        w_index, currentLsb, watermark_completed = extract_watermark_from_frame(frame, size_of_watermark,w_index)
        print("currentLsb", currentLsb)
        watermark_bits += str(currentLsb)
        if watermark_completed:
            print("Watermark bits have ended1")
            break  # Stop processing if watermark is fully embedded
        else:
            w_index += 1
    print("Watermark bits have ended")
    print("Watermark bits:", watermark_bits)
extract()