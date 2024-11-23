import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import numpy as np
import cv2




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

        label = tk.Label(self.root, text ="Results", font =("Verdana", 16))
        label.grid(row = 0, column = 2, padx = 10, pady = 10)


        saveBtn = tk.Button(self.root,text="Save Dual Imgs", command= self.saveResults)
        saveBtn.grid(row=0,column=1)
        
        startBtn = tk.Button(self.root,text="Start Watermarking", command= self.startWatermarking)
        startBtn.grid(row=0,column=0)
        
        button1 = tk.Button(self.root, text ="Select cover image",
                            command = self.uploadCoverImages)
        button1.grid(row = 2, column = 0, padx = 10, pady = 10)

        self.coverLabel = tk.Label(self.root)
        self.coverLabel.grid(row=1,column=0)
        
        button2 = tk.Button(self.root, text ="Select watermark",
                            command = self.uploadWatermark)
        button2.grid(row = 2, column = 1, padx = 10, pady = 10)

        self.watermarkLabel = tk.Label(self.root)
        self.watermarkLabel.grid(row=1,column=1)

        self.cd1Label = tk.Label(self.root)
        self.cd1Label.grid(row=1,column=2)


        self.coverImage = ""
        self.watermarkImage = ""

        self.cd1Np = None
        self.cap = cv2.VideoCapture()
        self.frameCounter = 0
        self.root.mainloop()

    def coverToBarcode(self):
        pass
    def nextFrame(self):
        if self.frameCounter == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
            return
                    #loop
            #self.frameCounter = 0
            #self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)        
        _, frame = self.cap.read()
        self.frameCounter += 1
        frame = cv2.resize(frame, (224, 224))
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        pic = ImageTk.PhotoImage(img)
        self.coverLabel.config(image=pic)
        self.coverLabel.image = pic
        self.coverLabel.after(100,  self.nextFrame)

    def uploadCoverImages(self):
        fileTypes = [("Image files", "*.mp4;*.jpg;*.jpeg")]
        path = filedialog.askopenfilename(filetypes=fileTypes)
        self.coverimg = path 
        self.cap = cv2.VideoCapture(path)

        # if file is selected
        if len(path):
            self.nextFrame()
        else:
            print("No file is Choosen !! Please choose a file.")

    def uploadWatermark(self):
        fileTypes = [("Image files", "*.png;*.jpg;*.jpeg")]
        path = filedialog.askopenfilename(filetypes=fileTypes)
        self.watermarkImage = path
        # if file is selected
        if len(path):
            img = Image.open(path)
            img = img.resize((200, 200))
            pic = ImageTk.PhotoImage(img)
            self.watermarkLabel.config(image=pic)
            self.watermarkLabel.image = pic
        else:
            print("No file is Choosen !! Please choose a file.")

    def saveResults(self):
        cv2.imwrite("work/watermarked images/CD1.png", self.cd1Np)

    def startWatermarking(self):
        inputimg = self.coverimg
        watermarkImg = self.watermarkImage
        image = cv2.imread(inputimg, cv2.IMREAD_GRAYSCALE)
        height, width = image.shape
        CD1 = image.copy()
        W = watermark_bitstream(watermarkImg)
        w_index = 0
        bits_per_block = 8
        # 15 * 15 pixels = 5 * 5 non overlapping blocks
        # 8 bits per block => 25 * 8 = 200 bits from watermark
        # some of the watermark bits won't be available
        # and extracted data will not fit into a square
        # prob sol: share/have fixed resultion of the watermark
        # and in extraction, get all the bits then fill the missing
        # bits with 0 till it fits size
        new_CD1 = np.zeros((height, width), dtype=np.uint8)
        for y in range(0, height ,3):
            for x in range(0, width ,3):
                if w_index + bits_per_block > len(W):
                    # If you need to loop the watermark, uncomment the next line
                    # w_index = 0
                    print("Watermark bits has ended")
                    break 
                cd1block = CD1[y: y+3, x:x+3]
                currentW = W[w_index:w_index + bits_per_block] 
                watermark_bits_int = [int(bit) for bit in currentW]
                cd1block_binary = to_binary(cd1block)
                cd1after = embed_bits_in_border_lsb(watermark_bits_int, cd1block_binary)
                decimal_cd1 = to_decimal(cd1after)
                new_CD1[y: y+3,x: x+3] = decimal_cd1
                w_index += bits_per_block
        
        self.cd1Np = new_CD1
        tkCd1 = ImageTk.PhotoImage(image=Image.fromarray(new_CD1))
        self.cd1Label.config(image=tkCd1)
        self.cd1Label.image = tkCd1



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

def to_binary(matrix):
    # Convert each pixel to binary, removing the '0b' prefix and padding to 8 bits
    binary_matrix = np.vectorize(lambda x: format(x, '08b'))(matrix)
    return binary_matrix
def to_decimal(matrix):
    # Vectorize allows the function to be applied element-wise on the array
    decimal_array = np.vectorize(lambda b: int(b, 2))(matrix)
    return decimal_array

def embed_bits_in_border_lsb(bit_array, binary_pixel_array):
    # Indices of the border elements
    updated_array = binary_pixel_array.copy()
    border_indices = [(0, 0), (0, 1), (0, 2),
                      (1, 2), 
                      (2, 2), (2, 1), (2, 0),
                      (1, 0)]
    # Embed the bits into the border pixels
    for bit, (row, col) in zip(bit_array, border_indices):
        # Slice off the last bit and append the new bit from ew
        updated_array[row, col] = updated_array[row, col][:-1] + str(bit)
    
    return updated_array


# Driver Code

WatermarkingPage()