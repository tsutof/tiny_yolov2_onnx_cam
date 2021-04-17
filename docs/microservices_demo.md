# Microservices Demo

## Prerequisites

- NVIDIA Jetson Nano Developer Kit
- USB Web Camera or Raspberry Pi Camera V2
- NVIDIA JetPack **4.4 or later**
- docker-compose with the **runtime** option support

## Usage

### Starting Services
```
$ git clone https://github.com/tsutof/tiny_yolov2_onnx_cam

$ cd tiny_yolov2_onnx_cam

$ chmod +x ./scripts/*.sh

$ ./scripts/compose-up.sh
```

At the first launch, the docker image building takes about 30min.

### Access to Dashboard
You can access to the Node-RED dashboard at [http://localhost:1880/ui](http://localhost:1880/ui)

### Stopping Sevices
```
$ ./scripts/compose-down.sh
```

## How to Install docker-compose with the runtime Option Support
The versions of docker-compose can be installed with apt install on L4T, don't support the **runtime** option, but you need the option support to run L4T based docker containers.
Here is an example to install the recent versions of docker-compose which supports the runtime option.

If you already have pip installed with apt in your Jetson. Remove it.
```
$ sudo apt remove python3-pip
```

*[Return to README](../README.md)*
