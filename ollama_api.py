import requests
import json
import base64


class OllamaClient:
    def __init__(self, url="http://localhost:11434/api/generate", model="gemma3:4b"):
        """
        初始化 OllamaClient

        参数:
          url: Ollama 服务的 API 地址
          model: 使用的模型名称
        """
        self.url = url
        self.model = model
        self.headers = {
            "Content-Type": "application/json"
        }

    def generate_from_image(self, image_path=None, prompt="中文描述图中的内容"):
        """
        根据指定图片和 prompt 生成结果
        如果没有传入 image_path，则请求体中不包含 images 字段

        参数:
          image_path: 本地图片路径，若为 None 则不传图片
          prompt: 描述图片内容的提示文本

        返回:
          模型生成的结果字符串，如果请求失败则返回 None
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
        }

        # 如果提供了 image_path，则读取图片并添加 images 字段
        if image_path:
            try:
                with open(image_path, "rb") as f:
                    img_bytes = f.read()
            except Exception as e:
                print(f"读取图片失败: {e}")
                return None

            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            payload["images"] = [img_b64]

        # 发送 POST 请求，使用 stream=True 以流式处理返回数据
        response = requests.post(self.url, headers=self.headers, json=payload, stream=True)

        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print("返回内容:", response.text)
            return None

        # 逐行读取并拼接返回的 response 字段
        result_str = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:  # 跳过空行
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    print("JSON解析错误:", e)
                    continue

                part = data.get("response", "")
                result_str += part

                if data.get("done", False) is True:
                    break

        return result_str


if __name__ == "__main__":
    # 测试用：如果存在图片，则传入图片路径，否则调用时不传图片
    client = OllamaClient()
    # 测试带图片：如果存在 "received_image.jpg"，则传入图片路径
    result = client.generate_from_image("received_image.jpg", prompt="中文描述图中的内容")
    print("最终输出结果：")
    print(result)

    # 测试不带图片：
    # result = client.generate_from_image(prompt="中文描述图中的内容")
    # print("最终输出结果：")
    # print(result)
