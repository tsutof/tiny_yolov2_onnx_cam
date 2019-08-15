#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import argparse

FPS = 30
GST_STR_CSI = 'nvarguscamerasrc \
    ! video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, format=(string)NV12, framerate=(fraction)%d/1 \
    ! nvvidconv ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx \
    ! videoconvert \
    ! appsink'
WINDOW_NAME = 'Tiny YOLO v2'
INPUT_RES = (416, 416)
MODEL_URL = 'https://onnxzoo.blob.core.windows.net/models/opset_8/tiny_yolov2/tiny_yolov2.tar.gz'
LABEL_URL = 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/voc.names'

# Draw bounding boxes on the screen from the YOLO inference result
def draw_bboxes(image, bboxes, confidences, categories, all_categories, message=None):
    for box, score, category in zip(bboxes, confidences, categories):
        x_coord, y_coord, width, height = box
        img_height, img_width, _ = image.shape
        left = max(0, np.floor(x_coord + 0.5).astype(int))
        top = max(0, np.floor(y_coord + 0.5).astype(int))
        right = min(img_width, np.floor(x_coord + width + 0.5).astype(int))
        bottom = min(img_height, np.floor(y_coord + height + 0.5).astype(int))
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
    # Parse the command line parameters
    parser = argparse.ArgumentParser(description='Tiny YOLO v2 Object Detector')
    parser.add_argument('--camera', '-c', \
        type=int, default=0, metavar='CAMERA_NUM', \
        help='Camera number, use any negative integer for MIPI-CSI camera')
    parser.add_argument('--width', \
        type=int, default=1280, metavar='WIDTH', \
        help='Capture width')
    parser.add_argument('--height', \
        type=int, default=720, metavar='HEIGHT', \
        help='Capture height')
    parser.add_argument('--objth', \
        type=float, default=0.6, metavar='OBJ_THRESH', \
        help='Threshold of object confidence score (between 0 and 1)')
    parser.add_argument('--nmsth', \
        type=float, default=0.3, metavar='NMS_THRESH', \
        help='Threshold of NMS algorithm (between 0 and 1)')
    args = parser.parse_args()

    if args.camera < 0:
        # Open the MIPI-CSI camera
        gst_cmd = GST_STR_CSI \
            % (args.width, args.height, FPS, args.width, args.height)
        cap = cv2.VideoCapture(gst_cmd, cv2.CAP_GSTREAMER)
    else:
        # Open the V4L2 camera
        cap = cv2.VideoCapture(args.camera)
        # Set the capture parameters
        cap.set(cv2.CAP_PROP_FPS, FPS)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    # Get the actual frame size
    act_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    act_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_info = 'Frame:%dx%d' %  (act_width, act_height)

    # Download the label data
    categories = download_label()

    # Configure the post-processing
    postprocessor_args = {
        # YOLO masks (Tiny YOLO v2 has only single scale.)
        "yolo_masks": [(0, 1, 2, 3, 4)],
        # YOLO anchors
        "yolo_anchors": [(1.08, 1.19), (3.42, 4.41), (6.63, 11.38), (9.42, 5.11), (16.62, 10.52)],
        # Threshold of object confidence score (between 0 and 1)
        "obj_threshold": args.objth,
        # Threshold of NMS algorithm (between 0 and 1)
        "nms_threshold": args.nmsth,
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
                = postprocessor.process(trt_outputs, (act_width, act_height))

            # Draw the bounding boxes
            if boxes is not None:
                draw_bboxes(img, boxes, scores, classes, categories)
            if frame_count > 10:
                fps_info = '{0}{1:.2f}'.format('FPS:', fps)
                msg = '%s %s' % (frame_info, fps_info)
                draw_message(img, msg)

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
