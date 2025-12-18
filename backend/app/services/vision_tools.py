import cv2
import numpy as np
import base64

class VisionTools:
    @staticmethod
    def extract_red_seal(file_bytes: bytes) -> bytes:
        """
        核心算法：从图片二进制流中提取红色印章，并返回透明背景的 PNG 二进制流
        """
        # 1. 将二进制流转换为 OpenCV 图像格式
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("无法解析图像文件")

        # 2. 转换颜色空间：BGR -> HSV (色相、饱和度、亮度)
        # HSV 更适合根据颜色提取物体
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 3. 定义红色的范围 (红色在 HSV 色环的 0度和180度附近)
        # 范围1：0-10度 (红)
        lower_red1 = np.array([0, 43, 46])
        upper_red1 = np.array([10, 255, 255])
        
        # 范围2：156-180度 (紫红)
        lower_red2 = np.array([156, 43, 46])
        upper_red2 = np.array([180, 255, 255])

        # 4. 生成掩膜 (Mask) - 只有红色的地方是白色的，其他地方是黑色的
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2 # 合并两个红色区间

        # 5. 图像平滑与降噪 (腐蚀与膨胀) - 去除噪点，让印章主体更饱满
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # 6. 构建带有 Alpha (透明) 通道的输出图像
        # 先把原图分离成 B, G, R 三个通道
        b, g, r = cv2.split(img)
        
        # 将 mask 作为 Alpha 通道：
        # mask 中白色的部分(255) -> 不透明
        # mask 中黑色的部分(0) -> 全透明
        rgba = cv2.merge([b, g, r, mask])

        # 7. 编码回 PNG 格式 (PNG 支持透明背景)
        success, encoded_img = cv2.imencode(".png", rgba)
        if not success:
            raise ValueError("图像编码失败")
            
        return encoded_img.tobytes()

vision_service = VisionTools()