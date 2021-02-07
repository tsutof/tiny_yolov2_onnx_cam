#!/bin/sh

cp /etc/apt/sources.list.d/nvidia-l4t-apt-source.list .
cp /etc/apt/trusted.gpg.d/jetson-ota-public.asc .

sudo docker build --no-cache -t tiny_yolov2_onnx_cam:l4t-r32.5.0 .
