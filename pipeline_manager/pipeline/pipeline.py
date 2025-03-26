
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
#from pipeline_manager.pipeline_elements import create_pipeline_elements, configure_pipeline_elements, add_elements_to_pipeline, link_pipeline_elements,start_pipeline_loop
from gi.repository import GLib, Gst
from pipeline_manager.buffer_processing_videos import osd_sink_pad_buffer_probe
import os

#Create a DOT file
# dot_output_folder = "/workspace/deepstream/deepstream_project/output/dot"
#os.makedirs(dot_output_folder, exist_ok=True)  
#os.environ["GST_DEBUG_DUMP_DOT_DIR"] = dot_output_folder

def run_pipeline(image_path, output_filename):
    platform_info = PlatformInfo()
    Gst.init(None)
    print("🚀 Running Pipeline")

    elements = create_pipeline_elements(image_path)
    configure_pipeline_elements(elements,image_path,output_filename)
    add_elements_to_pipeline(elements["pipeline"], elements,image_path,output_filename)  
    link_pipeline_elements(elements,image_path,output_filename)
    start_pipeline_loop(elements,image_path,output_filename)



def create_pipeline_elements(image_path):

    print("create pipeline elements...")

    pipeline = Gst.Pipeline()

    # determine if input is an image or video
    input_filename = os.path.basename(image_path)  
    source = Gst.ElementFactory.make("filesrc", "file-source")
    is_image = Is_image(image_path)
    if is_image:
        parser = Gst.ElementFactory.make("jpegparse", "jpeg-parser")
    else:
        parser = Gst.ElementFactory.make("h264parse", "h264-parser")

    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    tee = Gst.ElementFactory.make("tee", "nvsink-tee")
    queue1 = Gst.ElementFactory.make("queue", "nvtee-que1")
    queue2 = Gst.ElementFactory.make("queue", "nvtee-que2")
    queue3 = Gst.ElementFactory.make("queue", "nvtee-que3")
    msgconv = Gst.ElementFactory.make("nvmsgconv", "nvmsg-converter")
    msgbroker = Gst.ElementFactory.make("nvmsgbroker", "nvmsg-broker")

    platform_info = PlatformInfo()
    if platform_info.is_integrated_gpu():
        sink = Gst.ElementFactory.make("nv3dsink", "nv3d-sink")
    else:
        sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
    

    nvvidconv_output = Gst.ElementFactory.make("nvvideoconvert", "nvvidconv-output")
    if is_image:
        enc = Gst.ElementFactory.make("nvjpegenc", "jpeg-encoder")
    else:
        enc = Gst.ElementFactory.make("nvv4l2h264enc", "jpeg-encoder")
        muxer = Gst.ElementFactory.make("qtmux", "mp4-muxer")

    

    filesink = Gst.ElementFactory.make("filesink", "file-sink")
    
    if is_image:
        elements = {
        "pipeline": pipeline, "source": source, "parser": parser, "decoder": decoder,
        "streammux": streammux, "pgie": pgie, "nvvidconv": nvvidconv, "nvosd": nvosd,
        "msgconv": msgconv, "msgbroker": msgbroker, "tee": tee, "queue1": queue1,
        "queue2": queue2,"queue3": queue3,  "sink": sink,"nvvidconv_output":nvvidconv_output, "enc": enc, "filesink":filesink
    }
    else:
        elements = {
        "pipeline": pipeline, "source": source, "parser": parser, "decoder": decoder,
        "streammux": streammux, "pgie": pgie, "nvvidconv": nvvidconv, "nvosd": nvosd,
        "msgconv": msgconv, "msgbroker": msgbroker, "tee": tee, "queue1": queue1,
        "queue2": queue2,"queue3": queue3,  "sink": sink,"nvvidconv_output":nvvidconv_output, "enc": enc,"muxer":muxer, "filesink":filesink
    }

    # Check if all elements were created successfully
    for name, elem in elements.items():
        if not elem:
            sys.stderr.write(f"❌ Unable to create {name}\n")
    
    return elements
    

def configure_pipeline_elements(elements,image_path,output_filename):

    """Configures properties for each pipeline element."""

    input_filename = os.path.basename(image_path)  

    print("Configuring Pipeline Properties...\n")

    elements["source"].set_property('location', image_path)
    elements["streammux"].set_property('width', MUXER_OUTPUT_WIDTH)
    elements["streammux"].set_property('height', MUXER_OUTPUT_HEIGHT)
    elements["streammux"].set_property('batch-size', 1)
    elements["streammux"].set_property('batched-push-timeout', MUXER_BATCH_TIMEOUT_USEC)
    elements["pgie"].set_property('config-file-path', PGIE_CONFIG_FILE)
    elements["msgconv"].set_property('config', MSCONV_CONFIG_FILE)
    elements["msgconv"].set_property('payload-type', SCHEMA_TYPE)
    elements["msgbroker"].set_property('proto-lib', PROTO_LIB)
    elements["msgbroker"].set_property('conn-str', CONN_STR)
    if CFG_FILE is not None:
        elements["msgbroker"].set_property('config', CFG_FILE)
        #print("Set property config")
    if TOPIC is not None:
        elements["msgbroker"].set_property('topic', TOPIC)
    elements["msgbroker"].set_property('sync', False)
    elements["sink"].set_property("sync",True) #Ensure it syncs with display timing
    elements["sink"].set_property("qos",False) #avoid frame dropping
    elements["filesink"].set_property("location", output_filename)
    elements["filesink"].set_property("async", False)
    elements["filesink"].set_property("sync", True)

def add_elements_to_pipeline(pipeline, elements,image_path,output_filename):
    """Adds all created elements to the GStreamer pipeline."""

    print("Adding elements to the Pipeline...\n")
    
    pipeline.add(elements["source"])
    pipeline.add(elements["parser"])
    pipeline.add(elements["decoder"])
    pipeline.add(elements["streammux"])
    pipeline.add(elements["pgie"])
    pipeline.add(elements["nvvidconv"])
    pipeline.add(elements["nvosd"])
    pipeline.add(elements["tee"])
    pipeline.add(elements["queue1"])
    pipeline.add(elements["queue2"])
    pipeline.add(elements["queue3"])
    pipeline.add(elements["msgconv"])
    pipeline.add(elements["msgbroker"])
    pipeline.add(elements["sink"])
    pipeline.add(elements["nvvidconv_output"])
    pipeline.add(elements["enc"])
    is_image = Is_image(image_path)
    if not is_image:
        pipeline.add(elements["muxer"])
    pipeline.add(elements["filesink"])

def link_pipeline_elements(elements,image_path,output_filename):
    """Links all elements in the pipeline."""

    print("Linking Pipeline Elements...")

    elements["source"].link(elements["parser"])
    elements["parser"].link(elements["decoder"])

    sinkpad = elements["streammux"].request_pad_simple("sink_0")
    if not sinkpad:
        sys.stderr.write("❌ Unable to get the sink pad of streammux\n")

    srcpad = elements["decoder"].get_static_pad("src")
    if not srcpad:
        sys.stderr.write("❌ Unable to get source pad of decoder\n")
    
    srcpad.link(sinkpad)

    elements["streammux"].link(elements["pgie"])
    elements["pgie"].link(elements["nvvidconv"])
    elements["nvvidconv"].link(elements["nvosd"])
    elements["nvosd"].link(elements["tee"])
    elements["queue1"].link(elements["msgconv"])
    elements["msgconv"].link(elements["msgbroker"])
    elements["queue2"].link(elements["sink"])
    elements["queue3"].link(elements["nvvidconv_output"])
    elements["nvvidconv_output"].link(elements["enc"])

    is_image = Is_image(image_path)

    if is_image:
        elements["enc"].link(elements["filesink"])
    else:
        elements["enc"].link(elements["muxer"])
        elements["muxer"].link(elements["filesink"])


    tee_msg_pad = elements["tee"].request_pad_simple('src_%u')
    tee_render_pad = elements["tee"].request_pad_simple("src_%u")
    tee_bbox_pad = elements["tee"].request_pad_simple("src_%u")

    if not tee_msg_pad or not tee_render_pad or not tee_bbox_pad:
        sys.stderr.write("❌ Unable to get request pads for tee\n")

    tee_msg_pad.link(elements["queue1"].get_static_pad("sink"))
    tee_render_pad.link(elements["queue2"].get_static_pad("sink"))
    tee_bbox_pad.link(elements["queue3"].get_static_pad("sink"))

def start_pipeline_loop(elements,image_path,output_filename):
    """Starts the pipeline and runs the main loop."""
    
    print("Starting Pipeline...")
    
    loop = GLib.MainLoop()
    bus = elements["pipeline"].get_bus()
    #bus.add_signal_watch()
    #bus.connect("message", bus_call, loop)

    def on_message(bus, message, loop):
        """Handles messages from the pipeline to keep the display open."""
        msg_type = message.type

        if msg_type == Gst.MessageType.EOS:
            print("End of Stream reached. Close the window to exit.")
            elements["pipeline"].set_state(Gst.State.PAUSED)  # Keep the image displayed
            #loop.quit()
        elif msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            if "Output window was closed" in str(err):
                print(" Display window closed by user. Exiting gracefully.")
            else:
                print(f"❌ Error: {err}, {debug}")
            loop.quit()
        return True

    # Attach bus watch to wait for user to close the display
    bus.add_watch(0, on_message, loop)

    osdsinkpad = elements["nvosd"].get_static_pad("sink")
    if not osdsinkpad:
        sys.stderr.write("❌ Unable to get sink pad of nvosd\n")

    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)


    # #saving the pipepline as a DOT file with timestamp
    #Gst.debug_bin_to_dot_file_with_ts(elements["pipeline"], Gst.DebugGraphDetails.ALL, "deepstream_pipeline")

    #Start the pipeline
    elements["pipeline"].set_state(Gst.State.PLAYING)
    print("🎥 Displaying image/video... Close the window to exit.")

    try:
        loop.run()
    except KeyboardInterrupt:
        print("🛑 Stopping pipeline...")
    except:
        pass

    elements["pipeline"].set_state(Gst.State.NULL)
    print("✅ Pipeline stopped.")


def Is_image(image_path):
    file_extension = os.path.splitext(image_path)[1].lower()
    is_image = file_extension in ['.jpg','.jpeg','.png']
    return is_image
