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
# def embed_watermark_in_frame(frame, W, w_index):
#     height, width, _ = frame.shape
#     for row in range(height):
#         for col in range(width):
#             for channel in range(3):  # Iterate over B, G, R channels
#                 if w_index >= len(W):
#                     return w_index, True  # Return if watermark is fully embedded
#                 currentW = W[w_index]
#                 pixel_binary = bin(frame[row, col, channel])
#                 pixel_binary_after = pixel_binary[:-1] + str(currentW)
#                 frame[row, col, channel] = int(pixel_binary_after, 2)
#                 w_index += 1
#     return w_index, False  # Continue if watermark is not fully embedded
def embed_watermark_across_frames(frames, W):
    """
    Embeds the watermark bitstream into the video frames in a column-first manner.
    
    Args:
        frames: List of video frames (each frame is a 3D NumPy array).
        W: Watermark bitstream (string of '0's and '1's).

    Returns:
        Modified frames with the watermark embedded.
    """
    height, width, _ = frames[0].shape  # Dimensions of the frames
    num_frames = len(frames)  # Total number of frames
    w_index = 0  # Index for the watermark bitstream
    
    # Iterate pixel by pixel across all frames
    for row in range(height):
        for col in range(width):
            for channel in range(3):  # Iterate over B, G, R channels
                for frame_index in range(num_frames):  # Loop through frames
                    if w_index >= len(W):
                        return frames, True  # Stop if the watermark is fully embedded
                    
                    currentW = W[w_index]  # Get current watermark bit
                    frame = frames[frame_index]  # Current frame
                    pixel_binary = bin(frame[row, col, channel])  # Convert pixel to binary
                    pixel_binary_after = pixel_binary[:-1] + str(currentW)  # Replace LSB
                    frame[row, col, channel] = int(pixel_binary_after, 2)  # Convert back
                    w_index += 1  # Move to the next bit

    return frames, False  # Return frames if watermark embedding isn't complete
def processing_rgb():
    inputvidpath = "input/video.mp4"
    W = watermark_bitstream("input/watermark.png")
    video_without_audio_path = "watermarked/video_without_audio.mp4"
    output_with_audio_path = "watermarked/watermarked_video_with_audio.mp4"
    
    # Read video frames
    frames = read_video_as_frames_rgb(inputvidpath)
    
    # Embed watermark bits across frames
    frames, watermark_completed = embed_watermark_across_frames(frames, W)

    if watermark_completed:
        print("Watermark bits have been fully embedded across frames.")
    else:
        print("Watermark embedding ended prematurely (not enough capacity).")

    # Write the modified frames back into a video
    write_frames_to_video_rgb(frames, video_without_audio_path, fps=16)
    
    # Reattach original audio to the watermarked video
    add_audio_to_video(inputvidpath, video_without_audio_path, output_with_audio_path)


processing_rgb()
