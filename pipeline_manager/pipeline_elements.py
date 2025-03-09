import sys
sys.path.append('/opt/nvidia/deepstream/deepstream-7.1/sources/deepstream_python_apps/apps')
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from common.platform_info import PlatformInfo

PGIE_CONFIG_FILE = "/workspace/deepstream/deepstream_project/configs/config_infer_primary_yoloV8.txt"
MSCONV_CONFIG_FILE = "/workspace/deepstream/deepstream_project/configs/msgconv_config.txt"

def create_pipeline_elements():
    pipeline = Gst.Pipeline()

    source = Gst.ElementFactory.make("filesrc", "file-source")
    h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    tee = Gst.ElementFactory.make("tee", "nvsink-tee")
    queue1 = Gst.ElementFactory.make("queue", "nvtee-que1")
    queue2 = Gst.ElementFactory.make("queue", "nvtee-que2")
    msgconv = Gst.ElementFactory.make("nvmsgconv", "nvmsg-converter")
    msgbroker = Gst.ElementFactory.make("nvmsgbroker", "nvmsg-broker")

    platform_info = PlatformInfo()
    if platform_info.is_integrated_gpu():
        sink = Gst.ElementFactory.make("nv3dsink", "nv3d-sink")
    else:
        sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")

    if not all([source, h264parser, decoder, streammux, pgie, nvvidconv, nvosd, tee, queue1, queue2, msgconv, msgbroker, sink]):
        sys.stderr.write(" Failed to create pipeline elements\n")

    source.set_property('location', "/workspace/deepstream/deepstream_project/data/videos/input.h264")
    streammux.set_property('width', 1920)
    streammux.set_property('height', 1080)
    streammux.set_property('batch-size', 1)
    pgie.set_property('config-file-path', PGIE_CONFIG_FILE)
    msgconv.set_property('config', MSCONV_CONFIG_FILE)

    pipeline.add(source, h264parser, decoder, streammux, pgie, nvvidconv, nvosd, tee, queue1, queue2, msgconv, msgbroker, sink)

    source.link(h264parser)
    h264parser.link(decoder)
    streammux.link(pgie)
    pgie.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(tee)
    queue1.link(msgconv)
    msgconv.link(msgbroker)
    queue2.link(sink)

    return pipeline, {"nvosd": nvosd}
