import cv2
from pyzbar.pyzbar import decode
import twain

# Create a Twain object
twain_object = twain.Twain()

# Connect to the scanner
twain_object.connect("scanner_name")

# Get the scanner's capabilities
capabilities = twain_object.get_capabilities()

# Print the scanner's capabilities
print(capabilities)

# Disconnect from the scanner
twain_object.disconnect()

# Read the image with OpenCV
image_path = 'gray.tif'
image = cv2.imread(image_path)

# Decode the 2D barcode with pyzbar
decoded_objects = decode(image)
for obj in decoded_objects:
    print("Type:", obj.type)
    print("Data:", obj.data.decode('utf-8'))
