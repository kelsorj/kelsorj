import twain
import sys
from tkinter import *
from tkinter import messagebox
import traceback
import cv2
from pylibdmtx.pylibdmtx import decode

root = Tk()
root.title('scan.py')

if len(sys.argv) != 2:
    messagebox.showerror("Error", "Usage: python scan.py <filename>")
    exit(1)

outpath = sys.argv[1]

def scan():
    try:
        device_name = "PaperStream IP fi-65F"
        device_name_bytes = device_name.encode('utf-8')
        result = twain.acquire(outpath,
                               dpi=600,
                               ds_name=device_name_bytes,
                               frame=(0, 0, 1, 1),
                               pixel_type='color',
                               parent_window=root,
                               )

        # Read the image with OpenCV
        image = cv2.imread(outpath)
        #crop_image = cv2.imread(outpath)
        #crop_image = cv2.imread('barcode_qrcode.jpg')

        # Crop the image
        # image[y1:y2, x1:x2]
        crop_image = image[250:427, 180:352]
        gray = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
        #crop_image = cv2.threshold(gray, 0, 200, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        crop_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

        # Show the cropped image to make sure it's correct
        cv2.imshow('Cropped Image', crop_image)
        cv2.waitKey(0)  # waits until a key is pressed
        cv2.destroyAllWindows()

        # Decode the 2D barcode with pyzbar on the cropped image
        decoded_objects = decode(crop_image)
        print(decoded_objects)

    except:
        messagebox.showerror("Error", traceback.format_exc())
        sys.exit(1)
    else:
        sys.exit(0 if result else 1)

root.after(1, scan)
root.mainloop()