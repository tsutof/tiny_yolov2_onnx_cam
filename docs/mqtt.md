# MQTT Support (Experimental)

## Usage

```
# python3 tiny_yolov2_onnx_cam_mqtt.py [-h] [--camera CAMERA_NUM] [--csi]
                                    [--width WIDTH] [--height HEIGHT]
                                    [--objth OBJ_THRESH] [--nmsth NMS_THRESH]
                                    [--host MQTT_HOST] [--topic MQTT_TOPIC]
                                    [--port MQTT_PORT] [--novout]
Tiny YOLO v2 Object Detector
optional arguments:
  -h, --help            show this help message and exit
  --camera CAMERA_NUM, -c CAMERA_NUM
                        Camera number
  --csi                 Use CSI camera
  --width WIDTH         Capture width
  --height HEIGHT       Capture height
  --objth OBJ_THRESH    Threshold of object confidence score (between 0 and 1)
  --nmsth NMS_THRESH    Threshold of NMS algorithm (between 0 and 1)
  --host MQTT_HOST      MQTT remote broker IP address (Default: localhost)
  --topic MQTT_TOPIC    MQTT topic to be published on
  --port MQTT_PORT      MQTT port number (Default: 1883)
  --novout              No video output
```

## Data Format

Comma separated text.

1. Frame number
1. Class
1. Score
1. Bounding box x_min
1. Bounding box y_min
1. Bounding box x_max
1. Bounding box y_max

### Examples

```
2312,tvmonitor,0.61,480,4,627,176
2312,person,0.60,82,103,547,480
```

*[Return to README](../README.md)*
