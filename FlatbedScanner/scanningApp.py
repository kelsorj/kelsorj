import sys
import string
import traceback
import cv2
import twain
from pylibdmtx.pylibdmtx import decode  # dotmatrix barcode decoding
import concurrent.futures               # run tasks in parallel
import numpy as np
from datetime import datetime
from PIL import Image, ImageFilter, ImageEnhance, ImageTk, ImageOps
import csv
from tkinter import Tk, Button, Canvas, Label
import tkinter as tk
from tkinter import ttk


def improve_contrast(image):
    enhancer = ImageEnhance.Brightness(image)
    brighter_image = enhancer.enhance(1.2)
    enhancer = ImageEnhance.Contrast(brighter_image)
    return enhancer.enhance(1.3)  # You can change the level of contrast


def remove_noise(image):
    return image.filter(
        ImageFilter.MedianFilter(size=5)
    )  # Increased the filter size to 5


def row_number_to_letter(row_number):
    letters = string.ascii_uppercase  # This contains 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return letters[row_number]


def decode_barcode(y1, y2, x1, x2, image, row, col):
    # Crop and preprocess the cell image
    crop_image = image[y1:y2, x1:x2]
    # Crop away 10 pixels from all four sides
    new_y1 = y1 + 20
    new_y2 = y2 - 20
    new_x1 = x1 + 20
    new_x2 = x2 - 20
    # Perform the new cropping
    new_crop_image = image[new_y1:new_y2, new_x1:new_x2]
    crop_image = np.float32(new_crop_image)
    # Apply linear contrast transformation: new_image = alpha*image + beta
    alpha = 1.6  # Contrast control (1.0-3.0)
    beta = 50  # Brightness control (0-100)
    crop_image = cv2.convertScaleAbs(crop_image, alpha=alpha, beta=beta)
    # Save the processed image with row and column information
    filename = f"image_row_{row}_col_{col}.png"
    cv2.imwrite(filename, crop_image)
    # Decode the barcode
    decoded_objects = decode(crop_image)
    print(str(decoded_objects))
    return row, col, decoded_objects


# Function for 96 Barcodes
def process_96_barcodes():
    print("Processing 96 barcodes")
    # Your logic here for 96 barcodes
    # ...

# Function for 24 Barcodes
def process_24_barcodes():
    print("Processing 24 barcodes")
    # Your logic here for 24 barcodes
    # ...

# Create the Tkinter window
window = tk.Tk()
window.title("Choose Barcode Grid")

# Create buttons for the two cases
button1 = ttk.Button(window, text="Process 96 Barcodes", command=process_96_barcodes)
button2 = ttk.Button(window, text="Process 24 Barcodes", command=process_24_barcodes)

# Place buttons on the grid
button1.grid(row=0, column=0, padx=10, pady=10)
button2.grid(row=0, column=1, padx=10, pady=10)

# Run the Tkinter event loop
window.mainloop()