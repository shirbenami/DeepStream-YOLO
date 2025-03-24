import cv2
import os
import numpy as np
from configs.constants import INPUT_FOLDER_IMAGES,SHARPEN_FOLDER
import tempfile

def sharpen_image(image_path):
     """
     sharpening the image
     """
     sharpen_kernel = np.array([[0, -1, 0],
                            [-1, 5,-1],
                            [0, -1, 0]])
     img = cv2.imread(image_path)
     sharpened = cv2.filter2D(img, -1, sharpen_kernel)
    # Create temporary file in the same folder (or change dir if needed)
     temp_dir = tempfile.gettempdir()  # default temp folder
     filename = os.path.basename(image_path)
     sharpened_path = os.path.join(temp_dir, f"sharpened_{filename}")
    
     # Save the sharpened image
     cv2.imwrite(sharpened_path, sharpened)

     return sharpened_path

    





def sharpen_folder():
    input_folder = INPUT_FOLDER_IMAGES
    output_folder = SHARPEN_FOLDER
    os.makedirs(output_folder, exist_ok=True)

    sharpen_kernel = np.array([[0, -1, 0],
                            [-1, 5,-1],
                            [0, -1, 0]])

    for filename in os.listdir(input_folder):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            img_path = os.path.join(input_folder, filename)
            img = cv2.imread(img_path)

            sharpened = cv2.filter2D(img, -1, sharpen_kernel)
            cv2.imwrite(os.path.join(output_folder, filename), sharpened)
    

