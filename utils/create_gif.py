from PIL import Image
import imageio
import os



def create_crops_image(image_path,output_dir,crop_width,crop_height,shift_step):

    """"
    create a crops of the image each shift_step pixcels
    """

    # open the image
    large_image = Image.open(image_path)
    img_width, img_height = large_image.size

    cropped_images = []

    # crops the image according to the width and height
    
    for top in range(0, img_height - crop_height, shift_step):
        for left in range(0, img_width - crop_width, shift_step):
            cropped_image = large_image.crop((left, top, left + crop_width, top + crop_height))
            cropped_images.append(cropped_image)

    # Create a directory to save the cropped images if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save each cropped image
    for idx, image in enumerate(cropped_images):
        # Generate a filename for each image
        image_filename = os.path.join(output_dir, f'{idx+1}.jpg')
        # Save the image
        image.save(image_filename)
        print(f"Saved: {image_filename}")
    
    return cropped_images

def create_gif_from_crops(cropped_images_dir,gif_path,resize_width,resize_height):


    def extract_number(filename):
        return int(''.join(filter(str.isdigit, filename)))  # extract only numbers
    
    resized_images = []
    files = sorted(os.listdir(cropped_images_dir), key=extract_number)

    for filename in files:
        image_path = os.path.join(cropped_images_dir, filename)
        
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            img = Image.open(image_path)

            # Resize the images to reduce the size
            resized_image = img.resize((resize_width, resize_height))

            resized_images.append(resized_image)
            
    resized_images = [img.convert("RGB") for img in resized_images]  # Ensure all images are RGB

    # Create the GIF with optimized settings
    resized_images[0].save(gif_path, save_all=True, append_images=resized_images[1:], duration=250, loop=0)

    print(f"Optimized GIF saved successfully: {gif_path}")


image_path = '/workspace/deepstream/deepstream_project/output/dot/pipeline.png' 
output_dir = '/workspace/deepstream/images/output_cropped_images'
crop_width = 1845 # crops the image width each time 1845 pixels
crop_height = 564 #image height
shift_step = 50  

#cropped_images =create_crops_image(image_path,output_dir,crop_width,crop_height,shift_step)

cropped_images_dir= '/workspace/deepstream/images/output_cropped_images'
gif_path = '/workspace/deepstream/deepstream_project/output/dot/output_resized2.gif'
resize_width = 1291   # Adjust the width as needed
resize_height = 394  # Adjust the height as needed


create_gif_from_crops(cropped_images_dir,gif_path,resize_width,resize_height)