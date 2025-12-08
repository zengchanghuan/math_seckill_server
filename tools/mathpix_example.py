#!/usr/bin/env python3
"""
Mathpix API 使用示例

演示如何使用 mathpix_config 模块调用 Mathpix API
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mathpix_config import get_config, check_config
import requests
import json


def convert_image_to_markdown(image_url: str) -> dict:
    """
    将图片转换为 Markdown 格式
    
    参数:
        image_url: 图片 URL 或 base64 编码的图片
    
    返回:
        API 响应字典
    """
    config = get_config()
    
    if not config.is_configured():
        raise ValueError("Mathpix API 未配置")
    
    # 构建请求
    payload = {
        "src": image_url,
        "formats": ["text", "mathml"]
    }
    
    # 发送请求
    response = requests.post(
        config.api_url,
        headers=config.get_headers(),
        json=payload,
        timeout=config.timeout
    )
    
    # 检查响应
    response.raise_for_status()
    return response.json()


def convert_pdf_to_markdown(pdf_url: str) -> dict:
    """
    将 PDF 转换为 Markdown 格式
    
    参数:
        pdf_url: PDF 文件 URL 或 base64 编码的 PDF
    
    返回:
        API 响应字典
    """
    config = get_config()
    
    if not config.is_configured():
        raise ValueError("Mathpix API 未配置")
    
    # 构建请求（PDF 需要指定格式）
    payload = {
        "src": pdf_url,
        "formats": ["text", "mathml"],
        "pdf": {
            "include_text": True,
            "include_images": True
        }
    }
    
    # 发送请求
    response = requests.post(
        config.api_url,
        headers=config.get_headers(),
        json=payload,
        timeout=config.timeout
    )
    
    # 检查响应
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    """主函数"""
    print("🔍 检查 Mathpix API 配置...")
    
    if not check_config():
        print("\n❌ 配置检查失败，请先配置 .env 文件")
        sys.exit(1)
    
    config = get_config()
    print(f"✅ 配置有效: {config}")
    print(f"\n📝 使用示例：")
    print("\n1. 转换图片为 Markdown：")
    print("""
    result = convert_image_to_markdown("https://example.com/math.png")
    print(result["text"])
    """)
    
    print("\n2. 转换 PDF 为 Markdown：")
    print("""
    result = convert_pdf_to_markdown("https://example.com/math.pdf")
    print(result["text"])
    """)
    
    print("\n💡 提示：")
    print("- 确保图片/PDF URL 可公开访问，或使用 base64 编码")
    print("- 查看 API 响应中的 'text' 字段获取 Markdown 结果")
