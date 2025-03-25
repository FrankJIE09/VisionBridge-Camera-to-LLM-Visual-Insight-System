import socket
import os
import sys
import cv2
# 注意：请确保 initialize_all_connected_cameras 函数已正确定义并导入
from orbbec_camera import initialize_all_connected_cameras

class SocketServer:
    def __init__(self, host='127.0.0.1', port=6666):
        self.host = host
        self.port = port
        self.client_socket = None  # 客户端socket
        self.client_address = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

    def start(self):
        print("Waiting for connection...")
        while True:
            self.client_socket, self.client_address = self.server_socket.accept()
            print(f"Connection established with {self.client_address}")
            self.handle_client(self.client_socket)

    def handle_client(self, client_socket):
        try:
            msg_type, payload = self.receive_message(client_socket)
            if msg_type is None:
                print("没有接收到数据")
                return
            print(f"接收到数据，类型: {msg_type}, 内容: {payload if msg_type not in ['IMG ', 'DEP '] else '<二进制数据>'}")
            # 根据接收到的命令判断处理逻辑
            if msg_type.strip() == "CMD":
                command = payload.decode('utf-8')
                if command == "get_image":
                    self.send_one_image(client_socket)
                else:
                    self.send_message(client_socket, "TXT ", b"Unknown command")
            else:
                self.send_message(client_socket, "TXT ", b"Unknown command")
        except Exception as e:
            print(f"处理客户端时出错: {e}")
        finally:
            client_socket.close()
            print("连接已关闭")

    def recvall(self, sock, n):
        """确保从socket中接收n个字节数据"""
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def receive_message(self, client_socket):
        """
        按协议接收消息：
        1. 先接收12字节报文头（前4字节为类型，后8字节为数据长度）
        2. 根据长度接收数据体
        """
        header = self.recvall(client_socket, 12)
        if not header:
            return None, None
        msg_type = header[:4].decode('utf-8')
        try:
            length = int(header[4:12].decode('utf-8'))
        except ValueError:
            print("解析数据长度出错")
            return None, None
        payload = self.recvall(client_socket, length)
        return msg_type, payload

    def send_message(self, client_socket, msg_type, payload):
        """
        按协议发送消息：
        - msg_type：字符串，如"CMD ", "TXT ", "IMG "（确保长度为4）
        - payload：字节数据
        """
        length = len(payload)
        length_str = str(length).zfill(8)
        header = msg_type.encode('utf-8')[:4] + length_str.encode('utf-8')
        message = header + payload
        try:
            client_socket.sendall(message)
        except Exception as e:
            print(f"发送数据出错: {e}")

    def send_one_image(self, client_socket):
        """
        获取相机图像并发送一张图片给客户端
        """
        cameras = initialize_all_connected_cameras('CP1Z842000DM')
        if len(cameras) == 0:
            print("没有连接相机")
            self.send_message(client_socket, "TXT ", b"No cameras connected")
            return

        # 仅获取第一台相机的颜色图像
        camera = cameras[0]
        color_image, depth_image, depth_frame = camera.get_frames()

        # 对颜色图像进行JPEG编码
        ret, color_buf = cv2.imencode('.jpg', color_image)
        if not ret:
            print("颜色图编码失败")
            self.send_message(client_socket, "TXT ", b"Image encoding failed")
            return
        color_data = color_buf.tobytes()

        # 发送图片数据，消息类型为 "IMG "
        self.send_message(client_socket, "IMG ", color_data)
        print("已发送一张图片")

if __name__ == "__main__":
    print("进程启动，电源开启")
    server = SocketServer()
    server.start()
