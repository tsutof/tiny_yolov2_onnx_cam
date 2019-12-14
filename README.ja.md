# tiny_yolov2_onnx_cam
**NVIDIA TensorRT で高速化された Tiny YOLO v2 推論アプリケーション**

*Read this in [English](README.md)*

<img src="./screenshot.png" alt="Screenshot" title="Screenshot" width="640" height="360">

## このアプリケーションが行うこと

YOLO v2 モデルを [Open Neural Network eXchange (ONNX) Model Zoo](https://github.com/onnx/models) からダウンロードし、それを NVIDIA TensorRT 用モデルへ変換します。さらにそのモデルによりカメラに映った物体の検出を行います。

## 前提とする環境

- NVIDIA Jetson Nano 開発者キット
- USB ウェブカメラ または Raspberry Pi Camera V2
- NVIDIA JetPack 4.2.1 以降

## インストール方法

1. 依存ライブラリをインストールします。

    ```
    $ sudo apt update

    $ sudo apt install python3-pip protobuf-compiler libprotoc-dev libjpeg-dev cmake
    ```

1. 他の Python モジュールをインストールする前に、**Cython** モジュールをインストールします。これを行わないと次のステップで行う NumPy インストール時に **RuntimeError: Running cythonize failed!** エラーが発生する場合があります。

    ```
    $ pip3 install --user cython
    ```

1. 本アプリケーションと依存モジュールをインストールします。

    ```
    $ git clone https://github.com/tsutof/tiny_yolov2_onnx_cam

    $ cd tiny_yolov2_onnx_cam

    $ export PATH=$PATH:/usr/local/cuda/bin

    $ python3 -m pip install -r requirements.txt
    ```

## 実行方法

最初に Jetson のクロックアップを行います。これを行わないと、ビデオ・キャプチャー時に *select timeout* が発生します。

```
$ sudo nvpmodel -m 0
$ sudo jetson_clocks
```

本アプリケーションは以下のコマンドで実行します。
終了するには ESC キーを押します。

```
$ python3 tiny_yolov2_onnx_cam.py [-h] [--camera CAMERA_NUM] [--width WIDTH]
                                  [--height HEIGHT] [--objth OBJ_THRESH]
                                  [--nmsth NMS_THRESH]

optional arguments:
  -h, --help            show this help message and exit
  --camera CAMERA_NUM, -c CAMERA_NUM
                        Camera number, use any negative integer for MIPI-CSI camera
  --width WIDTH         Capture width
  --height HEIGHT       Capture height
  --objth OBJ_THRESH    Threshold of object confidence score (between 0 and 1)
  --nmsth NMS_THRESH    Threshold of NMS algorithm (between 0 and 1)
```

Raspberry Pi camera v2 などの CSI カメラを利用する場合はカメラナンバーに任意の負数を指定します。

```
$ python3 tiny_yolov2_onnx_cam.py --camera -1
```

USB ウェブカメラを利用する場合はそのデバイスナンバーを指定します。/dev/video0 と認識されているカメラは 0 を、/dev/video1 と認識されているカメラは 1 を指定します。

```
$ python3 tiny_yolov2_onnx_cam.py --camera 1
```

## サードパーティ・ライセンス

本プログラムは以下の条件でライセンスされるオープンソースを利用しています。

```
#
# Copyright 1993-2019 NVIDIA Corporation.  All rights reserved.
#
# NOTICE TO LICENSEE:
#
# This source code and/or documentation ("Licensed Deliverables") are
# subject to NVIDIA intellectual property rights under U.S. and
# international Copyright laws.
#
# These Licensed Deliverables contained herein is PROPRIETARY and
# CONFIDENTIAL to NVIDIA and is being provided under the terms and
# conditions of a form of NVIDIA software license agreement by and
# between NVIDIA and Licensee ("License Agreement") or electronically
# accepted by Licensee.  Notwithstanding any terms or conditions to
# the contrary in the License Agreement, reproduction or disclosure
# of the Licensed Deliverables to any third party without the express
# written consent of NVIDIA is prohibited.
#
# NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
# LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
# SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  IT IS
# PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
# NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
# DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
# NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
# NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
# LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
# SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THESE LICENSED DELIVERABLES.
#
# U.S. Government End Users.  These Licensed Deliverables are a
# "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
# 1995), consisting of "commercial computer software" and "commercial
# computer software documentation" as such terms are used in 48
# C.F.R. 12.212 (SEPT 1995) and is provided to the U.S. Government
# only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
# 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
# U.S. Government End Users acquire the Licensed Deliverables with
# only those rights set forth herein.
#
# Any use of the Licensed Deliverables in individual and commercial
# software must include, in the user documentation and internal
# comments to the code, the above Disclaimer and U.S. Government End
# Users Notice.
#
```
