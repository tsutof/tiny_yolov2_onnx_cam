# Docker Support

## Building the Docker Image

1. Clone the repository if you don't have it yet.
```
$ git clone https://github.com/tsutof/tiny_yolov2_onnx_cam

$ cd tiny_yolov2_onnx_cam
```
2. Add execution permission to the scripts.
```
$ chmod +x ./scripts/*.sh
```
3. Since this demo need much processor cycles, set the power model to the mode 0 and clock up.
```
$ sudo nvpmodel -m 0

$ sudo jetson_clocks
```
4. Build the docker image.
```
$ ./scripts/docker_build.sh
```

## Running a Docker Container from the Built Image

```
$ ./scripts/docker_run.sh
```
The **docker_run.sh** script is an example. Please change it as your need. The script assumes the **/dev/video0** camera device for the input.

The following command starts the application.
Press ESC key to exit from the application.

```
# python3 tiny_yolov2_onnx_cam.py [-h] [--camera CAMERA_NUM] [--csi]
                               [--width WIDTH] [--height HEIGHT]
                               [--objth OBJ_THRESH] [--nmsth NMS_THRESH]

optional arguments:
  -h, --help            show this help message and exit
  --camera CAMERA_NUM, -c CAMERA_NUM
                        Camera number
  --csi                 Use CSI camera
  --width WIDTH         Capture width
  --height HEIGHT       Capture height
  --objth OBJ_THRESH    Threshold of object confidence score (between 0 and 1)
  --nmsth NMS_THRESH    Threshold of NMS algorithm (between 0 and 1)
```

To exit from the docker container
```
# exit
```

*[Return to README](../README.md)*
