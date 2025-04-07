# DeepStream Vehicle Detection & Metadata Publisher


## Project Description
This project uses NVIDIA DeepStream SDK to perform object detection on images and videos using the YOLOv8 model. 
The model used was trained with **YOLOv11** on the **AITOD dataset**, which is specifically designed for **vehicle detection in aerial imagery**. 
The pipeline processes one frame at a time, extracts metadata for all detected objects, and publishes a single JSON message per frame to RabbitMQ containing all bounding boxes and labels.


## Pipeline Structure
---
![newgif](https://github.com/user-attachments/assets/17118b7e-009d-4bf4-b3f5-7d9891526018)
---

The pipeline follows these key stages:

1. **Source Input (GstFileSrc)** - Loads an image or video from a file located in:
2. **JPEG Parsing (GstJpegParse)** - Parses JPEG image data for processing.
3. **Decoder (nvv4l2decoder)** - It is decoded using NVIDIA NVDEC.
4. **Stream Muxing (GstNvStreamMux)** - Merges multiple streams into a batch for efficient GPU processing.
5. **Inference Engine (GstNvInfer)** - Runs object detection using a deep learning model with configurations.
6. **Video Conversion (Gstnvideoconvert)** - Converts video format for further processing.
7. **On-Screen Display (GstNvDsOsd)** - Overlays bounding boxes and object labels on the video.
8. **Stream Splitting (GstTee)** - Divides the processed stream into three outputs:
   - **Rendering output**
   - **Message conversion for metadata transmission**
   - **Processed data streaming**
9. **Message Conversion & Transmission (GstNvMsgConv & GstNvMsgBroker)** - Converts metadata and sends it via AMQP with GstNvMsgBroker, GstNvMsgConv.
10. **File Output (GstFileSink)** - Saves the images/output in a directory.


## 🚀 Features

- Run YOLOv11 with DeepStream to detect vehicles in aerial videos or images.
- The model is trained on the AITOD dataset, suitable for detecting vehicles from drone or satellite imagery.
- Choose your pipeline type directly from `main.py`, such as:
  - `images`
  - `videos`
  - `pre_process`

- For each frame:
  - Extract all detected objects (bounding box, label, confidence).
  - Save the annotated frame to an output video/images.
  - Send a single RabbitMQ message per frame with all detections.
- Output stored as:
  - Annotated video with bounding boxes.
  - JSON with metadata per frame.

To build a pipeline, the logic is structured such that:
- You choose the pipeline type via `main.py`
- The selected pipeline is implemented in the `pipeline_manager` module.
- All helper functions used to construct the pipeline (e.g., pre-processing, frame handling) are located inside `pipeline_manager/pipeline/`.


## 🛠️ Requirements

- Python 3.8+
- NVIDIA GPU with CUDA support
- DeepStream SDK (6.0 or newer recommended)
- Docker (recommended for easier setup)
- RabbitMQ running locally or remotely

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🧠 How the Pipeline Works

- The `osd_sink_pad_buffer_probe` function is used to hook into each frame as it passes through the pipeline.
- For each frame:
  - All detected objects are collected, including their bounding box, label, and confidence.
  - These are packed into a single dictionary.
  - The dictionary is converted to JSON and published to RabbitMQ using `rabbitmq_publisher.py`.

Sample JSON message sent per frame:

```json
{
  "frame_number": 42,
  "objects": [
    {
      "label": "car",
      "confidence": 0.92,
      "bbox": [120, 200, 80, 60]
    },
    {
      "label": "truck",
      "confidence": 0.88,
      "bbox": [400, 180, 150, 100]
    }
  ]
}
```

## 📦 Output

- videos/images with bounding boxes and labels drawn on each frame.
  ![image](https://github.com/user-attachments/assets/9f4c6452-76fa-49fb-9fba-8ab915745ff0)

- json files: optional copy of all metadata messages saved locally.
  ![image](https://github.com/user-attachments/assets/97149f65-ad6a-4a19-a58c-4541380463a2)

- **RabbitMQ** — all metadata messages are published in real-time per frame.
![image](https://github.com/user-attachments/assets/30c9d5b5-f4d2-492c-ac88-03633154cce3)

---


## Running the DeepStream Docker Container
To start the container and access the DeepStream workspace, use the following command:

before run: 
```bash
xhost +local:docker
```
run:

```bash
docker run --gpus all -it --net=host --privileged -v /home/user/shir/deepstream:/workspace/deepstream -e DISPLAY=$DISPLAY shir:4
```

Output example:



https://github.com/user-attachments/assets/889bc996-8bbe-4b48-9b34-6ff46bc5fb76





## 💡 TODO / Future Work

- Add support for detection of more object classes beyond vehicles.
- Support real-time video streams (e.g., RTSP camera feeds).
- Add support for automatic retraining with newly labeled data.

## links:
https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_docker_containers.html
https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/tree/9bffad1aea802f6be4419712c0a50f05d6a2d490/bindings#21-base-dependencies
https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/tree/master
https://www.fosslinux.com/6339/how-to-install-rabbitmq-server-on-ubuntu-18-04-lts.htm




**End of Guide**

