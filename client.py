import socket
import cv2
import numpy as np
from ollama_api import OllamaClient  # 导入封装好的类


def recvall(sock, n):
    """确保从 socket 中接收 n 个字节数据"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def receive_message(sock):
    """
    按协议接收消息：
    1. 先接收 12 字节报文头（前 4 字节为类型，后 8 字节为数据长度）
    2. 根据长度接收数据体
    """
    header = recvall(sock, 12)
    if not header:
        return None, None
    msg_type = header[:4].decode('utf-8')
    try:
        length = int(header[4:12].decode('utf-8'))
    except ValueError:
        print("解析数据长度出错")
        return None, None
    payload = recvall(sock, length)
    return msg_type, payload


def send_message(sock, msg_type, payload):
    """
    按协议发送消息：
    - msg_type：字符串，如 "CMD ", "TXT ", "IMG "（确保为 4 字节）
    - payload：字节数据
    """
    length = len(payload)
    length_str = str(length).zfill(8)
    header = msg_type.encode('utf-8')[:4] + length_str.encode('utf-8')
    message = header + payload
    sock.sendall(message)


def main():
    server_ip = '127.0.0.1'
    server_port = 6666

    # 建立 TCP 连接
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    print(f"已连接到服务器 {server_ip}:{server_port}")

    # 发送 "get_image" 命令给服务器
    send_message(sock, "CMD ", b"get_image")
    print("已发送获取图片命令: get_image")

    # 接收服务器返回的图片数据
    msg_type, payload = receive_message(sock)
    if msg_type is None:
        print("未收到数据")
    else:
        if msg_type == "IMG ":
            # 将收到的图片数据解码为图像
            nparr = np.frombuffer(payload, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is not None:
                save_path = "received_image.jpg"
                cv2.imwrite(save_path, image)
                print(f"图片已保存到: {save_path}")

                # 使用 OllamaClient 类调用 Ollama 接口进行图片解析，直接传入 prompt 参数
                client = OllamaClient()
                result = client.generate_from_image(save_path, prompt="中文描述图中的内容")
                print("图片解析结果:")
                print(result)
            else:
                print("图片解码失败")
        elif msg_type.strip() == "TXT":
            text = payload.decode('utf-8')
            print("文本消息:", text)
        else:
            print("未知数据类型:", msg_type)
    sock.close()


if __name__ == "__main__":
    main()
