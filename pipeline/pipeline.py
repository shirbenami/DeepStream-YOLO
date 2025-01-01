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

    print("Entering probe")

   # frame_number = 0
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

        print(f"Processing frame: {frame_number}")
        num_rects = frame_meta.num_obj_meta

        frame_counter += 1  # Increment the frame counter

        l_obj = frame_meta.obj_meta_list

        # Initialize metadata structure
        frame_metadata = {
            "image_name": f"frame_{frame_number}.jpg",  # Example of how you can define the image name
            "image_size": {
                "width": frame_meta.source_frame_width,
                "height": frame_meta.source_frame_height
            },
            "detections": []
        }

        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break

            # if obj_meta.class_id not in valid_class_ids:
            #   continue

            if obj_meta.class_id not in obj_counter:
            	obj_counter[obj_meta.class_id] = 0
            obj_counter[obj_meta.class_id] += 1

            obj_data = {
                "class_id": obj_meta.class_id,
                "class_name": class_names.get(obj_meta.class_id, "unknown"),
                "confidence": obj_meta.confidence,
                "bounding_box": {
                    "x_min": obj_meta.rect_params.left,
                    "y_min": obj_meta.rect_params.top,
                    "x_max": obj_meta.rect_params.left + obj_meta.rect_params.width,
                    "y_max": obj_meta.rect_params.top + obj_meta.rect_params.height
                }
            }

            # Add the object data to the detections list
            frame_metadata["detections"].append(obj_data)

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
    print("Exiting probe")
    return result




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
    streammux.set_property('width', 1920)  # Set output width
    streammux.set_property('height', 1080)  # Set output height
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

   # Add elements to pipeline
    pipeline.add(source)
    pipeline.add(h264parser)
    pipeline.add(decoder)
    pipeline.add(streammux)
    pipeline.add(pgie)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(vidconv)
    pipeline.add(encoder)
    pipeline.add(parser)
    pipeline.add(muxer)
    pipeline.add(sink)

    # Link elements in the pipeline
    # file-source -> qtdemux -> h264-parser -> nvh264-decoder ->
    # nvinfer -> nvvidconv -> nvosd -> video-renderer

   # Get source pad of the decoder
   # srcpad = decoder.get_static_pad("src")
   # if not srcpad:
    #    sys.stderr.write(" Unable to get source pad of decoder \n")

   # Get sink pad of the streammux
   # sinkpad = streammux.get_request_pad("sink_0")
   # if not sinkpad:
    #    sys.stderr.write(" Unable to get the sink pad of streammux \n")

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

  # Link the source pad of the decoder to the sink pad of the streammux
    source.link(h264parser)
    h264parser.link(decoder)
    #decoder.connect("pad-added", decoder_src_pad_added, streammux)
    srcpad.link(sinkpad)
    streammux.link(pgie)
    pgie.link(nvvidconv)
    nvvidconv.link(nvosd)  # Link the video converter to the OSD
    nvosd.link(vidconv)
    vidconv.link(encoder)
    encoder.link(parser)
    parser.link(muxer)
    muxer.link(sink)  # Link the muxer to the sink

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

