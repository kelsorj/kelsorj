from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from datetime import datetime
import paho.mqtt.client as mqtt
import subprocess
import time
from pyaxidraw import axidraw   # Import the module

ad = axidraw.AxiDraw()          # Create class instance

# Create an MQTT client
client = mqtt.Client()

# Create a flag to indicate if all CSVs are read successfully
all_csvs_read_successfully = True

def read_csv_file(filename):
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
            last_elem = lines[-1].split(",")
            num = int(last_elem[1])
            print(num)
            return num
    except (ValueError, FileNotFoundError) as e:
        print(f"Error opening {filename}: {e}")
        global all_csvs_read_successfully
        all_csvs_read_successfully = False
        return 0


def calculate_total(numArray):
    total = sum(numArray)
    print("total = " + str(total))
    return str(total)


def format_number_with_periods(number):
    formatted_number = "{:,}".format(int(number))
    formatted_number = formatted_number.replace(",", ".")
    return formatted_number

# Define what to do when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {rc}')
    client.subscribe('rpi/gpio')

# Define what to do when a message is received
def on_message(client, userdata, msg):
    print(msg.topic + ' ' + str(msg.payload))
    if msg.payload == b'trigger':
        print('Triggering script...')
        subprocess.call(['python', '/home/pi/powerOn.py'])

# Load the font file
font = TTFont(
    "/Users/kelsorj/anaconda3/pkgs/rdkit-2023.03.1-py39hcba3512_0/share/RDKit/Data/Fonts/ComicNeue-Italic.ttf"
)

# Get the cmap table
cmap = font["cmap"]
# Get the best Unicode cmap dictionary
best_cmap = cmap.getBestCmap()
# Get the glyph order
glyph_order = font.getGlyphOrder()

# Get the glyph set
glyph_set = font.getGlyphSet()

B1NUM = read_csv_file("/Volumes/LABDATA/Labeye_Video/Bender1_OLS.csv")
B2NUM = read_csv_file("/Volumes/LABDATA/Labeye_Video/Bender2_OLS.csv")
B3NUM = read_csv_file("/Volumes/LABDATA/Labeye_Video/Bender3_OLS.csv")
B4NUM = read_csv_file("/Volumes/LABDATA/Labeye_Video/Bender4_OLS.csv")

if all_csvs_read_successfully:
    # Proceed with the rest of the code only if all CSVs are read successfully
    total = calculate_total([B1NUM, B2NUM, B3NUM, B4NUM])
    # The word to render
    formatted_number = format_number_with_periods(total)
    word = str(formatted_number)

    # The initial position
    x = 0
    y_min = 0
    y_max = 0
    width = 0

    # Desired SVG box dimensions and padding
    svg_width_inches = 11.9  # Width in inches
    svg_height_inches = 3  # Height in inches
    padding_inches = 0.1  # Padding in inches

    # Convert inches to pixels based on DPI (dots per inch)
    dpi = 96  # Adjust DPI as needed
    svg_width_pixels = int(svg_width_inches * dpi)
    svg_height_pixels = int(svg_height_inches * dpi)
    padding_pixels = int(padding_inches * dpi)

    for char in word:
        # glyph_name = cmap[char]
        glyph_name = best_cmap[ord(char)]
        # Get the glyph order
        glyph_order = font.getGlyphOrder()
        # Get the glyph ID by its index
        glyph_id = glyph_order.index(glyph_name)
        # Get the glyph name
        glyph_name = font.getGlyphName(glyph_id)

        # Get the bounds of the glyph
        bounds_pen = BoundsPen(glyph_set)
        glyph_set[glyph_name].draw(bounds_pen)
        bbox = bounds_pen.bounds

        if bbox is not None:
            _, y0, _, y1 = bbox
            y_min = min(y_min, y0)
            y_max = max(y_max, y1)

        # Get the advance width for this glyph and add it to the x position
        advance_width, _ = font["hmtx"][glyph_name]
        x += advance_width

        width = max(width, x)

    # Compute scaling factors
    x_scale = (svg_width_pixels - 2 * padding_pixels) / width
    y_scale = (svg_height_pixels - 2 * padding_pixels) / (y_max - y_min)

    # Recalculate x
    x = 0

    # Calculate the date box dimensions
    date_box_width_inches = 3  # Width in inches
    date_box_height_inches = 0.5  # Height in inches
    date_box_padding_inches = 0.1  # Padding in inches
    # Convert inches to pixels based on DPI
    date_box_width_pixels = int(date_box_width_inches * dpi)
    date_box_height_pixels = int(date_box_height_inches * dpi)
    date_box_padding_pixels = int(date_box_padding_inches * dpi)
    total_height = date_box_height_pixels + svg_height_pixels

    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width_pixels} {total_height}" width="{svg_width_inches}in" height="{svg_height_inches}in">\n'

    for char in word:
        # glyph_name = cmap[char]
        glyph_name = best_cmap[ord(char)]
        # Get the glyph order
        glyph_order = font.getGlyphOrder()
        # Get the glyph ID by its index
        glyph_id = glyph_order.index(glyph_name)
        glyph_name = font.getGlyphName(glyph_id)

        # Prepare an SVG pen
        pen = SVGPathPen(glyph_set)

        # Draw the character
        glyph_set[glyph_name].draw(pen)

        # Get the SVG path commands
        svg_path = pen.getCommands()

        # Add the path to the SVG content, transforming it to the correct position, scaling, and flipping it vertically
        svg_content += f'    <path transform="translate({padding_pixels + x * x_scale} {svg_height_pixels - padding_pixels}) scale({x_scale} {-y_scale})" d="{svg_path}" fill="none" stroke="black"/>\n'

        # Get the advance width for this glyph and add it to the x position
        advance_width, _ = font["hmtx"][glyph_name]
        x += advance_width

    #####################
    # Calculate the date string
    date_string = datetime.now().strftime("%Y-%m-%d")
    # Calculate the date box dimensions
    date_box_width_inches = 3  # Width in inches
    date_box_height_inches = 0.5  # Height in inches
    date_box_padding_inches = 0.1  # Padding in inches
    # Convert inches to pixels based on DPI
    date_box_width_pixels = int(date_box_width_inches * dpi)
    date_box_height_pixels = int(date_box_height_inches * dpi)
    date_box_padding_pixels = int(date_box_padding_inches * dpi)
    advance_width = date_box_width_pixels / (len(str(date_string)) + 1)
    ## Calculate the main box dimensions
    main_box_width_inches = svg_width_inches  # Width in inches
    main_box_height_inches = svg_height_inches  # Height in inches
    main_box_padding_inches = padding_inches  # Padding in inches
    # Convert inches to pixels based on DPI
    main_box_width_pixels = int(main_box_width_inches * dpi)
    main_box_height_pixels = int(main_box_height_inches * dpi)
    main_box_padding_pixels = int(main_box_padding_inches * dpi)
    # Calculate the position of the main box
    main_box_x = main_box_padding_pixels
    main_box_y = main_box_padding_pixels
    # Calculate scaling factors
    x_scale = (date_box_width_pixels - 2 * padding_pixels) / width
    y_scale = (date_box_height_pixels - 2 * padding_pixels) / (y_max - y_min)
    # Calculate the position of the date text
    date_text_x = main_box_x + main_box_width_pixels - date_box_width_pixels - 30
    date_text_y = (
        main_box_y + main_box_height_pixels + (date_box_height_pixels/2)
    )  # Adjust the vertical offset as needed
    for char in date_string:
        glyph_name = best_cmap[ord(char)]
        glyph_id = glyph_order.index(glyph_name)
        glyph_name = font.getGlyphName(glyph_id)
        # Get the bounds of the glyph
        bounds_pen = BoundsPen(glyph_set)
        glyph_set[glyph_name].draw(bounds_pen)
        bbox = bounds_pen.bounds
        if bbox is not None:
            _, y0, _, y1 = bbox
            y_min = min(y_min, y0)
            y_max = max(y_max, y1)
        # Prepare an SVG pen
        pen = SVGPathPen(glyph_set)
        # Draw the character
        glyph_set[glyph_name].draw(pen)
        # Get the SVG path commands
        svg_path = pen.getCommands()
        # Add the path to the SVG content, transforming it to the correct position, scaling, and flipping it vertically
        svg_content += f'    <path transform="translate({padding_pixels + date_text_x} {date_text_y}) scale({x_scale} {-y_scale})" d="{svg_path}" fill="none" stroke="black"/>\n'
        # Get the advance width for this glyph and add it to the x position
        # advance_width, _ = font['hmtx'][glyph_name]
        date_text_x += advance_width

    svg_content += "</svg>\n"
    # Save the SVG file to disk
    svg_filename = "output.svg"
    with open(svg_filename, "w") as file:
        file.write(svg_content)
    print(f"SVG file saved as {svg_filename}")

    #######################################
    # Trigger the MQTT broker to scroll
    # the paper
    #######################################
    #client.connect('10.30.1.123', 1883, 60)

    # Publish a message to the "rpi/gpio" topic
    #client.publish('rpi/gpio', 'trigger')

    # Disconnect from the broker
    #client.disconnect()

    #time.sleep(360)  # 5 minutes = 300 seconds

    #######################################
    # Plot the well numbers
    #######################################
    # Load file & configure plot context
    ad.plot_setup("/Users/kelsorj/Drawing/output.svg")
    # Plot the file
    ad.plot_run() 
else:
    print("Not all CSV files could be read. Skipping plotting.")

                

