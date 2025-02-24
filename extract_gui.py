import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import cv2
import numpy as np
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
        resultsLabel.grid(row = 0, column = 1, padx = 10, pady = 10)

        startBtn = tk.Button(self.root,text="Start Extraction", command= self.startExtraction)
        startBtn.grid(row=0,column=0)
        
        selectCoverBtn = tk.Button(self.root, text ="Select Watermarked Video",
                            command = self.uploadCover)
        selectCoverBtn.grid(row = 2, column = 0, padx = 10, pady = 10)

        self.videoLabel = tk.Label(self.root)
        self.videoLabel.grid(row=1,column=0)

        self.watermarkImgLabel = tk.Label(self.root)
        self.watermarkImgLabel.grid(row=1,column=1)

        self.qrcodeLabel = tk.Label(self.root)
        self.qrcodeLabel.grid(row=1,column=2)

        self.watermarkImagePath = ""

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
    
    def startExtraction(self):
        watermarked_video = "watermarked/video_with_audio.avi"
        qr_path = "extracted/original_qr.png"
        watermark_path = "extracted/original_watermark.png"
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
        saveBinaryStrToImg(watermark_string, watermark_path)

        img = Image.open(watermark_path)
        img = img.resize((200, 200))
        pic = ImageTk.PhotoImage(img)
        self.qrcodeLabel.config(image=pic)
        self.qrcodeLabel.image = pic

        img = Image.open(qr_path)
        img = img.resize((200, 200))
        pic = ImageTk.PhotoImage(img)
        self.watermarkImgLabel.config(image=pic)
        self.watermarkImgLabel.image = pic 



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
    bits = []
    for bit in binary_data:
        bits.append(255 if bit == '1' else 0)

    pixel_values = np.array(bits)
    pixel_values = pixel_values.reshape((size, size)).astype(np.uint8)

    cv2.imwrite(savepath,pixel_values)


# Driver Code

WatermarkingPage()