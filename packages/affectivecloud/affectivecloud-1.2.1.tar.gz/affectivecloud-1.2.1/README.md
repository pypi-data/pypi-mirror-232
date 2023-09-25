# Enter Affective Cloud SDK For PC

## 简介

Enter Affective Cloud SDK For PC 是[回车科技](https://www.entertech.cn/)提供的，适配回车科技蓝牙芯片及情感云平台的 PC 端 SDK。本 SDK 使用 Python 语言开发，可以在 macOS、Linux、Win 下运行。

## 安装

`pip install affectivecloud`

## 功能

1. 接入蓝牙数据（[enterble](https://github.com/Entertech/Enter-Biomodule-BLE-PC-SDK)）
2. 连接情感云服务器
3. 调用情感计算服务
4. 接收情感计算服务数据

## 使用

查看 [examples](https://github.com/Entertech/Enter-AffectiveCloud-PC-SDK/tree/main/examples)

- [simple](https://github.com/Entertech/Enter-AffectiveCloud-PC-SDK/tree/main/examples/simple.py)
- [headband Demo](https://github.com/Entertech/Enter-AffectiveCloud-PC-SDK/tree/main/examples/headband_relatime_demo.py)
- [headband Demo GUI Version](https://github.com/Entertech/Enter-AffectiveCloud-PC-SDK/tree/main/examples/headband_relatime_gui_demo.py)

### 注意

#### 设备相关

每种设备名称(name)会不一样，在使用 Demo 的时候，请使用相应的名称或不指定名称。不指定名称的情况下，会枚举所有相同 UUID 下的设备。

#### 开发环境

SDK 默认支持 >= 3.6,< 3.10 版本的 Python 运行环境；如需 3.10 以上版本使用，请升级 websockets 依赖包为 >= 10.0 版本

#### 环境变量

在使用 Demo 的时候，需要设置环境变量：

`APP_KEY`

`APP_SECRET`

`CLIENT_ID`

详情参考：[认证并创建会话](https://docs.affectivecloud.cn/%F0%9F%8E%99%E6%8E%A5%E5%8F%A3%E5%8D%8F%E8%AE%AE/%E4%BC%9A%E8%AF%9D%E5%8D%8F%E8%AE%AE#%E8%AE%A4%E8%AF%81%E5%B9%B6%E5%88%9B%E5%BB%BA%E5%AF%B9%E8%AF%9D%E7%9A%84-request)
