import os 
import json
from PIL import Image,ImageDraw,ImageFont
from configs.constants import INPUT_FOLDER_IMAGES,OUTPUT_FOLDER_JSON, OUTPUT_FOLDER_ANNOTATED_IMAGES

def draw_detections(image_path,detections,output_path):
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    #font = ImageFont.load_default()
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=18)

    for detection in detections:
        box = detection["bounding_box"]
        class_name = detection["class_name"]
        confidence = detection["confidence"]

        x_min = box["x_min"]
        y_min = box["y_min"]
        x_max = box["x_max"]
        y_max = box["y_max"]
        
        # draw the bbox
        draw.rectangle([(x_min,y_min),(x_max,y_max)],outline="red",width=2)

        # draw the labels
        label = f"{class_name}({confidence:.2f})"
        draw.text((x_min-17,y_min-17),label,fill="black",font=font)
    
    image.save(output_path)
    print(f"saved annotated image: {output_path}")


for filename in os.listdir(OUTPUT_FOLDER_JSON):
    if filename.endswith(".json"):
        json_path = os.path.join(OUTPUT_FOLDER_JSON,filename)
        with open(json_path,"r") as f:
            data = json.load(f)
        
        image_name = data["image_name"]
        detections = data["detections"]

        image_path = os.path.join(INPUT_FOLDER_IMAGES,image_name)
        output_path = os.path.join(OUTPUT_FOLDER_ANNOTATED_IMAGES,image_name)

        if os.path.exists(image_path):
            draw_detections(image_path,detections,output_path)
        else:
            print(f"image not found: {image_path}")