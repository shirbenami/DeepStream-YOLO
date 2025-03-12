# Display and timestamp limits
MAX_DISPLAY_LEN = 64
MAX_TIME_STAMP_LEN = 32

# Define class IDs for different objects
PGIE_CLASS_ID_PERSON = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_CAR = 2
PGIE_CLASS_ID_MOTORCYCLE = 3
PGIE_CLASS_ID_AIRPLANE = 4
PGIE_CLASS_ID_BUS = 5
PGIE_CLASS_ID_TRAIN = 6
PGIE_CLASS_ID_TRUCK = 7

# Muxer properties
MUXER_OUTPUT_WIDTH = 1920
MUXER_OUTPUT_HEIGHT = 1080
MUXER_BATCH_TIMEOUT_USEC = 50000

# Input and Configuration Paths
#INPUT_FILE = "/workspace/deepstream/deepstream_project/data/videos/cars_cut2.h264" #video file
#INPUT_FILE = "/workspace/deepstream/deepstream_project/data/images/cars.jpg" #image file
#INPUT_FOLDER = "/workspace/deepstream/deepstream_project/data/images/" # folder of images
INPUT_FOLDER = "/workspace/deepstream/deepstream_project/data/videos_h264/" # folder of videos


SCHEMA_TYPE = 0
PROTO_LIB = "/opt/nvidia/deepstream/deepstream-7.1/lib/libnvds_amqp_proto.so"
CONN_STR="localhost;5672;guest"
CFG_FILE = "/workspace/deepstream/deepstream_project/configs/cfg_amqp.txt"
TOPIC = "topicname"
NO_DISPLAY = False
OUTPUT_FOLDER = "/workspace/deepstream/deepstream_project/output/"

# Inference Configuration Files
PGIE_CONFIG_FILE = "/workspace/deepstream/deepstream_project/configs/config_infer_primary_yoloV8.txt"
MSCONV_CONFIG_FILE = "/workspace/deepstream/deepstream_project/configs/msgconv_config.txt"
PREPROCESS_CONFIG = "/workspace/deepstream/deepstream_project/configs/nvdspreprocess_config.txt"


# Class names list
PGIE_CLASSES_STR = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
    "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
    "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", 
    "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl",
    "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza",
    "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table", "toilet",
    "tv", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven",
    "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
    "hair drier", "toothbrush"
]

# Class dictionary mapping class ID to name
CLASS_NAMES = {i: PGIE_CLASSES_STR[i] for i in range(len(PGIE_CLASSES_STR))}

