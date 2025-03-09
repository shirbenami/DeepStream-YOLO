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
MUXER_BATCH_TIMEOUT_USEC = 33000

# Input and Configuration Paths
INPUT_FILE = "/workspace/deepstream/deepstream_project/data/images/cars_cut2.h264"
SCHEMA_TYPE = 0
PROTO_LIB = "/opt/nvidia/deepstream/deepstream-7.1/lib/libnvds_amqp_proto.so"
CONN_STR="localhost;5672;guest"
CFG_FILE = "/workspace/deepstream/deepstream_project/configs/cfg_amqp.txt"
TOPIC = "topicname"
NO_DISPLAY = False

# Inference Configuration Files
PGIE_CONFIG_FILE = "/workspace/deepstream/deepstream_project/configs/config_infer_primary_yoloV8.txt"
MSCONV_CONFIG_FILE = "/workspace/deepstream/deepstream_project/configs/msgconv_config.txt"

# Class names
PGIE_CLASSES_STR = ["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck"]
CLASS_NAMES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    4: "airplane",
    5: "bus",
    6: "train",
    7: "truck"
}

