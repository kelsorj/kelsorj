import sys
import string
import cv2
import twain
from pylibdmtx.pylibdmtx import decode  # dotmatrix barcode decoding
import concurrent.futures  # run tasks in parallel
import numpy as np
from datetime import datetime
from PIL import Image, ImageFilter, ImageEnhance, ImageTk, ImageOps
import csv
from tkinter import Tk, Button, Canvas, Label


def improve_contrast(image):
    enhancer = ImageEnhance.Brightness(image)
    brighter_image = enhancer.enhance(1.4)
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
    #print("y " + str(y1)+" "+str(y2)+" x "+str(x1)+" "+str(x2))
    # Crop away 10 pixels from all four sides
    #new_y1 = y1 + 20
    #new_y2 = y2 - 20
    #new_x1 = x1 + 20
    #new_x2 = x2 - 20
    new_y1 = y1 + 20
    new_y2 = y2 - 20
    new_x1 = x1 + 20
    new_x2 = x2 - 20
    # Perform the new cropping
    new_crop_image = image[new_y1:new_y2, new_x1:new_x2]
    print("cropped y " + str(y1)+" "+str(y2)+" x "+str(x1)+" "+str(x2))
    crop_image = np.float32(new_crop_image)
    # Apply linear contrast transformation: new_image = alpha*image + beta
    alpha = 1.3     # Contrast control (1.0-3.0)
    beta = 40       # Brightness control (0-100)
    crop_image = cv2.convertScaleAbs(crop_image, alpha=alpha, beta=beta)
    # Save the processed image with row and column information
    filename = f"image_row_{row}_col_{col}.png"
    cv2.imwrite(filename, crop_image)
    # Decode the barcode
    decoded_objects = decode(crop_image)
    # print(str(decoded_objects))
    return row, col, decoded_objects


class BarcodeScanner:
    def __init__(self):
        self.root = Tk()
        self.outpath = "image.bmp"


    def display_window_with_buttons(self, all_decoded_objects, image):
        self.root.title("Barcode Scanning Results")

        # Convert OpenCV image format to PIL image
        cv2_im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im_rgb)
        # print(type(pil_im), pil_im)  # Debug print
        # Convert PIL image to ImageTk format
        im = ImageTk.PhotoImage(image=pil_im)
        # print(type(im), im)  # Debug print
        # Create Canvas and add image to it
        canvas = Canvas(self.root, height=im.height(), width=im.width())
        canvas.pack()
        canvas.create_image(0, 0, anchor="nw", image=im)

        # Keep a reference to avoid garbage collection
        canvas.image = im

        # Add Buttons below the image
        # Button(
        #    self.root, text="Re-scan", command=lambda: self.on_button_click(1, None)
        # ).pack(side="left")
        Button(
            self.root,
            text="Save Results to CSV",
            command=lambda: self.on_button_click(2, all_decoded_objects),
        ).pack(side="left")
        Button(
            self.root, text="Exit", command=lambda: self.on_button_click(3, None)
        ).pack(side="left")

        # Start the Tkinter main loop
        self.root.mainloop()


    def rescan(self):
        print("Re-scanning...")
        self.root = Tk()
        self.scan()


    def save_results_to_csv(self, all_decoded_objects):
        with open("results.csv", "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Column", "Row", "Barcode"])
            for (row, col), decoded_objects in all_decoded_objects.items():
                for decoded in decoded_objects:
                    csvwriter.writerow([col, row, decoded.data.decode("utf-8")])


    def on_button_click(self, button_id, userdata):
        if button_id == 1:
            print("Re-scanning...")
            self.rescan()
        elif button_id == 2:
            print("Saving results...")
            self.save_results_to_csv(userdata)
        elif button_id == 3:
            print("Exiting...")
            self.root.destroy()
            sys.exit(0)


    def scan(self):
        device_name = "PaperStream IP fi-65F"
        device_name_bytes = device_name.encode("utf-8")
        twain.IMAGE_ORIENT_LEFT = 1
        outpath = "image.bmp"
        result = twain.acquire(
            outpath,
            dpi=600,
            ds_name=device_name_bytes,
            frame=(0, 0, 4, 5.5),
            pixel_type="color",
        )

        # Read the image with PIL
        image = Image.open(outpath)
        # improved_contrast = improve_contrast(image)
        # removed_noise = remove_noise(improved_contrast)
        # Recast so opencv tools will work on image
        image = np.array(image)
        # TODO check to make sure the "right" barcode can be read where it's expected
        #       if it can't then start the process of rotating the image till it can
        test_orientation = image[980:1230, 20:260]
        # Decode the barcode
        decoded_objects = decode(test_orientation)
        # print("decoded orientation = " + str(decoded_objects))
        # if it didn't find barcode then time to rotate the image
        if len(decoded_objects) < 1:
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            cv2.imwrite("image_rotate.bmp", image)
        test_orientation = image[980:1230, 20:260]
        # cv2.imshow('Cropped Image', test_orientation)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        decoded_objects = decode(test_orientation)
        # print("decoded orientation = " + str(decoded_objects))
        if len(decoded_objects) < 1:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            cv2.imwrite("image_rotate_180.bmp", image)
        test_orientation = image[980:1230, 20:260]
        # cv2.imshow('Cropped Image', test_orientation)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        decoded_objects = decode(test_orientation)
        # print("decoded orientation = " + str(decoded_objects))
        if len(decoded_objects) < 1:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            cv2.imwrite("image_rotate_270.bmp", image)
        test_orientation = image[980:1230, 20:260]
        decoded_objects = decode(test_orientation)
        print("decoded orientation = " + str(decoded_objects))
        # Get the dimensions of the image
        # (height, width) = image.shape[:2]
        # Check if the image is portrait or landscape
        # if height > width:
        # Rotate image to landscape
        # image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # cv2.imwrite("image_rotate.bmp", image)

        # Define the grid dimensions
        rows = 4
        cols = 6

        # Define the dimensions of each barcode box
        box_height = 175
        box_width = 175

        # Define gaps between the boxes
        vertical_gap = 250      #430 too wide 333 = 430-87
        horizontal_gap = 250

        # Initialize list to store decoded objects
        all_decoded_objects = {}
        detected_boxes = []

        # Start coordinates for the first box
        # for 96 well image center of a1 bc = x-596 y-415
        #start_x = 505
        #start_y = 335
        # for 24 well image center of a1 bc = x-709 y-527
        start_x = 620
        start_y = 440

        # Create a ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(rows):
                for j in reversed(range(cols)):  # reverse the order here
                    y1 = start_y + (i * (box_height + vertical_gap))
                    y2 = y1 + box_height
                    x1 = start_x + (j * (box_width + horizontal_gap))
                    x2 = x1 + box_width
                    # Submit the function for execution
                    future = executor.submit(
                        decode_barcode, y1, y2, x1, x2, image, i, j
                    )
                    futures.append(future)

            # Collect results
            for future in concurrent.futures.as_completed(futures):
                row, col, decoded_objects = future.result()
                all_decoded_objects[(row, col)] = decoded_objects

                if decoded_objects:
                    detected_boxes.append(
                        (row, col)
                    )  # Appending the row and column indices where barcode is detected

        #print(all_decoded_objects)

        # Initialize a flag to True. This flag will be set to False if any barcode is missing.
        all_barcode_present = True

        # Check for rows and columns without detected barcodes
        for i in range(rows):
            for j in range(cols):
                row_letter = row_number_to_letter(i)
                col_number = cols - j  # Shift column numbering
                # Check if the key is in the dictionary and if the value list is empty
                if (i, j) not in all_decoded_objects or not all_decoded_objects[(i, j)]:
                    all_barcode_present = False
                    print(
                        f"No detected barcodes at row {row_letter}, column {col_number}"
                    )

        # If the flag is still True, it means all barcodes are present.
        if all_barcode_present:
            print("All 24 barcodes are present.")

        new_img_height = (
            (rows * box_height) + (rows - 1) * 10 + 100
        )  # 100 pixels for text space
        new_img_width = (
            (cols * box_width) + (cols - 1) * 10 + 50
        )  # 50 pixels for row letters
        new_img = 255 * np.ones(
            shape=[new_img_height, new_img_width, 3], dtype=np.uint8
        )

        undetected_wells = []

        for i in range(rows):
            for j in range(cols):
                y1_new = 50 + i * (box_height + 10)  # 50 pixels for column numbers
                y2_new = y1_new + box_height
                x1_new = 25 + j * (box_width + 10)  # 25 pixels for row letters
                x2_new = x1_new + box_width

                y1 = start_y + (i * (box_height + vertical_gap))
                y2 = y1 + box_height
                x1 = start_x + (j * (box_width + horizontal_gap))
                x2 = x1 + box_width

                # Crop and place in the new image
                crop_image = image[y1:y2, x1:x2]
                new_img[y1_new:y2_new, x1_new:x2_new] = crop_image

                if (i, j) not in detected_boxes:
                    cv2.rectangle(
                        new_img, (x1_new, y1_new), (x2_new, y2_new), (0, 0, 255), 6
                    )
                    row_letter = row_number_to_letter(i)
                    col_number = cols - j
                    undetected_wells.append(f"{row_letter}{col_number}")
                else:
                    cv2.rectangle(
                        new_img, (x1_new, y1_new), (x2_new, y2_new), (0, 255, 0), 6
                    )
        new_img = cv2.flip(new_img, 1)

        # Add column numbers and row letters
        for i in range(rows):
            y = 50 + i * (box_height + 10) + box_height // 2
            cv2.putText(
                new_img,
                row_number_to_letter(i),
                (5, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 0),
                2,
            )

        for j in range(cols):
            x = 25 + j * (box_width + 10) + box_width // 2
            cv2.putText(
                new_img,
                str(j + 1),  # This should start the numbering from 1 instead of 12
                (x, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 0),
                2,
            )

        # Add current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Get the text size
        (text_width, text_height), _ = cv2.getTextSize(
            current_datetime, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
        )

        # Calculate the X coordinate: it should be in the middle of the image
        x = new_img_width // 2 - text_width // 2

        # Calculate the Y coordinate: move it higher up in the image
        y = 5  # 40 pixels from the top; you can adjust this value

        # Draw the text
        cv2.putText(
            new_img,
            current_datetime,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 0),
            2,
        )

        # Add list of undetected wells
        undetected_wells_text = "Undetected: " + ", ".join(undetected_wells)
        cv2.putText(
            new_img,
            undetected_wells_text,
            (50, new_img_height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
        )

        # Show the new image
        resized_image = cv2.resize(
            new_img, dsize=(0, 0), fx=0.5, fy=0.5
        )  # Resize if needed
        # cv2.imshow("Barcode Detection", resized_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # After scan, display window with buttons
        # print(type(resized_image), resized_image.shape, resized_image.dtype)
        self.display_window_with_buttons(all_decoded_objects, resized_image)


# root = Tk()
# set location for output image from scanner
# outpath = "image.bmp"
# trigger a scan when script is run
# scan()

if __name__ == "__main__":
    scanner = BarcodeScanner()
    scanner.scan()
