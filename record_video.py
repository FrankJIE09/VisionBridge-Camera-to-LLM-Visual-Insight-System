import cv2
import time
from orbbec_camera import OrbbecCamera

def record_video(serial_number='CP1Z842000DM', output_file='output.mp4', duration_sec=10, fps=15):
    # 初始化相机
    camera = OrbbecCamera(serial_number)

    # 获取一帧确定图像尺寸
    color_image, _, _ = camera.get_frames()
    height, width, _ = color_image.shape

    # 定义视频编码器和输出对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 保存为 .mp4 格式
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    print(f"开始录制视频：{output_file}，时长：{duration_sec} 秒")
    start_time = time.time()

    try:
        while time.time() - start_time < duration_sec:
            color_image, _, _ = camera.get_frames()
            out.write(color_image)  # 写入视频帧
            cv2.imshow("Recording...", color_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("录制中断")
                break
    finally:
        out.release()
        camera.stop()
        cv2.destroyAllWindows()
        print(f"视频已保存为 {output_file}")

if __name__ == "__main__":
    record_video(
        serial_number='CP1Z842000DM',  # 根据实际设备修改
        output_file='orbbec_output.mp4',
        duration_sec=10,  # 录制时长：10秒
        fps=15
    )
