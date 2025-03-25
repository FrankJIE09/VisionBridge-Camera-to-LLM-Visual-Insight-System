import os
import cv2
import base64
import requests
import json


class OllamaClient:
    def __init__(self, url="http://localhost:11434/api/generate", model="gemma3:4b"):
        self.url = url
        self.model = model
        self.headers = {"Content-Type": "application/json"}

    def generate_from_image_bytes(self, img_bytes, prompt="描述图像内容"):
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [img_b64]

        }

        response = requests.post(self.url, headers=self.headers, json=payload, stream=True)
        if response.status_code != 200:
            print(f"请求失败: {response.status_code}")
            return None

        result_str = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    data = json.loads(line)
                    result_str += data.get("response", "")
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
        return result_str


def extract_frames_from_video(video_path, output_folder, interval=30):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ 无法打开视频")
        return []

    frame_paths = []
    frame_count = 0
    saved_count = 0

    print("📽️ 正在从视频中抽帧...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % interval == 0:
            frame_filename = f"frame_{saved_count:03d}.jpg"
            frame_path = os.path.join(output_folder, frame_filename)
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            print(f"✅ 已保存帧: {frame_filename}")
            saved_count += 1
        frame_count += 1

    cap.release()
    print(f"🎉 抽帧完成，共保存 {saved_count} 张图像")
    return frame_paths


def run_inference_on_images(image_paths, client, prompt="请描述画面内容"):
    results = []
    for idx, img_path in enumerate(image_paths):
        try:
            with open(img_path, "rb") as f:
                img_bytes = f.read()
        except Exception as e:
            print(f"❌ 读取失败: {img_path}, 错误: {e}")
            continue

        print(f"🖼️ 正在识别第 {idx + 1} 张图像: {os.path.basename(img_path)}")
        result = client.generate_from_image_bytes(img_bytes, prompt)
        print("🧠 识别结果:", result)
        print("-" * 50)
        results.append((img_path, result))
    return results


def save_results(results, output_file="results.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for path, result in results:
            f.write(f"【{os.path.basename(path)}】\n{result}\n\n")
    print(f"📄 结果已保存至 {output_file}")


if __name__ == "__main__":
    # 参数设置
    video_path = "orbbec_output.mp4"        # 输入视频路径
    image_folder = "images"                 # 抽帧保存目录
    frame_interval = 10                     # 每隔多少帧抽取一张
    prompt_text = "请用中文描述视频帧的内容"

    # 执行流程
    image_paths = extract_frames_from_video(video_path, image_folder, interval=frame_interval)
    client = OllamaClient()
    results = run_inference_on_images(image_paths, client, prompt=prompt_text)
    save_results(results, output_file="results.txt")
