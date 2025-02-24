import cv2
import subprocess

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

def extract_audio(input_video, output_audio):
    subprocess.run([
        "ffmpeg", "-i", input_video, "-q:a", "0", "-map", "a", output_audio
    ], check=True)
def merge_audio_video(watermarked_video, extracted_audio, output_video):
    subprocess.run([
        "ffmpeg", "-i", watermarked_video, "-i", extracted_audio, 
        "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", output_video
    ], check=True)

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

def embed_watermark_across_frames(frames, W):
    height, width, _ = frames[0].shape  # Dimensions of the frames
    num_frames = len(frames)  # Total number of frames
    w_index = 0  # Index for the watermark bitstream
    
    # Iterate pixel by pixel across all frames
    for row in range(height):
        for col in range(width):
            for frame_index in range(num_frames):  # Loop through frames
                for channel in range(3):  # Iterate over B, G, R channels
                    if w_index >= len(W):
                        return frames, True  # Stop if the watermark is fully embedded
                    
                    currentW = W[w_index]  # Get current watermark bit
                    frame = frames[frame_index]  # Current frame
                    pixel_binary = f'{frame[row, col, channel]:08b}'
                    pixel_binary_after = pixel_binary[:-1] + currentW
                    frame[row, col, channel] = int(pixel_binary_after, 2)
                    print(
                        f"Embedding bit: {currentW} into pixel (Row: {row}, Col: {col}, Frame: {frame_index}, Channel: {channel})\n"
                        f"Original Binary: {pixel_binary}, Modified Binary: {pixel_binary_after}"
                    )

                    w_index += 1  # Move to the next bit

    return frames, False  # Return frames if watermark embedding isn't complete
def processing_rgb():
    W = watermark_bitstream("input/watermark.png") 
    inputvidpath = "input/video.mp4"

    extracted_audio = "watermarked/extracted_audio.aac"

    video_without_audio_path = "watermarked/video_without_audio.avi"
    video_with_audio_path = "watermarked/video_with_audio.avi"
    
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
    # add_audio_to_video(inputvidpath, video_without_audio_path, output_with_audio_path)
    extract_audio(inputvidpath, extracted_audio)
    merge_audio_video(video_without_audio_path, extracted_audio, video_with_audio_path)




processing_rgb()
