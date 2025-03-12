
import sys
sys.path.append('/opt/nvidia/deepstream/deepstream-7.1/sources/deepstream_python_apps/apps')
from pipeline_manager.run_pipeline import select_and_run_pipeline
from pipeline_manager.arg_parser import parse_args

if __name__ == '__main__':
    args = parse_args()
    # If argument parsing fails, returns failure (non-zero)
    if args == 1:
        sys.exit(1)
    sys.exit(select_and_run_pipeline(sys.argv))
