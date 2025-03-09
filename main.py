
import sys
sys.path.append('/opt/nvidia/deepstream/deepstream-7.1/sources/deepstream_python_apps/apps')
from pipeline_manager import run_pipeline
from pipeline_manager.pipeline_elements import parse_args

if __name__ == '__main__':
    ret = parse_args()
    if ret == 1:
        sys.exit(1)
    sys.exit(run_pipeline())
