# Microservices Demo

<img src="./services.png" alt="Services" title="Services" width="640">

This demo uses Eclipse Mosquitto™ for the MQTT broker and uses Node-RED for the dashboard.

## Prerequisites

- NVIDIA Jetson Nano Developer Kit
- USB Web Camera or Raspberry Pi Camera V2
- NVIDIA JetPack **4.4 or later**
- docker-compose with the **runtime** option support [(see this section)](#how-to-install-docker-compose-with-the-runtime-option-support)

## Usage

### Starting Services
1. Clone the repository if you don't have it yet.
```
$ git clone https://github.com/tsutof/tiny_yolov2_onnx_cam
```
2. Add execution permission to the scripts.
```
$ cd tiny_yolov2_onnx_cam

$ chmod +x ./scripts/*.sh
```
3. Since this demo need much processor cycles, set the power model to the mode 0 and clock up.
```
$ sudo nvpmodel -m 0

$ sudo jetson_clocks
```
4. Start the services. (For CSI camera, modify docker-compose.yml prior to execute this command. See [this note](#csi-camera).)
```
$ ./scripts/compose-up.sh
```
**At the first launch, the docker image building takes about 30min.**

#### CSI Camera
If you use a CSI camera like Raspberry Pi camera v2, add the **--csi** option to the application at the last line of [docker-compose.yml](../docker-compose.yml).
```
command: python3 tiny_yolov2_onnx_cam_mqtt.py --topic tiny_yolov2_onnx_cam --novout --csi
```

### Access to Dashboard
You can access to the Node-RED dashboard at [http://localhost:1880/ui](http://localhost:1880/ui)
<img src="./dashboard.png" alt="Dashboard" title="Dashboard" width="640">

### Stopping Sevices
```
$ ./scripts/compose-down.sh
```

## How to Install docker-compose with the runtime Option Support
At this time, the versions of docker-compose can be installed with apt install on L4T, don't support the **runtime** option, but you need the option support to run L4T based docker containers.
Here is an example to install the recent versions of docker-compose which supports the runtime option.

1. If you already have pip installed with apt in your Jetson. Remove it.
```
$ sudo apt remove python3-pip
```
2. Install pip from PyPA
```
$ sudo apt update
$ sudo apt install curl python3-testresources
$ curl -kL https://bootstrap.pypa.io/get-pip.py | python3
```
3. Install docker-compose
```
$ python3 -m pip install --user docker-compose
```
4. Add $HOME/.local/bin directory in your PATH.
5. Comfirm docker-compose installed successfully.
```
docker-compose --version
```

*[Return to README](../README.md)*
