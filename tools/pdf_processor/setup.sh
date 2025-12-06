#!/bin/bash

echo "🚀 PDF处理工具环境设置"
echo ""

# 检查Tesseract
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract已安装"
    tesseract --version | head -1
else
    echo "❌ Tesseract未安装"
    echo "macOS安装命令: brew install tesseract tesseract-lang"
    echo "Ubuntu安装命令: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim"
    echo ""
fi

# 安装Python依赖
echo ""
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

echo ""
echo "✅ 设置完成！"
echo ""
echo "📝 使用示例："
echo "  python3 pdf_extractor.py sample.pdf"
echo "  python3 ocr_engine.py temp/pdf_images/page_1.png"
echo "  python3 question_splitter.py temp/pdf_images/page_1.json"





