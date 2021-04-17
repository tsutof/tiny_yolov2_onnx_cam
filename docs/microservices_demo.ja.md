# マイクロサービス・デモ

<img src="./services.png" alt="Services" title="Services" width="640">

本デモはEclipse Mosquitto™をMQTTブローカーとして利用、Node-REDをダッシュボードとして利用しています。

## 前提する環境

- NVIDIA Jetson Nano開発者キット
- USBウェブカメラ、または、Raspberry Pi Camera V2
- NVIDIA JetPack **4.4 または、それ以降のバージョン**
- **runtime** オプションがサポートされたdocker-compose [（この項目を参照）](#runtime%E3%82%AA%E3%83%97%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%8C%E3%82%B5%E3%83%9D%E3%83%BC%E3%83%88%E3%81%95%E3%82%8C%E3%81%9Fdocker-compose%E3%82%92%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95)

## 実行方法

### サービスの起動
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
4. サービスを起動
```
$ ./scripts/compose-up.sh
```
**最初の起動時に、Dockerイメージのビルドに約30分を要します。**

### ダッシュボードへアクセス
[http://localhost:1880/ui](http://localhost:1880/ui) からダッシュボードへアクセスできます。
<img src="./dashboard.png" alt="Dashboard" title="Dashboard" width="640">

### サービスの停止（別のターミナルから）
```
$ ./scripts/compose-down.sh
```

## runtimeオプションがサポートされたdocker-composeをインストールする方法
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

*[README.jaへ戻る](../README.ja.md)*
