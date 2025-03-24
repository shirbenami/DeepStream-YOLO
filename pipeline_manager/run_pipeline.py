import importlib
import sys
import os
import sys
sys.path.append('/workspace/deepstream/deepstream_project')
from configs.constants import TOPIC,OUTPUT_FOLDER_IMAGES,OUTPUT_FOLDER_PREPROCESS,OUTPUT_FOLDER_VIDEOS,INPUT_FOLDER_IMAGES,INPUT_FOLDER_VIDEOS,SHARPEN_FOLDER, MSCONV_CONFIG_FILE, MUXER_OUTPUT_WIDTH, MUXER_OUTPUT_HEIGHT, MUXER_BATCH_TIMEOUT_USEC,CONN_STR, SCHEMA_TYPE,PROTO_LIB,CFG_FILE 
import glob
from gi.repository import Gst

PIPELINE_FOLDER = "pipeline_manager/pipeline"
PIPELINE_MODULE = "pipeline_manager.pipeline"

def list_available_pipelines():

    """
    Lists all available pipeline scripts inside the pipeline folder.

    Returns:
        List of available pipeline script names (without .py extension).
    """

    files = [f for f in os.listdir(PIPELINE_FOLDER) if f.endswith(".py") and f != "__init__.py"]
    pipelines = [f[:-3] for f in files]  # Remove ".py" extension
    return pipelines

def select_and_run_pipeline(args):

    """
    Prompts the user to select a pipeline and runs it on available image files.

    Args:
        args (list): Command-line arguments passed to the script.
    """

    # Get available pipeline scripts
    pipelines = list_available_pipelines()
    if not pipelines:
        print("No pipelines found to execute!")
        sys.exit(1)

    # Display available pipelines for user selection
    print("🔹 Available Pipelines:")
    for i, pipeline in enumerate(pipelines, 1):
        print(f"{i}. {pipeline}")

    # Prompt user to select a pipeline
    choice = input("📌 Enter the pipeline number to execute: ")
    try:
        choice = int(choice) - 1
        if choice < 0 or choice >= len(pipelines):
            raise ValueError
    except ValueError:
        print("❌ Invalid selection!")
        sys.exit(1)

    selected_pipeline = pipelines[choice]
    print(f"🚀 Executing pipeline: {selected_pipeline}")

    if "pre_process" in selected_pipeline.lower():
        #input_folder = SHARPEN_FOLDER
        input_folder = INPUT_FOLDER_IMAGES
        output_folder = OUTPUT_FOLDER_PREPROCESS

    elif "images" in selected_pipeline.lower():
        input_folder = INPUT_FOLDER_IMAGES
        output_folder = OUTPUT_FOLDER_IMAGES

    elif "videos" in selected_pipeline.lower():
        input_folder = INPUT_FOLDER_VIDEOS
        output_folder = OUTPUT_FOLDER_VIDEOS


    else:
        input_folder= INPUT_FOLDER_IMAGES
        output_folder = OUTPUT_FOLDER_IMAGES



    # Dynamically import and run the selected pipeline
    try:
        pipeline_module = importlib.import_module(f"{PIPELINE_MODULE}.{selected_pipeline}")
    except ModuleNotFoundError as e:
        print(f"❌ Error: Could not find module {PIPELINE_MODULE}.{selected_pipeline}")
        print(e)
        sys.exit(1)

    # Search for image files in the INPUT_FOLDER (only jpg, jpeg, png ,h264,mp4 formats)
    image_files = glob.glob(os.path.join(input_folder, "*.jpg")) + \
              glob.glob(os.path.join(input_folder, "*.jpeg")) + \
              glob.glob(os.path.join(input_folder, "*.png")) + \
              glob.glob(os.path.join(input_folder, "*.h264")) + \
              glob.glob(os.path.join(input_folder, "*.mp4")) 

    if not image_files:
        print("❌ not found any images in", input_folder)
        exit(1)

    # Process each image file using the selected pipeline
    for image_path in image_files:
        print(f"🔄 processing image: {image_path}")
        input_filename = os.path.basename(image_path)
        output_filename = os.path.join(output_folder, input_filename)

        # Check if the selected pipeline has the required function
        if hasattr(pipeline_module, "run_pipeline"):
            pipeline_module.run_pipeline(image_path, output_filename)

            
        else:
            print(f"❌ {selected_pipeline} does not contain a function named run_pipeline()")
            sys.exit(1)
