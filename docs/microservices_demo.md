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

At the first launch, the docker image build takes about 30min.

### Access to Dashboard
You can access to the Node-RED dashboard at [http://localhost:1880/ui](http://localhost:1880/ui)

### Stopping Sevices
```
$ ./scripts/compose-down.sh
```

## docker-compose with the runtime option support

```

```

*[Return to README](../README.md)*
