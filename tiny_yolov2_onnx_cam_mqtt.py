#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2021 Tsutomu Furuse
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import print_function

from data_processing import PostprocessYOLO
#from get_engine import get_engine
import cv2
import numpy as np
import tensorrt as trt

TRT_VERSION = trt.__version__.split('.')
print('TensorRT v{} detected.'.format(trt.__version__))
TRT_MAJOR = int(TRT_VERSION[0])
if TRT_MAJOR >= 8:
    from get_engine import get_engine
    print('Using the new version of get_engine')
else:
    from get_engine_prev import get_engine
    print('Using the previous version of get_engine')

import pycuda.autoinit
import os
import common
import time
import argparse
import paho.mqtt.client as mqtt
import tiny_yolov2_onnx_cam as appbase

def on_connect(client, userdata, flag, rc):
    print("Connected with result code " + str(rc))

def on_disconnect(client, userdata, flag, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_publish(client, userdata, mid):
    print("publish: {0}".format(mid))

def init_mqtt(host, port=1883):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    #client.on_publish = on_publish
    client.connect(host, port, 60)
    client.loop_start()
    return client

def publish_bboxes(client, topic, frame_num, \
    image, bboxes, confidences, categories, all_categories):
    for box, score, category in zip(bboxes, confidences, categories):
        x_coord, y_coord, width, height = box
        img_height, img_width, _ = image.shape
        left = max(0, np.floor(x_coord + 0.5).astype(int))
        top = max(0, np.floor(y_coord + 0.5).astype(int))
        right = min(img_width, np.floor(x_coord + width + 0.5).astype(int))
        bottom = min(img_height, np.floor(y_coord + height + 0.5).astype(int))
        info = '{0},{1},{2:.2f},{3},{4},{5},{6}'.format(
            frame_num,
            all_categories[category],
            score,
            left,
            top,
            right,
            bottom
        )
        print(info)
        if client is not None:
            client.publish(topic, info)

# Main function
def main():
    # Parse the command line parameters
    parser = argparse.ArgumentParser(description='Tiny YOLO v2 Object Detector')
    parser.add_argument('--camera', '-c', \
        type=int, default=0, metavar='CAMERA_NUM', \
        help='Camera number')
    parser.add_argument('--csi', \
        action='store_true', \
        help='Use CSI camera')
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
    parser.add_argument('--host', \
        type=str, default='localhost', metavar='MQTT_HOST', \
        help='MQTT remote broker IP address')
    parser.add_argument('--topic', \
        type=str, metavar='MQTT_TOPIC', \
        help='MQTT topic to be published on')
    parser.add_argument('--port', \
        type=int, default=1883, metavar='MQTT_PORT', \
        help='MQTT port number')
    parser.add_argument('--novout', \
        action='store_true', \
        help='No video output')
    args = parser.parse_args()

    client = None
    if args.topic is not None:
        client = init_mqtt(args.host, args.port)

    if args.csi or (args.camera < 0):
        if args.camera < 0:
            args.camera = 0
        # Open the MIPI-CSI camera
        gst_cmd = appbase.GST_STR_CSI \
            % (args.width, args.height, appbase.FPS, args.camera, args.width, args.height)
        cap = cv2.VideoCapture(gst_cmd, cv2.CAP_GSTREAMER)
    else:
        # Open the V4L2 camera
        cap = cv2.VideoCapture(args.camera)
        # Set the capture parameters
        #cap.set(cv2.CAP_PROP_FPS, FPS)     # Comment-out for OpenCV 4.1
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    # Get the actual frame size
    # OpenCV 4.1 does not get the correct frame size
    #act_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    #act_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    act_width = args.width
    act_height = args.height
    frame_info = 'Frame:%dx%d' %  (act_width, act_height)

    # Download the label data
    categories = appbase.download_label()

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
        "yolo_input_resolution": appbase.INPUT_RES,
        # Number of object classes
        "num_categories": len(categories)}
    postprocessor = PostprocessYOLO(**postprocessor_args)

    # Image shape expected by the post-processing
    output_shapes = [(1, 125, 13, 13)]

    # Download the Tiny YOLO v2 ONNX model
    onnx_file_path = appbase.download_model()

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

        print('video capture started')

        try:
            while True:
                # Get the frame start time for FPS calculation
                start_time = time.time()

                # Capture a frame
                ret, img = cap.read()
                if ret != True:
                    continue

                # Reshape the capture image for Tiny YOLO v2
                rs_img = cv2.resize(img, appbase.INPUT_RES)
                rs_img = cv2.cvtColor(rs_img, cv2.COLOR_BGRA2RGB)
                src_img = appbase.reshape_image(rs_img)

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

                if boxes is not None:
                    publish_bboxes(client, args.topic, frame_count, \
                        img, boxes, scores, classes, categories)

                if not args.novout:
                    # Draw the bounding boxes
                    if boxes is not None:
                        appbase.draw_bboxes(img, boxes, scores, classes, categories)
                    if frame_count > 10:
                        fps_info = '{0}{1:.2f}'.format('FPS:', fps)
                        msg = '%s %s' % (frame_info, fps_info)
                        appbase.draw_message(img, msg)

                    # Show the results
                    cv2.imshow(appbase.WINDOW_NAME, img)

                    # Check if ESC key is pressed to terminate this application
                    key = cv2.waitKey(20)
                    if key == 27: # ESC
                        break

                    # Check if the window was closed
                    if cv2.getWindowProperty(appbase.WINDOW_NAME, cv2.WND_PROP_AUTOSIZE) < 0:
                        break

                # Calculate the average FPS value of the last ten frames
                elapsed_time = time.time() - start_time
                time_list = np.append(time_list, elapsed_time)
                time_list = np.delete(time_list, 0)
                avg_time = np.average(time_list)
                fps = 1.0 / avg_time

                frame_count += 1

        except KeyboardInterrupt:
            print('exitting..')

    # Release the capture object
    cap.release()

    if not args.novout:
        cv2.destroyAllWindows()

    if client is not None:
        client.disconnect()

if __name__ == "__main__":
    main()
