import cv2
import numpy as np
import os

def crop_purple(folderloc, image_path, newfolderloc, crop_size=(100, 100)):
    # Read the image
    img = cv2.imread(folderloc + image_path)

    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the range of purple color in HSV
    lower_purple = np.array([125, 50, 50])
    upper_purple = np.array([160, 255, 255])

    # Threshold the image to get only purple pixels
    mask = cv2.inRange(hsv, lower_purple, upper_purple)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the contour with the maximum area
        max_contour = max(contours, key=cv2.contourArea)

        # Find the bounding box of the purple region
        x, y, w, h = cv2.boundingRect(max_contour)

        # Calculate the center of the bounding box
        center_x = x + w // 2
        center_y = y + h // 2

        # Adjust the crop size based on the image dimensions
        crop_width, crop_height = crop_size
        crop_x = max(center_x - crop_width // 2, 0)
        crop_y = max(center_y - crop_height // 2, 0)

        # Ensure the crop dimensions do not exceed the image boundaries
        crop_x = min(crop_x, img.shape[1] - crop_width)
        crop_y = min(crop_y, img.shape[0] - crop_height)

        for color in ["255,0,0","0,255,0", "0,0,255", "0,255,255", "255,0,255", "255,255,0", "255,255,255", "0,0,0"]:
            carimg = cv2.imread(folderloc + image_path.replace('255,0,255', color))
             # Crop the image to the new coordinates
            cropped_carimg = carimg[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]
            cv2.imwrite(newfolderloc + image_path.replace('255,0,255', color), cropped_carimg)
        
        
    else:
        print("No purple color found in the image.")

folderloc = "D:/SelfDrivingImages/vehicle.volkswagen.t2/"
newfolderloc = "D:/SelfDrivingImages/cropped.vehicle.volkswagen.t2/"
# Path to the input image
input_image_path = "ang360h2p-30dist10lshift0color255,0,255.png"
 
# Output path for the cropped image
#output_image_path = ".newimage.png"

# Crop size (width, height)
crop_size = (384, 384)


directory = os.fsencode(folderloc)
    
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith("255,0,255.png"): 
        crop_purple(folderloc, filename, newfolderloc, crop_size)
        #create file with crop coordinates
