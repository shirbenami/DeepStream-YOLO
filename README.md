# DeepStream Setup Guide

## Project Description
This project provides a comprehensive guide to setting up and running NVIDIA DeepStream with Triton Inference Server for video analytics. The goal is to utilize DeepStream's GPU-accelerated pipelines for video processing, leveraging machine learning models to perform object detection and classification.

The guide walks through the process of downloading and configuring the DeepStream Docker image, modifying configuration files, and running experiments on video files. By following these steps, users can create a containerized environment capable of processing video streams and outputting results with object detection overlays.

Key highlights include:
- Downloading the DeepStream Docker image (version 6.0.1 with Triton support)
- Saving and committing changes to Docker containers
- Running DeepStream applications in Docker
- Configuring video input and output parameters
- Verifying GPU availability and DeepStream environment
- Running experiments and validating output

This project is designed for developers and engineers working with NVIDIA GPUs, focusing on deploying AI-powered video analytics solutions.

---

## Step 1: Download the DeepStream Docker Image
To download the DeepStream Docker image with Triton Inference Server support, run the following command:
```bash
docker pull nvcr.io/nvidia/deepstream:6.0.1-triton
or
docker pull nvcr.io/nvidia/deepstream:7.1-gc-triton-devel
```
**Explanation:**
- This command pulls the DeepStream version 6.0.1 image from NVIDIA's repository.
- The Triton Inference Server is included for enhanced model serving capabilities.

---

## Saving Changes to the Container
Once you’ve made changes inside the container, you can save them by creating a new Docker image.

### 1. Find the Container ID or Name
To list all running containers, use:
```bash
docker ps
```

### 2. Save the Container as a New Image
Use the `docker commit` command to save the container's current state:
```bash
docker commit <container_id_or_name> <new_image_name>:<tag>
```
**Example:**
```bash
docker commit shir_container shir_with_onnx_installed
```
- `shir_container` – The container you were working on.
- `shir_with_onnx_installed` – The name of the new image that includes ONNX installation.

### 3. Verify the New Image
Check if the new image was created successfully:
```bash
docker images
```

### 4. Exit the Running Container
If you are still inside the container, exit by typing:
```bash
exit
```

---

## Step 2: Running the DeepStream Docker Container
To start the container and access the DeepStream workspace, use the following command:
```bash
docker run -it --gpus all \
-v /home/user1/shir/ssl_project:/workspace/ssl_project \
shir_deepstream7.1:1 /bin/bash
```
or:

```bash
docker run --gpus all -it --net=host --privileged -v /home/user1/shir/ssl_project:/workspace/ssl_project -e DISPLAY=$DISPLAY -w /opt/nvidia/deepstream/deepstream-7.1 nvcr.io/nvidia/deepstream:7.1-gc-triton-devel
```

**Explanation:**
- `-it` – Interactive mode to allow terminal interaction.
- `--gpus all` – Grants access to all GPUs on the system.
- `-v` – Mounts the local directory to the container (`/workspace/ssl_project`).
- `/bin/bash` – Opens a bash shell inside the container.

---

## Step 3: Verify the DeepStream Environment
### 1. Check NVIDIA GPU
Run the following inside the container:
```bash
nvidia-smi
```
**Expected Result:**
- GPU details, CUDA version, and memory usage should be displayed.

### 2. Check DeepStream Version
Verify the installed DeepStream version by running:
```bash
deepstream-app --version-all
```

---

## Step 4: Prepare Configuration Files
### 1. Navigate to Configuration Directory
Inside the container, go to the DeepStream sample configuration directory:
```bash
cd /opt/nvidia/deepstream/deepstream-6.0/samples/configs/deepstream-app
```

### 2. Copy the Sample Configuration File
Create a copy of the existing configuration file to customize:
```bash
cp source1_usb_dec_infer_resnet_int8.txt source1_usb_dec_infer_resnet_int8_copy.txt
```

### 3. Edit the Configuration File
Open the copied file for editing:
```bash
nano source1_usb_dec_infer_resnet_int8_copy.txt
```

---

## Step 5: Modify the Configuration File
### 1. Update Input Source
Replace the `[source0]` section with the following to set the video input:
```ini
[source0]
enable=1
type=3
uri=file:///workspace/ssl_project/images/cars_cut.mp4
num-sources=1
gpu-id=0
cudadec-memtype=0
```

### 2. Update Output Settings
Replace the `[sink0]` section to configure the output:
```ini
[sink0]
enable=1
type=3
container=2  # MP4 container
codec=1      # H.264 codec
sync=0
output-file=/workspace/ssl_project/output/output_video.mp4
```

### 3. Verify Model Paths
Ensure the `[primary-gie]` section points to the correct model paths:
```ini
[primary-gie]
enable=1
model-engine-file=/opt/nvidia/deepstream/deepstream-5.1/samples/models/Primary_Detector/resnet10.engine
batch-size=1
bbox-border-color0=1;0;0;1
bbox-border-color1=0;1;1;1
config-file=config_infer_primary.txt
```

---

## Step 6: Run the Experiment
Execute the DeepStream application using the modified configuration file:
```bash
deepstream-app -c source1_usb_dec_infer_resnet_int8_copy.txt
```

---

## Step 7: Check the Results
### 1. Verify the Output File
After running the experiment, check if the output video is saved:
```bash
ls /workspace/ssl_project/output/output_video.mp4
```

### 2. Play the Output Video
Use a media player (like VLC) to review the detection results in the video.



---



# Guide for train YOLO Model

### 1. Project Setup

*  go to deepstream6.1/sources/ . follow this directions: https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/blob/master/HOWTO.md

* pip3 install this link https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/releases

after this download the Yolo directory:

```bash
cd /opt/nvidia/deepstream/deepstream-6.0/samples/configs/deepstream-app
```
1. Clone the DeepStream-Yolo repository:
```bash
git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps
git clone https://github.com/marcoslucianops/DeepStream-Yolo.git
cd DeepStream-Yolo
```
2. Build the custom parser:
```bash
cd nvdsinfer_custom_impl_Yolo
make clean && make
```
**If there is an issue:**

modify Makefile:
```
CUDA_VER?=12.2
#ifeq ($(CUDA_VER),)
#       $(error "CUDA_VER is not set")
#endif
```

** example of use in : /opt/nvidia/deepstream/deepstream-7.1/sources/deepstream_python_apps/apps
you can run:
```
python3 deepstream_test_4.py -i /workspace/ssl_project/images/cars_cut2.h264 -p '/opt/nvidia/deepstream/deepstream-7.1/lib/libnvds_amqp_proto.so' --conn-str="localhost;5672;guest" -c "cfg_amqp.txt" --topic "topicname"

```

### 3. Configure YOLOv8
Edit the YOLOv8 configuration file: 

```
nano config_infer_primary_yoloV8.txt
```

```
[property]
gpu-id=0
net-scale-factor=0.0039215697906911373
onnx-file=yolov8s.pt.onnx
labelfile-path=/opt/nvidia/deepstream/deepstream-5.1/samples/configs/deepstream-app/DeepStream-Yolo/labels.txt
model-engine-file=model_b1_gpu0_fp32.engine
num-detected-classes=80
```
Run application:
```bash
deepstream-app -c deepstream_app_config_YOLO8.txt
```

Run "pipeline_nvmconv.py" :
```bash
python3 pipeline_nvmconv.py /workspace/ssl_project/images/cars_cut2.h264
```

---


links:
https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_docker_containers.html
https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/tree/9bffad1aea802f6be4419712c0a50f05d6a2d490/bindings#21-base-dependencies
https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/tree/master

**End of Guide**

