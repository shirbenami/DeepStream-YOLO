# DeepStream Setup Guide

## Project Description
This project provides a comprehensive guide to setting up and running NVIDIA DeepStream with Triton Inference Server for video analytics. The goal is to utilize DeepStream's GPU-accelerated pipelines for video processing, leveraging machine learning models to perform object detection and classification.

The guide walks through the process of downloading and configuring the DeepStream Docker image, modifying configuration files, and running experiments on video files. By following these steps, users can create a containerized environment capable of processing video streams and outputting results with object detection overlays.

Key highlights include:
- Downloading the DeepStream Docker image (version 7.1.1 with Triton support)
- Saving and committing changes to Docker containers
- Running DeepStream applications in Docker
- Configuring video input and output parameters
- Verifying GPU availability and DeepStream environment
- Running experiments and validating output

This project is designed for developers and engineers working with NVIDIA GPUs, focusing on deploying AI-powered video analytics solutions.

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

before run: 
```bash
xhost +local:docker
```
run:

```bash
docker run --gpus all -it --net=host --privileged -v /home/user/shir/deepstream:/workspace/deepstream -e DISPLAY=$DISPLAY shir:4
```

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


# Guide for train YOLO Model

### 1. Project Setup

```bash
cd /opt/nvidia/deepstream/deepstream-7.1/samples/configs/deepstream-app/DeepStream-Yolo
```

you can run:
```
python3 main.py -i /workspace/deepstream/images/cars_cut2.h264 -p '/opt/nvidia/deepstream/deepstream-7.1/lib/libnvds_amqp_proto.so' --conn-str="localhost;5672;guest" -c "cfg_amqp.txt" --topic "topicname"

```


# Setting Up AMQP Protocol Adapter for DeepStream

This guide provides step-by-step instructions to set up the AMQP protocol adapter for DeepStream using RabbitMQ. Follow the steps carefully to configure RabbitMQ, create users, queues, and integrate with DeepStream.

## Prerequisites
- RabbitMQ installed and running.
- Access to RabbitMQ Management Interface (default: http://localhost:15672).
- Credentials for RabbitMQ (default: guest/guest or user-defined).

---

## Step 1: Install RabbitMQ

### Using a Package Manager
```bash
sudo apt-get install rabbitmq-server
```

### Check RabbitMQ Status
```bash
sudo service rabbitmq-server status
```

### Start RabbitMQ
```bash
sudo service rabbitmq-server start
```

### Enable RabbitMQ Management Plugin
```bash
sudo rabbitmq-plugins enable rabbitmq_management
```

---

## Step 2: Access RabbitMQ Management Interface
1. Open a browser and navigate to [http://localhost:15672](http://localhost:15672).
2. Log in using the default credentials (guest/guest) or previously configured credentials.

---

## Step 3: Create a RabbitMQ User and Queue

### Create a New User
1. Log in to RabbitMQ locally or within the container.
2. Execute the following commands to add a user and grant necessary permissions:

```bash
rabbitmqctl add_user myuser mypassword
rabbitmqctl set_user_tags myuser administrator
rabbitmqctl set_permissions -p / myuser ".*" ".*" ".*"
```

### Create a Queue
1. Go to the **Queues** tab in the RabbitMQ Management Interface.
2. Add a queue named `test_queue`.

---

## Step 4: Create an Exchange and Bind to Queue
1. Navigate to the **Exchanges** tab in RabbitMQ Management Interface.
2. Create or use an existing exchange (e.g., `amq.topic`).
3. Add a binding to link the `test_queue` with the exchange.
4. In the Routing key write : topicname
![image](https://github.com/user-attachments/assets/d00b0045-9fa8-45ad-b926-c827b8391989)

---

## Step 5: Verify Queue and Exchange Setup
Run the following commands to verify the queue and exchange bindings:

### List Queues
```bash
rabbitmqctl list_queues
```

### List Bindings
```bash
rabbitmqctl list_bindings
```

Expected output:
```
Listing bindings:
exchange    test_queue    queue    test_queue    []
amq.topic   exchange      test_queue    queue    topicname    []
```

If the bindings are missing, restart RabbitMQ:
```bash
sudo rabbitmqctl stop_app
sudo rabbitmqctl start_app
```

---


## Additional Notes
- Ensure RabbitMQ is configured correctly for external connections if not running locally.
- Use secure credentials for production environments.
- To clean (or purge) messages from a queue in RabbitMQ:
  ```
   rabbitmqctl purge_queue test_queue
  ```

For further details, refer to the [DeepStream Plugin Guide](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_plugin_gst-nvmsgbroker.html).


---


links:
https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_docker_containers.html
https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/tree/9bffad1aea802f6be4419712c0a50f05d6a2d490/bindings#21-base-dependencies
https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/tree/master
https://www.fosslinux.com/6339/how-to-install-rabbitmq-server-on-ubuntu-18-04-lts.htm

**End of Guide**

