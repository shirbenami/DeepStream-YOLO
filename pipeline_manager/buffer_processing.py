import pyds
from gi.repository import Gst
from configs.constants import PGIE_CLASS_ID_PERSON,OUTPUT_FOLDER_JSON,PGIE_CLASSES_STR,CLASS_NAMES,PGIE_CLASS_ID_BICYCLE,PGIE_CLASS_ID_CAR,PGIE_CLASS_ID_MOTORCYCLE,PGIE_CLASS_ID_AIRPLANE,PGIE_CLASS_ID_AIRPLANE,PGIE_CLASS_ID_BUS,PGIE_CLASS_ID_TRAIN,PGIE_CLASS_ID_TRUCK
from pipeline_manager.event_metadata import generate_event_msg_meta
import json 
import os 
from datetime import datetime



def osd_sink_pad_buffer_probe(pad, info, u_data):

    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    #image_name = f"frame_{timestamp}"
    image_path = u_data
    image_name = os.path.basename(image_path)
    image_name_no_ext = os.path.splitext(image_name)[0]  

    obj_counter = {i: 0 for i in range(len(PGIE_CLASSES_STR))}

    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return Gst.PadProbeReturn.OK
    
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    if not batch_meta:
        return Gst.PadProbeReturn.OK
    
    l_frame = batch_meta.frame_meta_list

    while l_frame is not None:

        frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        frame_number = frame_meta.frame_num
        
        detections = []

        l_obj = frame_meta.obj_meta_list

        while l_obj is not None:

            obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)

            rect = obj_meta.rect_params
            bbox = {
                "x_min": rect.left,
                "y_min": rect.top,
                "x_max": rect.left + rect.width,
                "y_max": rect.top + rect.height
            }

            detections.append({
                "class_id": obj_meta.class_id,
                "class_name": PGIE_CLASSES_STR[obj_meta.class_id],
                "confidence": obj_meta.confidence,
                "bounding_box": bbox
            })

            # Update the object text display
            txt_params = obj_meta.text_params

            # Set display_text. Any existing display_text string will be
            # freed by the bindings module.
            txt_params.display_text = PGIE_CLASSES_STR[obj_meta.class_id]

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

            user_event_meta = pyds.nvds_acquire_user_meta_from_pool(batch_meta)
            if user_event_meta:
                msg_meta = pyds.alloc_nvds_event_msg_meta(user_event_meta)
                msg_meta.trackingId = frame_number
                msg_meta.confidence = obj_meta.confidence
                msg_meta = generate_event_msg_meta(msg_meta, obj_meta.class_id)
                msg_meta.bbox.top = obj_meta.rect_params.top
                msg_meta.bbox.left = obj_meta.rect_params.left
                msg_meta.bbox.width = obj_meta.rect_params.width
                msg_meta.bbox.height = obj_meta.rect_params.height
                user_event_meta.user_meta_data = msg_meta
                user_event_meta.base_meta.meta_type = pyds.NvDsMetaType.NVDS_EVENT_MSG_META
                pyds.nvds_add_user_meta_to_frame(frame_meta, user_event_meta)

                print("Attached custom JSON message to frame")
            else:
                print("Failed to allocate user meta")


            l_obj = l_obj.next


        
        frame_dict = {
            "image_name": image_name,
            "image_size": {
                "width": frame_meta.source_frame_width,
                "height": frame_meta.source_frame_height
            },
            "detections": detections
        }

        os.makedirs(OUTPUT_FOLDER_JSON,exist_ok=True)
        json_path = os.path.join(OUTPUT_FOLDER_JSON,f"{image_name_no_ext}.json")
        with open(json_path, "w") as f:
            json.dump(frame_dict, f, indent=4)

        print(f"📄 Saved JSON: {json_path}")


        
        l_frame = l_frame.next

 
    return Gst.PadProbeReturn.OK


