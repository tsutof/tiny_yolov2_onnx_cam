# tiny_yolov2_onnx_cam
**NVIDIA TensorRT で高速化された Tiny YOLO v2 推論アプリケーション**

*Read this in [English](README.md)*

<img src="./screenshot.png" alt="Screenshot" title="Screenshot" width="640" height="360">

## 目次
- [このアプリケーションが行うこと](#%E3%81%93%E3%81%AE%E3%82%A2%E3%83%97%E3%83%AA%E3%82%B1%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%8C%E8%A1%8C%E3%81%86%E3%81%93%E3%81%A8)
- [前提とする環境](#%E5%89%8D%E6%8F%90%E3%81%A8%E3%81%99%E3%82%8B%E7%92%B0%E5%A2%83)
- [インストール方法](#%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E6%96%B9%E6%B3%95)
- [実行方法](#%E5%AE%9F%E8%A1%8C%E6%96%B9%E6%B3%95)
- [Dockerサポート](docs/docker.ja.md)
- [MQTTサポート](docs/mqtt.ja.md)
- [マイクロサービス・デモ](docs/microservices_demo.ja.md)
  （「Jetson Nano 超入門 改訂 第2版 9-4 Dockerを利用したデプロイメント」で紹介）
- [サードパーティ・ライセンス](#%E3%82%B5%E3%83%BC%E3%83%89%E3%83%91%E3%83%BC%E3%83%86%E3%82%A3%E3%83%A9%E3%82%A4%E3%82%BB%E3%83%B3%E3%82%B9)

## このアプリケーションが行うこと

YOLO v2 モデルを [Open Neural Network eXchange (ONNX) Model Zoo](https://github.com/onnx/models) からダウンロードし、それを NVIDIA TensorRT 用モデルへ変換します。さらにそのモデルによりカメラに映った物体の検出を行います。

## 前提とする環境

- NVIDIA Jetson Nano 開発者キット
- USB ウェブカメラ または Raspberry Pi カメラモジュール V2
- NVIDIA JetPack 4.2.1 以降

## インストール方法

1. 依存ライブラリをインストールします。

    ```
    sudo apt update
    ```
    ```
    sudo apt install python3-pip protobuf-compiler libprotoc-dev libjpeg-dev cmake libcanberra-gtk-module libcanberra-gtk3-module
    ```

1. いくつかの Python モジュールはインストール順序に制約があります。

    ```
    pip3 install --user --upgrade setuptools wheel Cython
    ```
    ```
    pip3 install --user numpy protobuf==3.16.0
    ```
    ```
    pip3 install --user --no-deps "onnx>=1.6.0,<=1.11.0"
    ```

1. 本アプリケーションと依存モジュールをインストールします。

    ```
    git clone https://github.com/tsutof/tiny_yolov2_onnx_cam
    ```
    ```
    cd tiny_yolov2_onnx_cam
    ```
    ```
    export PATH=$PATH:/usr/local/cuda/bin
    ```
    ```
    python3 -m pip install --user -r requirements.txt
    ```

## 実行方法

最初に Jetson のクロックアップを行います。これを行わないと、ビデオ・キャプチャー時に *select timeout* が発生します。

```
sudo nvpmodel -m 0
```
```
sudo jetson_clocks
```

本アプリケーションは以下のコマンドで実行します。
終了するには ESC キーを押します。

```
python3 tiny_yolov2_onnx_cam.py [-h] [--camera CAMERA_NUM] [--csi]
                               [--width WIDTH] [--height HEIGHT]
                               [--objth OBJ_THRESH] [--nmsth NMS_THRESH]

optional arguments:
  -h, --help            ヘルプメッセージを表示し、終了
  --camera CAMERA_NUM, -c CAMERA_NUM
                        カメラナンバー
  --csi                 CSIカメラ利用時にセット
  --width WIDTH         カメラキャプチャー幅
  --height HEIGHT       カメラキャプチャー高
  --objth OBJ_THRESH    オブジェクト検出のスコア閾値（0 ～ 1）
  --nmsth NMS_THRESH    NMS（非最大値の抑制）アルゴリズムの閾値（0 ～ 1）
```

Raspberry Pi camera v2 などの CSI カメラを利用する場合は **--csi** オプションを付けます。

```
python3 tiny_yolov2_onnx_cam.py --csi --camera 0
```

USB ウェブカメラを利用する場合はそのデバイスナンバーを指定します。/dev/video0 と認識されているカメラは 0 を、/dev/video1 と認識されているカメラは 1 を指定します。

```
python3 tiny_yolov2_onnx_cam.py --camera 1
```

**お使いの USB ウェブカメラがこのアプリケーションのデフォルト解像度設定に対応しない場合は、--width と --height コマンドライン・オプションでキャプチャ解像度を変更してください。**

お使いのカメラがサポートする解像度は、**gst-device-monitor-1.0** コマンドで取得できます。

## Dockerサポート

*[このページを参照](docs/docker.ja.md)*

## MQTTサポート

*[このページを参照](docs/mqtt.ja.md)*

## マイクロサービス・デモ

*[このページを参照](docs/microservices_demo.ja.md)*

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
