#
# Copyright (c) 2019 Tsutomu Furuse
#

from __future__ import print_function

from data_processing import PostprocessYOLO, load_label_categories
from get_engine import get_engine
import cv2
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import sys
import os
import common
import wget
import tarfile
import time

FPS = 30
#ORG_RES = (1080, 1080)
ORG_RES = (720, 720)
GST_STR_CSI = 'nvarguscamerasrc \
    ! video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=(fraction)%d/1 \
    ! nvvidconv ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx \
    ! videoconvert \
    ! appsink' \
    % (FPS, ORG_RES[0], ORG_RES[1])
WINDOW_NAME = 'Tiny YOLO v2'
INPUT_RES = (416, 416)
MODEL_URL = 'https://onnxzoo.blob.core.windows.net/models/opset_8/tiny_yolov2/tiny_yolov2.tar.gz'
LABEL_URL = 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/voc.names'

# Draw bounding boxes on the screen from the YOLO inference result
def draw_bboxes(image, bboxes, confidences, categories, all_categories, message=None):
    for box, score, category in zip(bboxes, confidences, categories):
        x_coord, y_coord, width, height = box
        left = max(0, np.floor(x_coord + 0.5).astype(int))
        top = max(0, np.floor(y_coord + 0.5).astype(int))
        right = min(ORG_RES[0], np.floor(x_coord + width + 0.5).astype(int))
        bottom = min(ORG_RES[1], np.floor(y_coord + height + 0.5).astype(int))
        cv2.rectangle(image, \
            (left, top), (right, bottom), (0, 0, 255), 3)
        info = '{0} {1:.2f}'.format(all_categories[category], score)
        cv2.putText(image, info, (right, top), \
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
        print(info)
    if message is not None:
        cv2.putText(image, message, (32, 32), \
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)

# Draw the message on the screen
def draw_message(image, message):
    cv2.putText(image, message, (32, 32), \
        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)

# Reshape the image from OpneCV to Tiny YOLO v2
def reshape_image(img):
    # Convert 8-bit integer to 32-bit floating point
    img = img.astype(np.float32)
    # Convert HWC to CHW
    img = np.transpose(img, [2, 0, 1])
    # Convert CHW to NCHW
    img = np.expand_dims(img, axis=0)
    # Convert to row-major
    img = np.array(img, dtype=np.float32, order='C')
    return img

# Download file from the URL if it doesn't exist yet.
def download_file_from_url(url):
    file = os.path.basename(url)
    if not os.path.exists(file):
        print('\nDownload from %s' % url)
        wget.download(url)
    return (file)

# Download the label file if it doesn't exist yet.
def download_label():
    file = download_file_from_url(LABEL_URL)
    categories = load_label_categories(file)
    num_categories = len(categories)
    assert(num_categories == 20)
    return (categories)

# Download the Tiny YOLO v2 ONNX model file and extract it
# if it doesn't exist yet.
def download_model():
    file = download_file_from_url(MODEL_URL)
    base, _ = os.path.splitext(file)
    ext_dir_name, _ = os.path.splitext(base)
    if os.path.isdir(ext_dir_name) == False:
        tar = tarfile.open(file)
        tar.extractall()
        tar.close()
    onnx_file = None
    for f in os.listdir(ext_dir_name):
        _, ext = os.path.splitext(f)
        if ext == '.onnx':
            onnx_file = os.path.join(ext_dir_name, f)
    return (onnx_file)

# Main function
def main():
    # Obtain the camera number form the command line
    # Negative number means MIPI-CSI camera (e.g. Raspberry-Pi camera v2).
    args = sys.argv
    cam = 0
    if len(args) <= 1:
        cam = 0
    elif (int(args[1]) < 0):
        cam = -1
    else:
        cam = int(args[1])

    cap = None
    if cam < 0:
        # Open the MIPI-CSI camera
        cap = cv2.VideoCapture(GST_STR_CSI, cv2.CAP_GSTREAMER)
    else:
        # Open the V4L2 camera
        cap = cv2.VideoCapture(cam)
        # Set the capture parameters
        cap.set(cv2.CAP_PROP_FPS, FPS)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, ORG_RES[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ORG_RES[1])

    # Download the label data
    categories = download_label()

    # Configure the post-processing
    postprocessor_args = {
        # YOLO masks (Tiny YOLO v2 has only single scale.)
        "yolo_masks": [(0, 1, 2, 3, 4)],
        # YOLO anchors
        "yolo_anchors": [(1.08, 1.19), (3.42, 4.41), (6.63, 11.38), (9.42, 5.11), (16.62, 10.52)],
        # Threshold of object confidence score (between 0 and 1)
        "obj_threshold": 0.6,
        # Threshold of NMS algorithm (between 0 and 1)
        "nms_threshold": 0.3,
        # Input image resolution
        "yolo_input_resolution": INPUT_RES,
        # Number of object classes
        "num_categories": len(categories)}
    postprocessor = PostprocessYOLO(**postprocessor_args)

    # Image shape expected by the post-processing
    output_shapes = [(1, 125, 13, 13)]

    # Download the Tiny YOLO v2 ONNX model
    onnx_file_path = download_model()

    # Define the file name of local saved TensorRT plan
    engine_file_path = 'model.trt'

    time_list = np.zeros(10)

    # Load the model into TensorRT
    with get_engine(onnx_file_path, engine_file_path) as engine, \
        engine.create_execution_context() as context:

        # Allocate buffer memory for TensorRT
        inputs, outputs, bindings, stream = common.allocate_buffers(engine)

        fps = 0.0
        frame_count = 0

        while True:
            # Get the frame start time for FPS calculation
            start_time = time.time()

            # Capture a frame
            ret, img = cap.read()
            if ret != True:
                continue

            # Reshape the capture image for Tiny YOLO v2
            rs_img = cv2.resize(img, INPUT_RES)
            rs_img = cv2.cvtColor(rs_img, cv2.COLOR_BGRA2RGB)
            src_img = reshape_image(rs_img)

            # Execute an inference in TensorRT
            inputs[0].host = src_img
            trt_outputs = common.do_inference(context, bindings=bindings, \
                inputs=inputs, outputs=outputs, stream=stream)

            # Reshape the network output for the post-processing
            trt_outputs = [output.reshape(shape) \
                for output, shape in zip(trt_outputs, output_shapes)]

            # Calculates the bounding boxes
            boxes, classes, scores \
                = postprocessor.process(trt_outputs, ORG_RES)

            # Draw the bounding boxes
            if boxes is not None and frame_count > 10 :
                fps_info = '{0} {1:.2f}'.format('FPS:', fps)
                draw_bboxes(img, boxes, scores, classes, categories, fps_info)

            # Show the results
            cv2.imshow(WINDOW_NAME, img)

            # Check if ESC key is pressed to terminate this application
            key = cv2.waitKey(20)
            if key == 27: # ESC
                break

            # Calculate the average FPS value of the last ten frames
            elapsed_time = time.time() - start_time
            time_list = np.append(time_list, elapsed_time)
            time_list = np.delete(time_list, 0)
            avg_time = np.average(time_list)
            fps = 1.0 / avg_time

            frame_count += 1

    # Release the capture object
    cap.release()

if __name__ == "__main__":
    main()
