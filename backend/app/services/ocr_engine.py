from paddleocr import PaddleOCR
import numpy as np
import cv2
import logging
import os
import paddle

# 1. 环境配置
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
logging.getLogger("ppocr").setLevel(logging.ERROR)

class OCREngine:
    def __init__(self):
        self.gpu_available = False
        try:
            if paddle.device.is_compiled_with_cuda():
                self.gpu_available = True
                print(f"✅ 检测到 GPU: {paddle.device.get_device()}")
        except:
            pass

        # 初始化主模型
        print("⏳ 正在加载 OCR 主模型 (v2.9.1 黄金版)...")
        self.ocr_model = self._init_model(use_gpu=self.gpu_available)
        self.current_mode = 'gpu' if self.gpu_available else 'cpu'

    def _init_model(self, use_gpu):
        """适配 PaddleOCR v2.9.1 (支持 use_gpu 参数)"""
        try:
            mode_str = "GPU" if use_gpu else "CPU"
            print(f"   - 尝试加载模式: {mode_str} ...")
            
            return PaddleOCR(
                use_angle_cls=True, 
                lang="ch", 
                use_gpu=use_gpu,    
                show_log=False,     
                use_mp=True if use_gpu else False 
            )
        except Exception as e:
            print(f"   - {mode_str} 模式加载失败: {e}")
            if use_gpu:
                print("   - 🔄 自动降级到 CPU 模式...")
                return self._init_model(use_gpu=False)
            raise e

    def resize_image(self, img):
        """保留手写细节的高清压缩"""
        h, w = img.shape[:2]
        max_side = 2500
        if max(h, w) > max_side:
            scale = max_side / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        return img

    def extract_text(self, file_bytes: bytes) -> str:
        # 解码
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("CV2无法解码图像")

        optimized_img = self.resize_image(img)

        # 🔄 执行识别
        try:
            result = self._run_ocr_safe(optimized_img)
        except Exception as e:
            print(f"❌ OCR 运行出错: {e}")
            raise e
        
        # 结果解析
        raw_text_list = []
        if not result:
            return "" 
            
        page_result = result[0] if isinstance(result, list) and len(result) > 0 else []
        
        if page_result:
            for line in page_result:
                if isinstance(line, list) and len(line) >= 2:
                    content = line[1]
                    if isinstance(content, tuple) and len(content) > 0:
                        raw_text_list.append(content[0])
        
        return "\n".join(raw_text_list)

    def _run_ocr_safe(self, img):
        """双保险执行器"""
        result = self.ocr_model.ocr(img, cls=True)
        
        # 判定是否静默失败
        is_empty_result = (
            result is None or 
            len(result) == 0 or 
            (len(result) > 0 and result[0] is None)
        )

        if is_empty_result and self.current_mode == 'gpu':
            print("⚠️ 警告：GPU 模式返回空结果。")
            print("🔄 正在强制切换到 CPU 模式重试...")
            self.ocr_model = self._init_model(use_gpu=False)
            self.current_mode = 'cpu'
            result = self.ocr_model.ocr(img, cls=True)
            print(f"✅ CPU 重试完成")

        return result

# 实例化对象
ocr_engine = OCREngine()