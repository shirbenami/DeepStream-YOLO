from optparse import OptionParser

def parse_args():
    """Parses and validates command-line arguments."""
    parser = OptionParser()
    parser.add_option("-c", "--cfg-file", dest="cfg_file",
                      help="Set the adaptor config file. Optional if "
                           "connection string has relevant details.",
                      metavar="FILE")
    parser.add_option("-i", "--input-file", dest="input_file",
                      help="Set the input H264 file", metavar="FILE")
    parser.add_option("-p", "--proto-lib", dest="proto_lib",
                      help="Absolute path of adaptor library", metavar="PATH")
    parser.add_option("", "--conn-str", dest="conn_str",
                      help="Connection string of backend server. Optional if "
                           "it is part of config file.", metavar="STR")
    parser.add_option("-s", "--schema-type", dest="schema_type", default="0",
                      help="Type of message schema (0=Full, 1=minimal), "
                           "default=0", metavar="<0|1>")
    parser.add_option("-t", "--topic", dest="topic",
                      help="Name of message topic. Optional if it is part of "
                           "connection string or config file.", metavar="TOPIC")
    parser.add_option("", "--no-display", action="store_true",
                      dest="no_display", default=False,
                      help="Disable display")

    (options, args) = parser.parse_args()

    if not (options.proto_lib and options.input_file):
        print("Usage: python3 deepstream_test_4.py -i <H264 filename> -p "
              "<Proto adaptor library> --conn-str=<Connection string>")
        return None

    # Return parsed arguments as a dictionary
    return {
        "cfg_file": options.cfg_file,
        "input_file": options.input_file,
        "proto_lib": options.proto_lib,
        "conn_str": options.conn_str,
        "topic": options.topic,
        "schema_type": 0 if options.schema_type == "0" else 1,
        "no_display": options.no_display
    }
