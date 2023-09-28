# logo-qrcode

A simple Python library for generating QR codes with logo

---



### 一、直接拷贝脚本文件使用

`logo_qrcode.py -data http://www.google.com -logo logo.png -save qecode.png`

![www.google.com](https://raw.githubusercontent.com/hellofan1998/logo_qrcode/main/tests/google.png)

## 二、使用 pip 安装

`pip install logo-qrcode`

### 查看帮助

使用 `pip install logo-qrcode` 安装成功可以直接使用 `cli` 工具使用

`logo-qrcode-cli -h`

或

`python3 -m logo_qrcode -h`

### 使用 logo-qrcode-cli

使用 `pip install logo-qrcode` 安装成功可以直接使用 `cli` 工具

`logo-qrcode-cli -data http://www.baidu.com -logo logo.png -save qecode.png`

使用 `--base64` 直接在控制台输出图片 `base64`
`logo-qrcode-cli -data http://www.baidu.com -logo logo.png --base64`
