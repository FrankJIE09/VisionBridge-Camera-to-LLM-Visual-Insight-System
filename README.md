
# Camera-to-LLM 图像采集与分析系统

本项目是一个基于 Orbbec 相机采集图像，并通过 Ollama 本地大模型进行图像理解的系统。客户端请求图像，服务器端采集图像后传送给客户端，客户端再通过本地部署的大模型对图像内容进行中文描述。

## 🌟 项目结构

```
├── client.py              # 客户端脚本，请求图像并调用 Ollama 解析
├── server.py              # 服务器端，采集图像并发送至客户端
├── orbbec_camera.py       # Orbbec 相机封装，负责图像获取、对齐、深度处理等
├── ollama_api.py          # 本地 Ollama API 调用封装
├── utils.py               # 图像格式转换工具函数
├── received_image.jpg     # 接收到的图像样例（由 client.py 保存）
```

## ⚙️ 依赖项

请确保你已安装以下依赖：

```bash
pip install opencv-python numpy requests pyyaml matplotlib
```

此外，还需要安装并配置：

- **Ollama** 本地服务（默认地址 `http://localhost:11434`）
- **Orbbec SDK** (`pyorbbecsdk`) 及相机驱动

## 🚀 使用说明

### 启动服务器

```bash
python server.py
```

服务器启动后将监听本地端口 `6666`，等待客户端连接。

### 启动客户端

```bash
python client.py
```

客户端会向服务器发送 `get_image` 命令，接收图像并调用 Ollama 模型进行中文内容生成。

## 🔧 模块说明

### `client.py`
- 与服务器建立 TCP 连接
- 按自定义协议发送命令和接收图像
- 使用 `OllamaClient` 调用本地模型进行图像内容识别

### `server.py`
- 监听客户端连接
- 响应客户端命令，调用相机采集一张图像并发送
- 使用 `initialize_all_connected_cameras` 初始化 Orbbec 相机

### `orbbec_camera.py`
- 封装 Orbbec 相机初始化、对齐、采集逻辑
- 支持自动曝光调节、深度图、外参加载等功能

### `ollama_api.py`
- 封装本地 `Ollama` API 的访问逻辑
- 支持图像+prompt 联合推理

### `utils.py`
- 提供多种视频格式（如 MJPG、YUYV 等）转 BGR 的工具函数
- 支持 OpenCV 显示图像

## 📷 示例图像

`received_image.jpg` 是客户端成功接收到图像并保存的示例。

## 📌 其他说明

- 默认使用相机序列号 `'CP1Z842000DM'`，如有多个相机请修改相关调用逻辑。
- 默认模型为 `gemma3:4b`，请根据实际安装的模型修改 `ollama_api.py` 中的 `model` 字段。
- 图像通信协议为：
  - 报文头：12 字节（4 字节类型 + 8 字节数据长度）
  - 报文体：图像或文本数据

---

欢迎使用与扩展该系统！
```

---

如需将其保存为文件或继续优化，请告诉我，我可以为你自动生成 `README.md` 文件并提供下载。