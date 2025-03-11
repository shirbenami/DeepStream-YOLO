import importlib
import sys
import os
import sys
sys.path.append('/workspace/deepstream/deepstream_project')
from configs.constants import TOPIC,OUTPUT_FOLDER,INPUT_FOLDER, MSCONV_CONFIG_FILE, MUXER_OUTPUT_WIDTH, MUXER_OUTPUT_HEIGHT, MUXER_BATCH_TIMEOUT_USEC,CONN_STR, SCHEMA_TYPE,PROTO_LIB,CFG_FILE 
import glob


PIPELINE_FOLDER = "pipeline_manager/pipeline"
PIPELINE_MODULE = "pipeline_manager.pipeline"

def list_available_pipelines():
    """Lists all available pipeline scripts inside the pipeline folder."""
    files = [f for f in os.listdir(PIPELINE_FOLDER) if f.endswith(".py") and f != "__init__.py"]
    pipelines = [f[:-3] for f in files]  # Remove ".py" extension
    return pipelines

def select_and_run_pipeline(args):
    """Prompts the user to select a pipeline and runs it."""
    pipelines = list_available_pipelines()
    if not pipelines:
        print("No pipelines found to execute!")
        sys.exit(1)

    print("🔹 Available Pipelines:")
    for i, pipeline in enumerate(pipelines, 1):
        print(f"{i}. {pipeline}")

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

    # Dynamically import and run the selected pipeline
    try:
        pipeline_module = importlib.import_module(f"{PIPELINE_MODULE}.{selected_pipeline}")
    except ModuleNotFoundError as e:
        print(f"❌ Error: Could not find module {PIPELINE_MODULE}.{selected_pipeline}")
        print(e)
        sys.exit(1)

    image_files = glob.glob(os.path.join(INPUT_FOLDER, "*.jpg")) + \
              glob.glob(os.path.join(INPUT_FOLDER, "*.jpeg")) + \
              glob.glob(os.path.join(INPUT_FOLDER, "*.png"))

    if not image_files:
        print("❌ not found any images in", INPUT_FOLDER)
        exit(1)

    for image_path in image_files:
        print(f"🔄 processing image: {image_path}")
    

        input_filename = os.path.basename(image_path)
        output_filename = os.path.join(OUTPUT_FOLDER, input_filename)
        if hasattr(pipeline_module, "run_pipeline"):
            pipeline_module.run_pipeline(image_path, output_filename)
        else:
            print(f"❌ {selected_pipeline} does not contain a function named run_pipeline()")
            sys.exit(1)
        
    
    
    
    """
    if hasattr(pipeline_module, "run_pipeline"):
        pipeline_module.run_pipeline()
    else:
        print(f"❌ {selected_pipeline} does not contain a function named run_pipeline()")
        sys.exit(1)
    """