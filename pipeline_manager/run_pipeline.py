import importlib
import sys
import os
import sys
sys.path.append('/workspace/deepstream/deepstream_project')



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
        
    if hasattr(pipeline_module, "run_pipeline"):
        pipeline_module.run_pipeline()
    else:
        print(f"❌ {selected_pipeline} does not contain a function named run_pipeline()")
        sys.exit(1)
