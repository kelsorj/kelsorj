from pymongo import MongoClient
from camera_utils.camera_list import get_camera_mapping
import os
import datetime
import cv2
import sys
import argparse

# Connect to MongoDB
client = MongoClient("mongodb://ekpedevreed1.corp.eikontx.com:27017/")
db = client["mydb"]
collection = db["lab_media_collection"]

# Put text onto frame of image both movie and video
def overlay_text_on_image(frame, text, position=(10, 30), font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, font_color=(255, 255, 255), line_type=2):
    cv2.putText(frame, text, position, font, font_scale, font_color, line_type)
    return frame
    
# Function to create the directory structure
def create_directory_structure(elnid, step, plate_id):
    base_dir = "Z:\ExperimentTracker\images"
    elnid_dir = os.path.join(base_dir, elnid)
    step_dir = os.path.join(elnid_dir, step)
    plate_dir = os.path.join(step_dir, plate_id)

    try:
        os.makedirs(plate_dir, exist_ok=True)
    except OSError as e:
        print(f"Failed to create directory: {e}")
        output_path = r'C:\Labeye_Video\output.txt'  # Specify the output file path
        # Open the file in write mode and write the text
        with open(output_path, 'w') as file:
            file.write(elnid)
            file.write(step)
            file.write(plate_id)
        # Handle the error or provide appropriate feedback to the user

    return plate_dir

# Function to capture and save an image in the correct directory
def capture_and_save_image(camera_url, output_dir, stepID, plate_id):
    # Add code here to capture an image from the camera (using camera_url)
    # and save it to the output_dir
    cap = cv2.VideoCapture(camera_url)

    # Check if the camera stream is opened successfully
    if not cap.isOpened():
        print(f"Failed to open the camera stream for URL: {camera_url}")
        return False

    # Read the first frame from the stream
    ret, frame = cap.read()

    # Check if the frame was successfully read
    if not ret:
        print(f"Failed to read the frame from URL: {camera_url}")
        return False

    image_filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    image_path = os.path.join(output_dir, image_filename)
    # Overlay step name and barcode
    overlay_text = f"Step: {stepID}, Barcode: {plate_id}"
    frame = overlay_text_on_image(frame, overlay_text)
    # Save the captured frame as an image with the specified output file name
    cv2.imwrite(image_path, frame)

    # Release the capture object and close any open windows
    cap.release()
    cv2.destroyAllWindows()

    return image_path

def capture_video(camera_url, output_dir, duration, stepID, plate_id):
    cap = cv2.VideoCapture(camera_url)

    # Check if the camera stream is opened successfully
    if not cap.isOpened():
        print(f"Failed to open the camera stream for URL: {camera_url}")
        return False

    # Get the frames per second (FPS) of the camera stream
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Calculate the total number of frames to capture based on the duration
    total_frames = int(duration * fps)

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    video_filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    video_path = os.path.join(output_dir, video_filename)
    out = cv2.VideoWriter(video_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

    # Start capturing frames for the specified duration
    frame_count = 0

    while frame_count < total_frames:
        ret, frame = cap.read()

        # Check if the frame was successfully read
        if not ret:
            print(f"Failed to read the frame from URL: {camera_url}")
            break
        overlay_text = f"Step: {stepID}, Barcode: {plate_id}"
        frame = overlay_text_on_image(frame, overlay_text)
        # Write the frame to the video file
        out.write(frame)

        frame_count += 1

    # Release the capture and video writer objects
    cap.release()
    out.release()

    return video_path


# Function to record the step in the MongoDB database
def record_step(elnid, plate_id, step, media_path, taskCamera):
    # Strip out the "images/" portion
    media_path = media_path.replace("images/", "")
    print("recording in mongodb")
    entry = {
        'elnid': elnid,
        'plate': plate_id,
        'step': step,
        'filepath': media_path,
        'taskCamera': taskCamera,
        'datetime_processed': datetime.datetime.now()
    }
    collection.insert_one(entry)
    print("recorded in mongodb")


def main(sptELNID, plate_id, stepID, taskCamera, video_dur):
    try:
        # Create the directory structure
        output_dir = create_directory_structure(sptELNID, stepID, plate_id)
        # Capture and save an image in the correct directory
        camera_mapping = get_camera_mapping()
        camera_url = camera_mapping[taskCamera]
        # Try to capture an Image
        image_path = capture_and_save_image(camera_url, output_dir, stepID, plate_id)
    except Exception as e:
        print(f"Failed to capture and save image due to: {e}")
        image_path = "Failed"
    record_step(sptELNID, plate_id, stepID, image_path, taskCamera)
    # Capture and save video in the correct directory
    video_int = int(video_dur)
    if video_int > 0:
        video_path = capture_video(camera_url, output_dir, video_int, stepID, plate_id)
        # Record the video in the MongoDB database
        record_step(sptELNID, plate_id, stepID, video_path, taskCamera)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture and record video and image")
    parser.add_argument("--sptELNID", required=True, help="ELNID")
    parser.add_argument("--plate_id", required=True, help="Plate ID")
    parser.add_argument("--stepID", required=True, help="Step ID")
    parser.add_argument("--taskCamera", required=True, help="Camera task")
    parser.add_argument("--video_dur", required=True, help="Duration of video set 0 for no video")
    args = parser.parse_args()

    main(args.sptELNID, args.plate_id, args.stepID, args.taskCamera, args.video_dur)
