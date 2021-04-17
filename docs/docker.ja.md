# Dockerサポート

## Dockerイメージのビルド

1. （もし、まだであったら）本リポジトリのクローン
```
$ git clone https://github.com/tsutof/tiny_yolov2_onnx_cam
```
2. シェルスクリプトファイルに実行権限を付与
```
$ cd tiny_yolov2_onnx_cam

$ chmod +x ./scripts/*.sh
```
3. Jetson Nanoの電力モードをモード0にして、クロックアップ
```
$ sudo nvpmodel -m 0

$ sudo jetson_clocks
```
4. Dockerイメージのビルド
```
$ ./scripts/docker_build.sh
```

## ビルドしたDockerイメージからコンテナを起動

```
$ ./scripts/docker_run.sh
```
**docker_run.sh** は例として **/dev/video0** をカメラ入力としていますが、ご使用の環境に合わせて変更してください。

コンテナ内のシェルから、以下のコマンドで本アプリケーションを起動できます。ESCキーでアプリケーションを終了します。

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

**exit** で、コンテナからホストOSに戻ります。
```
# exit
```

*[README.jaに戻る](../README.ja.md)*
