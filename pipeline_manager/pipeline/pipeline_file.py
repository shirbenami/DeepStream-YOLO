
import sys
sys.path.append('/opt/nvidia/deepstream/deepstream-7.1/sources/deepstream_python_apps/apps')
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst
from optparse import OptionParser
from common.platform_info import PlatformInfo
from common.bus_call import bus_call
from common.utils import long_to_uint64
import pyds
import json
from pipeline_manager.arg_parser import parse_args
from configs.constants import TOPIC,OUTPUT_FOLDER,PGIE_CONFIG_FILE, MSCONV_CONFIG_FILE, MUXER_OUTPUT_WIDTH, MUXER_OUTPUT_HEIGHT, MUXER_BATCH_TIMEOUT_USEC,CONN_STR, SCHEMA_TYPE,PROTO_LIB,CFG_FILE 
from pipeline_manager.pipeline_elements import create_pipeline_elements, configure_pipeline_elements, add_elements_to_pipeline, link_pipeline_elements,start_pipeline_loop
from gi.repository import GLib, Gst
from pipeline_manager.buffer_processing import osd_sink_pad_buffer_probe
import os


def run_pipeline(image_path, output_filename):
    platform_info = PlatformInfo()
    Gst.init(None)
    print("🚀 Running Pipeline")

    # Deprecated: following meta_copy_func and meta_free_func
    # have been moved to the binding as event_msg_meta_copy_func()
    # and event_msg_meta_release_func() respectively.
    # Hence, registering and unsetting these callbacks in not needed
    # anymore. Please extend the above functions as necessary instead.
    # # registering callbacks
    # pyds.register_user_copyfunc(meta_copy_func)
    # pyds.register_user_releasefunc(meta_free_func)

    print("Creating Pipeline \n ")

    elements = create_pipeline_elements(image_path)
    configure_pipeline_elements(elements,image_path,output_filename)
    add_elements_to_pipeline(elements["pipeline"], elements,image_path,output_filename)  
    link_pipeline_elements(elements,image_path,output_filename)
    start_pipeline_loop(elements,image_path,output_filename)


