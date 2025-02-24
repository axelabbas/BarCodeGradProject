import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import cv2
import subprocess

from qrmanager import qrcoder

class WatermarkingPage:
    
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry("1000x500")
        self.root.columnconfigure(0,weight=1)
        self.root.columnconfigure(1,weight=1)
        self.root.columnconfigure(2,weight=1)
        self.root.rowconfigure(0,weight=1)
        self.root.rowconfigure(1,weight=1)
        self.root.rowconfigure(2,weight=1)
        self.root.config(bg="#cfccc6")

        resultsLabel = tk.Label(self.root, text ="Results", font =("Verdana", 16))
        resultsLabel.grid(row = 0, column = 2, padx = 10, pady = 10)


        
        
        startBtn = tk.Button(self.root,text="Start Watermarking", command= self.startWatermarking)
        startBtn.grid(row=0,column=0)
        
        selectCoverBtn = tk.Button(self.root, text ="Select cover image",
                            command = self.uploadCover)
        selectCoverBtn.grid(row = 2, column = 0, padx = 10, pady = 10)

        self.videoLabel = tk.Label(self.root)
        self.videoLabel.grid(row=1,column=0)
        
        selectWatermarkBtn = tk.Button(self.root, text ="Select watermark",
                            command = self.uploadWatermark)
        selectWatermarkBtn.grid(row = 2, column = 1, padx = 10, pady = 10)

        self.watermarkImgLabel = tk.Label(self.root)
        self.watermarkImgLabel.grid(row=0,column=1)
        self.qrcodeLabel = tk.Label(self.root)
        self.qrcodeLabel.grid(row=1,column=1)

        self.watermarkedVideoLabel = tk.Label(self.root)
        self.watermarkedVideoLabel.grid(row=1,column=2)

    

        self.watermarkImagePath = ""
        self.qrcodePath = "input/qr.png"

        self.watermarked_video = None
        self.extractedAudioPath = "watermarked/extracted_audio.aac"
        self.video_without_audio_path = "watermarked/video_without_audio.avi"
        self.video_with_audio_path = "watermarked/video_with_audio.avi"
        self.root.mainloop()
    
    def uploadCover(self):
        fileTypes = [("Video files", "*.mp4;*.avi;")]
        path = filedialog.askopenfilename(filetypes=fileTypes)
        self.videoPath = path
        # if file is selected
        if len(path):
            vid = cv2.VideoCapture(path) 
            _, frame = vid.read() 
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 
            captured_image = Image.fromarray(opencv_image) 
            photo_image = ImageTk.PhotoImage(image=captured_image.resize((200,200))) 
            self.videoLabel.photo_image = photo_image 
            self.videoLabel.configure(image=photo_image) 
        else:
            print("No file is Choosen !! Please choose a file.")

    def uploadWatermark(self):
        fileTypes = [("Image files", "*.png;*.jpg;*.jpeg")]
        path = filedialog.askopenfilename(filetypes=fileTypes)
        self.watermarkImagePath = path
        qrcoder.image_to_qr(self.watermarkImagePath, self.qrcodePath)
        img = Image.open(self.qrcodePath)
        img = img.resize((200, 200))
        pic = ImageTk.PhotoImage(img)
        self.qrcodeLabel.config(image=pic)
        self.qrcodeLabel.image = pic
        # if file is selected
        if len(path):
            img = Image.open(path)
            img = img.resize((200, 200))
            pic = ImageTk.PhotoImage(img)
            self.watermarkImgLabel.config(image=pic)
            self.watermarkImgLabel.image = pic
        else:
            print("No file is Choosen !! Please choose a file.")

    def saveResults(self):
        cv2.imwrite("watermarked/watermarked.avi", self.watermarked_video)
    
    def startWatermarking(self):
        W =  watermark_bitstream(self.qrcodePath) 
        
        
        # Read video frames
        frames = read_video_as_frames_rgb(self.videoPath)
        
        # Embed watermark bits across frames
        frames, watermark_completed = embed_watermark_across_frames(frames, W)

        if watermark_completed:
            print("Watermark bits have been fully embedded across frames.")
        else:
            print("Watermark embedding ended prematurely (not enough capacity).")

        # Write the modified frames back into a video
        write_frames_to_video_rgb(frames, self.video_without_audio_path, fps=16)
        
        # Reattach original audio to the watermarked video
        # add_audio_to_video(inputvidpath, video_without_audio_path, output_with_audio_path)
        extract_audio(self.videoPath, self.extractedAudioPath)
        vid = cv2.VideoCapture(self.video_without_audio_path) 
        _, frame = vid.read() 
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 
        captured_image = Image.fromarray(opencv_image) 
        photo_image = ImageTk.PhotoImage(image=captured_image.resize((200,200))) 
        self.watermarkedVideoLabel.photo_image = photo_image 
        self.watermarkedVideoLabel.configure(image=photo_image) 
        merge_audio_video(self.video_without_audio_path, self.extractedAudioPath, self.video_with_audio_path)


def extract_audio(input_video, output_audio):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_video, "-q:a", "0", "-map", "a", output_audio
    ], check=True)

def merge_audio_video(watermarked_video, extracted_audio, output_video):
    subprocess.run([
        "ffmpeg", "-y", "-i", watermarked_video, "-i", extracted_audio, 
        "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", output_video
    ], check=True)
def write_frames_to_video_rgb(frames, output_path, fps):
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()
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
                   

                    w_index += 1  # Move to the next bit

    return frames, False  # Return frames if watermark embedding isn't complete
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

# Driver Code

WatermarkingPage()