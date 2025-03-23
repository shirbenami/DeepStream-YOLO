import cv2
import os
import numpy as np
from configs.constants import INPUT_FOLDER, SHARPEN_FOLDER


def sharpen():
    input_folder = INPUT_FOLDER
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
    

sharpen()