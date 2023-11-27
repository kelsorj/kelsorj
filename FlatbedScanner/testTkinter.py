from tkinter import Tk, Button, Canvas
from PIL import Image, ImageTk
import cv2
import numpy as np


def on_button_click(option):
    print(f"Button {option} clicked.")


def display_window_with_buttons(image):
    root = Tk()
    root.title("Barcode Scanning Results")

    cv2_im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im_rgb)

    im = ImageTk.PhotoImage(image=pil_im)

    print(type(im), im)  # Debug print

    canvas = Canvas(root, height=im.height(), width=im.width())
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=im)
    canvas.image = im

    Button(root, text="Re-scan", command=lambda: on_button_click("Re-scan")).pack(side="left")
    Button(root, text="Save Results", command=lambda: on_button_click("Save")).pack(side="left")
    Button(root, text="Exit", command=lambda: on_button_click("Exit")).pack(side="left")

    root.mainloop()


# Dummy image for testing
dummy_image = np.zeros((400, 400, 3), dtype=np.uint8)
cv2.rectangle(dummy_image, (50, 50), (350, 350), (255, 0, 0), 5)

display_window_with_buttons(dummy_image)
