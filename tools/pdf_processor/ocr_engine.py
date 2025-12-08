"""
OCR文本识别引擎
使用Tesseract对PDF图片进行OCR识别
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import json


class OCREngine:
    def __init__(self, lang: str = 'chi_sim+eng'):
        """
        初始化OCR引擎

        Args:
            lang: 识别语言（chi_sim=简体中文, eng=英文）
        """
        self.lang = lang

        # 检查Tesseract是否安装
        try:
            pytesseract.get_tesseract_version()
            print(f"✅ Tesseract已安装")
        except:
            print("❌ Tesseract未安装！")
            print("macOS安装: brew install tesseract tesseract-lang")
            raise

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        图像预处理（提高OCR准确率）

        Args:
            image_path: 图片路径

        Returns:
            预处理后的图像
        """
        # 读取图像
        img = cv2.imread(image_path)

        # 转灰度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 去噪
        denoised = cv2.fastNlMeansDenoising(gray)

        # 二值化（提高对比度）
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary

    def detect_formula_regions(self, image_path: str) -> List[Dict]:
        """
        检测公式区域（基于数学符号密度）

        Args:
            image_path: 图片路径

        Returns:
            公式区域列表 [{"x": x, "y": y, "w": w, "h": h}, ...]
        """
        # 简化版：返回空列表
        # 完整实现需要训练模型或使用数学符号检测算法
        return []

    def ocr_with_layout(self, image_path: str) -> Dict:
        """
        OCR识别，保留布局信息

        Args:
            image_path: 图片路径

        Returns:
            包含文本和坐标信息的字典
        """
        # 预处理
        processed = self.preprocess_image(image_path)

        # OCR识别（保留位置信息）
        data = pytesseract.image_to_data(
            processed,
            lang=self.lang,
            output_type=pytesseract.Output.DICT
        )

        # 组织结果
        words = []
        n_boxes = len(data['text'])

        for i in range(n_boxes):
            text = data['text'][i].strip()
            if text:  # 忽略空字符串
                words.append({
                    'text': text,
                    'confidence': data['conf'][i],
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i]
                })

        # 简单的文本拼接
        full_text = pytesseract.image_to_string(processed, lang=self.lang)

        return {
            'fullText': full_text,
            'words': words,
            'wordCount': len(words)
        }

    def process_page(self, image_path: str) -> Dict:
        """
        处理单页图片

        Args:
            image_path: 图片路径

        Returns:
            处理结果
        """
        print(f"\n🔍 OCR识别: {Path(image_path).name}")

        # OCR识别
        ocr_result = self.ocr_with_layout(image_path)

        # 检测公式区域
        formula_regions = self.detect_formula_regions(image_path)

        result = {
            'imagePath': image_path,
            'ocrResult': ocr_result,
            'formulaRegions': formula_regions
        }

        print(f"  ✓ 识别到{ocr_result['wordCount']}个词")
        print(f"  ✓ 文本长度: {len(ocr_result['fullText'])}字符")

        return result


def main():
    """示例用法"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python ocr_engine.py <图片路径>")
        return

    image_path = sys.argv[1]

    # 创建OCR引擎
    ocr = OCREngine()

    # 处理图片
    result = ocr.process_page(image_path)

    # 显示结果
    print(f"\n📝 识别结果：")
    print(result['ocrResult']['fullText'][:500])

    # 保存结果
    output_path = Path(image_path).with_suffix('.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 结果已保存到: {output_path}")


if __name__ == "__main__":
    main()






