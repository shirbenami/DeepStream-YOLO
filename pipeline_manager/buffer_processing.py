import pyds
from gi.repository import Gst
from configs.constants import PGIE_CLASS_ID_PERSON,PGIE_CLASS_ID_BICYCLE,PGIE_CLASS_ID_CAR,PGIE_CLASS_ID_MOTORCYCLE,PGIE_CLASS_ID_AIRPLANE,PGIE_CLASS_ID_AIRPLANE,PGIE_CLASS_ID_BUS,PGIE_CLASS_ID_TRAIN,PGIE_CLASS_ID_TRUCK


# osd_sink_pad_buffer_probe  will extract metadata received on OSD sink pad
# and update params for drawing rectangle, object information etc.
# IMPORTANT NOTE:
# a) probe() callbacks are synchronous and thus holds the buffer
#    (info.get_buffer()) from traversing the pipeline until user return.
# b) loops inside probe() callback could be costly in python.
#    So users shall optimize according to their use-case.
def osd_sink_pad_buffer_probe(pad, info, u_data):
    frame_number = 0
    # Intiallizing object counter with 0.
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

    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    # Retrieve batch metadata from the gst_buffer
    # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
    # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    if not batch_meta:
        return Gst.PadProbeReturn.OK
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting is done by pyds.NvDsFrameMeta.cast()
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            continue
        is_first_object = True

    

        # Short example of attribute access for frame_meta:
        # print("Frame Number is ", frame_meta.frame_num)
        # print("Source id is ", frame_meta.source_id)
        # print("Batch id is ", frame_meta.batch_id)
        # print("Source Frame Width ", frame_meta.source_frame_width)
        # print("Source Frame Height ", frame_meta.source_frame_height)
        # print("Num object meta ", frame_meta.num_obj_meta)

        frame_number = frame_meta.frame_num
        l_obj = frame_meta.obj_meta_list

        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                continue

            # Update the object text display
            txt_params = obj_meta.text_params

            # Set display_text. Any existing display_text string will be
            # freed by the bindings module.
            txt_params.display_text = pgie_classes_str[obj_meta.class_id]

            obj_counter[obj_meta.class_id] += 1

            # Font , font-color and font-size
            txt_params.font_params.font_name = "Serif"
            txt_params.font_params.font_size = 10
            # set(red, green, blue, alpha); set to White
            txt_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)

            # Text background color
            txt_params.set_bg_clr = 1
            # set(red, green, blue, alpha); set to Black
            txt_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)

            # Ideally NVDS_EVENT_MSG_META should be attached to buffer by the
            # component implementing detection / recognition logic.
            # Here it demonstrates how to use / attach that meta data.
            if is_first_object and (frame_number % 30) == 0:
                # Frequency of messages to be send will be based on use case.
                # Here message is being sent for first object every 30 frames.

                user_event_meta = pyds.nvds_acquire_user_meta_from_pool(
                    batch_meta)
                if user_event_meta:
                    # Allocating an NvDsEventMsgMeta instance and getting
                    # reference to it. The underlying memory is not manged by
                    # Python so that downstream plugins can access it. Otherwise
                    # the garbage collector will free it when this probe exits.
                    msg_meta = pyds.alloc_nvds_event_msg_meta(user_event_meta)
                    msg_meta.bbox.top = obj_meta.rect_params.top
                    msg_meta.bbox.left = obj_meta.rect_params.left
                    msg_meta.bbox.width = obj_meta.rect_params.width
                    msg_meta.bbox.height = obj_meta.rect_params.height
                    msg_meta.frameId = frame_number
                    #msg_meta.trackingId = long_to_uint64(obj_meta.object_id)
                    msg_meta.trackingId = frame_number

                    msg_meta.confidence = obj_meta.confidence
                    msg_meta = generate_event_msg_meta(msg_meta, obj_meta.class_id)

                    user_event_meta.user_meta_data = msg_meta
                    user_event_meta.base_meta.meta_type = pyds.NvDsMetaType.NVDS_EVENT_MSG_META
                    pyds.nvds_add_user_meta_to_frame(frame_meta,
                                                     user_event_meta)
                    print("attaching event meta to buffer")
                else:
                    print("Error in attaching event meta to buffer\n")

                is_first_object = False
            try:
                l_obj = l_obj.next
            except StopIteration:
                break
        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    print("Frame Number =", frame_number, "cars Count =",
          obj_counter[PGIE_CLASS_ID_CAR], "truck Count =",
          obj_counter[PGIE_CLASS_ID_TRUCK])
    return Gst.PadProbeReturn.OK
