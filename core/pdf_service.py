"""
PDF处理服务
提供PDF上传、预处理、题目提取的API服务
"""
from fastapi import UploadFile, HTTPException
from pathlib import Path
import shutil
import json
import subprocess
from typing import List, Dict
import uuid


class PDFService:
    def __init__(self):
        """初始化PDF服务"""
        self.upload_dir = Path("data/pdf_uploads")
        self.temp_dir = Path("tools/pdf_processor/temp")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # 虚拟环境Python路径
        self.python_path = "tools/pdf_processor/venv/bin/python"

    async def save_uploaded_file(self, file: UploadFile) -> str:
        """
        保存上传的PDF文件

        Returns:
            文件路径
        """
        # 生成唯一文件名
        file_id = str(uuid.uuid4())[:8]
        file_name = f"{file_id}_{file.filename}"
        file_path = self.upload_dir / file_name

        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return str(file_path)

    def extract_pages(self, pdf_path: str) -> Dict:
        """
        提取PDF页面为图片

        Returns:
            提取结果
        """
        try:
            # 调用pdf_extractor.py
            result = subprocess.run(
                [self.python_path, "tools/pdf_processor/pdf_extractor.py", pdf_path],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            if result.returncode != 0:
                raise Exception(f"PDF提取失败: {result.stderr}")

            # 读取metadata
            metadata_path = self.temp_dir / "pdf_images" / "metadata.json"
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            return {
                "success": True,
                "pageCount": metadata.get("pageCount", 0),
                "images": metadata.get("images", [])
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF提取失败: {str(e)}")

    def ocr_page(self, image_path: str) -> Dict:
        """
        对页面图片进行OCR识别

        Returns:
            OCR结果
        """
        try:
            # 调用ocr_engine.py
            result = subprocess.run(
                [self.python_path, "tools/pdf_processor/ocr_engine.py", image_path],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise Exception(f"OCR识别失败: {result.stderr}")

            # 读取OCR结果
            json_path = Path(image_path).with_suffix('.json')
            with open(json_path, 'r') as f:
                ocr_result = json.load(f)

            return ocr_result

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")

    def split_questions(self, ocr_json_path: str) -> Dict:
        """
        切分题目

        Returns:
            题目列表
        """
        try:
            # 调用question_splitter.py
            result = subprocess.run(
                [self.python_path, "tools/pdf_processor/question_splitter.py", ocr_json_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise Exception(f"题目切分失败: {result.stderr}")

            # 读取切分结果
            split_path = Path(ocr_json_path).with_name('questions_split.json')
            with open(split_path, 'r') as f:
                split_result = json.load(f)

            return split_result

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"题目切分失败: {str(e)}")

    async def process_pdf(self, file: UploadFile) -> Dict:
        """
        完整处理PDF文件

        Returns:
            处理结果
        """
        # 1. 保存文件
        pdf_path = await self.save_uploaded_file(file)

        # 2. 提取页面
        extract_result = self.extract_pages(pdf_path)

        # 3. OCR + 切分每一页
        all_questions = []
        images = extract_result.get("images", [])

        for i, image_path in enumerate(images):
            # OCR识别
            ocr_result = self.ocr_page(image_path)

            # 保存OCR结果
            ocr_json = Path(image_path).with_suffix('.json')

            # 题目切分
            split_result = self.split_questions(str(ocr_json))

            # 添加图片路径
            for question in split_result.get("questions", []):
                question["imagePath"] = image_path
                question["pageNumber"] = i + 1
                all_questions.append(question)

        return {
            "success": True,
            "fileName": file.filename,
            "pageCount": extract_result["pageCount"],
            "questionCount": len(all_questions),
            "questions": all_questions
        }


# 全局实例
pdf_service = PDFService()

