#!/usr/bin/env python3
import sys
import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst
from common.platform_info import PlatformInfo
from common.bus_call import bus_call
import pyds
import json  # Ensure json is imported to handle JSON files
import ctypes
sys.path.append('/opt/nvidia/deepstream/deepstream/lib')


# Define class IDs for different objects
PGIE_CLASS_ID_PERSON = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_CAR = 2
PGIE_CLASS_ID_MOTORCYCLE = 3
PGIE_CLASS_ID_AIRPLANE = 4
PGIE_CLASS_ID_BUS = 5
PGIE_CLASS_ID_TRAIN = 6
PGIE_CLASS_ID_TRUCK = 7


#PGIE_CLASS_ID_ROADSIGN = 3
MUXER_BATCH_TIMEOUT_USEC = 33000

valid_class_ids = [PGIE_CLASS_ID_PERSON, PGIE_CLASS_ID_BICYCLE, PGIE_CLASS_ID_CAR]

class_names = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane", 5: "bus", 6: "train", 7: "truck"}  # Add the class names

metadata= {}

# Function to handle the metadata and display on-screen information
def osd_sink_pad_buffer_probe(pad, info, u_data):

    num_rects = 0
   # metadata = {}
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    # Retrieve batch metadata from the gst_buffer
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list

    frame_limit = 10  # Define how many frames to process
    frame_counter = 0  # Initialize the frame counter

    while l_frame is not None:

	#print("Entering frame loop")
        # if frame_counter >= frame_limit:
        # break  # Stop processing after the frame limit is reached

        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        obj_counter = {
            PGIE_CLASS_ID_PERSON: 0,
            PGIE_CLASS_ID_BICYCLE: 0,
            PGIE_CLASS_ID_CAR: 0,
            PGIE_CLASS_ID_MOTORCYCLE: 0,
        PGIE_CLASS_ID_AIRPLANE: 0,
        PGIE_CLASS_ID_BUS: 0,
        PGIE_CLASS_ID_TRAIN: 0,
        PGIE_CLASS_ID_TRUCK: 0
        }

        frame_number = frame_meta.frame_num

     #   print(f"Processing frame: {frame_number}")
        num_rects = frame_meta.num_obj_meta

        frame_counter += 1  # Increment the frame counter

        l_obj = frame_meta.obj_meta_list

        # Initialize metadata structure
        frame_metadata = {
            "image_name": f"frame_{frame_number}.jpg",  # Example of how you can define the image name
            "image_size": {
                "width": frame_meta.source_frame_width,
                "height": frame_meta.source_frame_height,
                "num object meta": frame_meta.num_obj_meta
            },
            "detections": []
        }

        frame_number = frame_meta.frame_num

        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)

                # Print or process the metadata
                # print(f"Object ID: {obj_meta.object_id}, Class: {obj_meta.class_id}")
                #print(f"Component ID: {obj_meta.unique_component_id}")

            except StopIteration:
                break

            if obj_meta.class_id not in obj_counter:
            	obj_counter[obj_meta.class_id] = 0

            obj_counter[obj_meta.class_id] += 1

            if frame_number % 50 == 0:

                obj_data = {
                    "class_id": obj_meta.class_id,
                    "class_name": class_names.get(obj_meta.class_id, "unknown"),
                    "confidence": obj_meta.confidence,
                    "bounding_box": {
                        "left": obj_meta.rect_params.left,
                        "top": obj_meta.rect_params.top,
                        "width": obj_meta.rect_params.width,
                        "height": obj_meta.rect_params.height
                    }
                }

                # Add the object data to the detections list
                frame_metadata["detections"].append(obj_data)
                # for detection in frame_metadata['detections']:
                #   print(detection)


                user_event_meta = pyds.nvds_acquire_user_meta_from_pool(batch_meta)
                if user_event_meta:
                    msg_meta = pyds.alloc_nvds_event_msg_meta()
                    msg_meta.bbox.top = obj_meta.rect_params.top
                    msg_meta.bbox.left = obj_meta.rect_params.left
                    msg_meta.bbox.width = obj_meta.rect_params.width
                    msg_meta.bbox.height = obj_meta.rect_params.height
                    msg_meta.frameId = frame_number

                    # msg_meta.trackingId = long_to_uint64(obj_meta.object_id)
                    # msg_meta.trackingId = int(ctypes.c_uint64(obj_meta.object_id).value
                    msg_meta.trackingId = frame_number
                    msg_meta.confidence = obj_meta.confidence
                    msg_meta = generate_event_msg_meta(msg_meta, obj_meta.class_id)

                    # print(f"Sending Meta - sensorId: {msg_meta.sensorId}, bbox: {msg_meta.bbox.left}, {msg_meta.bbox.top}")

                    user_event_meta.user_meta_data = msg_meta
                    user_event_meta.base_meta.meta_type = pyds.NvDsMetaType.NVDS_EVENT_MSG_META
                    pyds.nvds_add_user_meta_to_frame(frame_meta, user_event_meta)



            try:
                l_obj = l_obj.next
            except StopIteration:
                break

        # Add metadata for this frame to the overall metadata
        #if frame_number not in metadata:
        metadata[frame_number] = frame_metadata

       # Force frame advance
        if l_frame.next is not None:
       	    l_frame = l_frame.next
        else:
            break

        # Acquire display metadata for drawing the text
        display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        py_nvosd_text_params = display_meta.text_params[0]

        # Set offsets for text position
        py_nvosd_text_params.x_offset = 10
        py_nvosd_text_params.y_offset = 12
        py_nvosd_text_params.set_bg_clr = 1
        py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)  # Black background

        # Display the text (not essential for saving metadata but useful for on-screen display)
        print(pyds.get_string(py_nvosd_text_params.display_text))
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)

    # After processing the frames, save the metadata to a JSON file
    with open('/workspace/ssl_project/output/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)

    result = Gst.PadProbeReturn.OK

    #print(f"Frame {frame_number}: {len(frame_metadata['detections'])} objects detected")

   # print("Exiting probe")
    return result


def generate_event_msg_meta(data, class_id):
    meta = pyds.NvDsEventMsgMeta.cast(data)
    meta.sensorId = 0
    meta.placeId = 0
    meta.moduleId = 0
    meta.sensorStr = "sensor-0"
    meta.ts = pyds.alloc_buffer(32)
    pyds.generate_ts_rfc3339(meta.ts, 32)
   # meta.type = pyds.NvDsEventType.NVDS_EVENT_MOVING
   # meta.objType = pyds.NvDsObjectType.NVDS_OBJECT_TYPE_UNKNOWN
   # meta.objClassId = obj_meta.class_id
    return meta


def long_to_uint64(l):
    value = ctypes.c_uint64(l & 0xffffffffffffffff).value
    print(f"Converted Tracking ID:{value}")
    return value
   # return ctypes.c_uint64(l).value

def main(args):
    # Check input arguments
    if len(args) != 2:
        sys.stderr.write("usage: %s <media file or uri>\n" % args[0])
        sys.exit(1)

    platform_info = PlatformInfo()
    Gst.init(None)  # Initialize GStreamer

    # Create pipeline
    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()

    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")

    # Create source element (reading from video file)
    print("Creating Source \n ")
    source = Gst.ElementFactory.make("filesrc", "file-source")
    if not source:
        sys.stderr.write(" Unable to create Source \n")

    source.set_property('location', args[1])

    # Create elements for parsing and decoding the video
    print("Creating H264Parser \n")
    h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
    if not h264parser:
        sys.stderr.write(" Unable to create h264 parser \n")

    h264parser.set_property("config-interval", 1)  # Enable configuration interval

    print("Creating Decoder \n")
    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
   # decoder = Gst.ElementFactory.make("decodebin", "decoder")
    if not decoder:
        sys.stderr.write(" Unable to create Nvv4l2 Decoder \n")

    # Create streammux to batch input video
    print("Creating Stream Muxer \n")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write(" Unable to create NvStreamMux \n")
    streammux.set_property('batch-size', 1)
    streammux.set_property('width', 640)  # Set output width
    streammux.set_property('height', 640)  # Set output height
    streammux.set_property('batched-push-timeout', 1000000)  # Set batch timeout

    # Create primary inference element for object detection
    print("Creating Primary Inference Element \n")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        sys.stderr.write(" Unable to create pgie \n")

    # Set the path to your YOLOv8 configuration file here
    pgie.set_property('config-file-path', 'config_infer_primary_yoloV8.txt')

    # Convert video format to RGBA for on-screen display
    print("Creating Video Converter \n")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")

    # Create an encoder for H264 (codec=1)
    print("Creating H264 Encoder \n")
    #encoder = Gst.ElementFactory.make("nvh264enc", "h264-encoder")  # Use nvh264enc for hardware-accelerated encoding
    encoder = Gst.ElementFactory.make("x264enc", "h264-encoder")

    if not encoder:
        sys.stderr.write(" Unable to create H264 encoder \n")

   # Make parser
    print("Creating parser \n")
    parser = Gst.ElementFactory.make("h264parse", "h264parse")
    if not parser:
        sys.stderr.write(" Unable to create h264parse")

    # Make mux
    print("Creating muxer \n")
    muxer = Gst.ElementFactory.make("mp4mux", "mp4mux")
    if not muxer:
        sys.stderr.write(" Unable to create mp4mux \n")


    # Create OSD (On-Screen Display) to draw labels and boxes
    print("Creating OSD \n")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")


    # Create tee to split the stream
    print("Creating tee \n")
    tee = Gst.ElementFactory.make("tee", "tee-element")
    if not tee:
    	sys.stderr.write(" Unable to create tee \n")


    # Create queues for each branch
    print("Creating queue1 for video \n")
    queue1 = Gst.ElementFactory.make("queue", "queue-video")
    if not queue1:
        sys.stderr.write(" Unable to create queue1 \n")


    print("Creating queue2 for json \n")
    queue2 = Gst.ElementFactory.make("queue", "queue-json")
    if not queue2:
        sys.stderr.write(" Unable to create queue2 \n")


    def probe_func(pad, info, u_data):
        #print("JSON metadata is flowing")
        return Gst.PadProbeReturn.OK

    # Add probe to the sink pad of queue2
    queue2_pad = queue2.get_static_pad("sink")
    if queue2_pad:
        queue2_pad.add_probe(Gst.PadProbeType.BUFFER, probe_func, 0)
    else:
        sys.stderr.write(" Unable to get sink pad of queue2 \n")

    # Create msgconv to create json from metadata
    print("Creating msgconv \n")
    msgconv = Gst.ElementFactory.make("nvmsgconv", "message-converter")
    if not msgconv:
    	sys.stderr.write(" Unable to create nvmsgconv \n")

    msgconv.set_property("payload-type", 0)  # 0 - JSON
    msgconv.set_property("comp-id", 2)
    msgconv.set_property("config", "msgconv_config.txt")
    msgconv.set_property("msg2p-lib","/opt/nvidia/deepstream/deepstream/lib/libnvds_msgconv.so")
    msgconv.set_property("debug-payload-dir","/workspace/ssl_project/output/debug")


    msgbroker = Gst.ElementFactory.make("nvmsgbroker", "nvmsg-broker")
    if not msgbroker:
        sys.stderr.write(" Unable to create msgbroker \n")
    msgbroker.set_property('config', 'cfg_amqp.txt')
    msgbroker.set_property('proto-lib', '/opt/nvidia/deepstream/deepstream-5.1/lib/libnvds_amqp_proto.so')
   # msgbroker.set_property('conn-str', 'amqp://myuser:mypassword@172.17.0.2:5672/%2F')

    #msgbroker.set_property('conn-str', 'localhost;5672;myuser')
    msgbroker.set_property('sync', False)
    msgbroker.set_property('topic', 'topicname')

    # Create nvvideoconvert
    print("Creating Video Converter \n")
    vidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor_postosd")
    if not vidconv:
        sys.stderr.write(" Unable to create vidconv \n")

    # Create a filesink for saving the output video
    sink = Gst.ElementFactory.make("filesink", "video-output")
    if not sink:
        sys.stderr.write(" Unable to create filesink \n")
    sink.set_property("location", "/workspace/ssl_project/output/yolo_output2.mp4")
    sink.set_property("sync", 0)
    sink.set_property("sync", False)
    sink.set_property("async", False)

    # Create json sink
    jsonsink = Gst.ElementFactory.make("filesink", "json-output")
    jsonsink.set_property("location", "/workspace/ssl_project/output/msgconv_metadata.json")
    jsonsink.set_property("sync", False)

   # Add elements to pipeline
    pipeline.add(source) # Video source (file or camera stream)
    pipeline.add(h264parser) # Parses H.264 video stream into raw data
    pipeline.add(decoder)   # Decodes H.264 stream into raw video frames
    pipeline.add(streammux) # Muxer that combines multiple video streams into one (required for inference)
    pipeline.add(pgie)   # Primary GIE (AI model for object detection, e.g., YOLO or ResNet)
    pipeline.add(nvvidconv)   # Video converter (resizes or changes color format, e.g., RGBA to NV12)
    pipeline.add(nvosd)  # On-Screen Display (draws bounding boxes and labels on video)
    pipeline.add(tee) # Tee element splits the stream into two paths (video and metadata)
    pipeline.add(queue1)  # Add queue for video
    pipeline.add(queue2)  # Add queue for json
    pipeline.add(msgconv) # Converts metadata to JSON format
    pipeline.add(vidconv)  # Additional video converter before encoding
    pipeline.add(encoder) # Encodes video back to compressed format (e.g., H.264)
    pipeline.add(parser)  # Parses the encoded video before saving in mp4 file
    pipeline.add(muxer)    # Muxes audio and video to produce an MP4 file
#    pipeline.add(msgconv)
   # pipeline.add(msgbroker)
    pipeline.add(sink)    # Sink element that writes the processed video to a file
    pipeline.add(jsonsink) # Sink element that writes JSON metadata to a file

    # Link elements in the pipeline

    sinkpad = streammux.get_request_pad("sink_0")
    if not sinkpad:
        sys.stderr.write(" Unable to get the sink pad of streammux \n")
    srcpad = decoder.get_static_pad("src")
    if not srcpad:
        sys.stderr.write(" Unable to get source pad of decoder \n")


    def decoder_src_pad_added(decoder, pad, streammux):
    	print("Linking decoder src pad to streammux sink pad")
    	sinkpad = streammux.get_request_pad("sink_0")
    	if not sinkpad.is_linked():
            pad.link(sinkpad)

    print("Linking elements in the Pipeline \n")
    source.link(h264parser)
    h264parser.link(decoder)
    srcpad.link(sinkpad)

    streammux.link(pgie)
    pgie.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(tee)

    tee_video_pad = tee.get_request_pad("src_%u")
    tee_json_pad = tee.get_request_pad("src_%u")

    if not tee_video_pad or not tee_json_pad:
    	sys.stderr.write(" Unable to get tee pads \n")


    queue1_pad = queue1.get_static_pad("sink")
    queue2_pad = queue2.get_static_pad("sink")

    if not queue1_pad or not queue2_pad:
        sys.stderr.write(" Unable to get queue pads \n")

    tee_video_pad.link(queue1_pad)
    tee_json_pad.link(queue2_pad)

     #Link the video queue to the video processing path
    queue1.link(vidconv)
    vidconv.link(encoder)
    encoder.link(parser)
    parser.link(muxer)
    muxer.link(sink)
    muxer.link(msgbroker)

    # Link the json queue to the msgconv and jsonsink
    #pgie.link(msgconv)
    queue2.link(msgconv)
    msgconv.link(jsonsink)
   # msgconv.link(msgbroker)

    # Add probe to get informed of the metadata generated
    osdsinkpad = nvosd.get_static_pad("sink")
    if not osdsinkpad:
        sys.stderr.write(" Unable to get sink pad of nvosd \n")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

    # Create an event loop and listen to messages
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    # Start playback and listen for events
    print("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass
    # Cleanup
    pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    sys.exit(main(sys.argv))

