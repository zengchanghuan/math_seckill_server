"""
PDF页面提取器
将PDF文件的每一页转换为高分辨率图片
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import List
import json


class PDFExtractor:
    def __init__(self, pdf_path: str, output_dir: str = "temp/pdf_images"):
        """
        初始化PDF提取器

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
        """
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 打开PDF
        self.doc = fitz.open(str(self.pdf_path))
        self.page_count = len(self.doc)

        print(f"✅ 已加载PDF: {self.pdf_path.name}")
        print(f"📄 总页数: {self.page_count}")

    def extract_page(self, page_num: int, dpi: int = 300) -> str:
        """
        提取单页为图片

        Args:
            page_num: 页码（从0开始）
            dpi: 分辨率（推荐300）

        Returns:
            图片文件路径
        """
        if page_num >= self.page_count:
            raise ValueError(f"页码超出范围: {page_num} >= {self.page_count}")

        # 获取页面
        page = self.doc[page_num]

        # 设置缩放矩阵（控制分辨率）
        zoom = dpi / 72  # 72是PDF的默认DPI
        mat = fitz.Matrix(zoom, zoom)

        # 渲染为图片
        pix = page.get_pixmap(matrix=mat)

        # 保存
        image_path = self.output_dir / f"page_{page_num + 1}.png"
        pix.save(str(image_path))

        print(f"  ✓ 第{page_num + 1}页 → {image_path.name}")

        return str(image_path)

    def extract_all_pages(self, dpi: int = 300) -> List[str]:
        """
        提取所有页面

        Returns:
            所有图片路径列表
        """
        print(f"\n开始提取所有页面（DPI={dpi}）...")

        image_paths = []
        for page_num in range(self.page_count):
            image_path = self.extract_page(page_num, dpi)
            image_paths.append(image_path)

        print(f"\n✅ 提取完成！共{len(image_paths)}页")

        # 保存元数据
        metadata = {
            "pdfFile": str(self.pdf_path),
            "pageCount": self.page_count,
            "dpi": dpi,
            "images": image_paths
        }

        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return image_paths

    def get_page_text(self, page_num: int) -> str:
        """
        提取页面文本（PyMuPDF内置，用于对比）

        Args:
            page_num: 页码

        Returns:
            页面文本
        """
        page = self.doc[page_num]
        return page.get_text()

    def close(self):
        """关闭PDF文档"""
        self.doc.close()


def main():
    """示例用法"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python pdf_extractor.py <pdf文件路径>")
        print("示例: python pdf_extractor.py sample.pdf")
        return

    pdf_path = sys.argv[1]

    # 创建提取器
    extractor = PDFExtractor(pdf_path)

    try:
        # 提取所有页面
        images = extractor.extract_all_pages(dpi=300)

        print(f"\n📊 提取结果：")
        print(f"  - 输出目录: {extractor.output_dir}")
        print(f"  - 图片数量: {len(images)}")
        print(f"  - 元数据: metadata.json")

        # 显示第一页的文本预览
        if extractor.page_count > 0:
            print(f"\n📝 第1页文本预览（PyMuPDF提取）:")
            text = extractor.get_page_text(0)
            print(text[:200] + "..." if len(text) > 200 else text)

    finally:
        extractor.close()


if __name__ == "__main__":
    main()

