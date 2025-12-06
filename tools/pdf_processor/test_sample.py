#!/usr/bin/env python3
"""
PDF处理工具测试脚本
用于测试完整的PDF → OCR → 切分流程
"""
import sys
from pathlib import Path

# 检查依赖
try:
    import fitz
    print("✅ PyMuPDF已安装")
except ImportError:
    print("❌ PyMuPDF未安装，请运行: pip install PyMuPDF")
    sys.exit(1)

try:
    import pytesseract
    pytesseract.get_tesseract_version()
    print("✅ Tesseract已安装")
except:
    print("❌ Tesseract未安装")
    print("macOS: brew install tesseract tesseract-lang")
    print("Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")
    sys.exit(1)

try:
    import cv2
    print("✅ OpenCV已安装")
except ImportError:
    print("❌ OpenCV未安装，请运行: pip install opencv-python")
    sys.exit(1)

print("\n✅ 所有依赖已安装，可以开始使用！")
print("\n📝 使用示例：")
print("  1. 提取PDF: python pdf_extractor.py sample.pdf")
print("  2. OCR识别: python ocr_engine.py temp/pdf_images/page_1.png")
print("  3. 切分题目: python question_splitter.py temp/pdf_images/page_1.json")
print("\n💡 提示：将PDF文件放在当前目录，然后运行上述命令")





