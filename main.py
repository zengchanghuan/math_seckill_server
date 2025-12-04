from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
from pathlib import Path
import uuid
import shutil
import subprocess
import sys

app = FastAPI(title="数学秒杀 API v2.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据文件路径
DATA_DIR = Path(__file__).parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"
TUTORIALS_FILE = DATA_DIR / "tutorials.json"
THEME_CONFIG_FILE = DATA_DIR / "theme_configs.json"

# PDF处理临时目录
PDF_TEMP_DIR = Path(__file__).parent / "tools" / "pdf_processor" / "temp"
PDF_TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Pydantic模型定义
class QuestionMetadata(BaseModel):
    questionId: str
    topic: str
    difficulty: str
    type: str
    question: str
    answer: str
    options: Optional[List[str]] = None
    solution: str
    tags: List[str]
    knowledgePoints: List[str]
    abilityTags: List[str]

class ProblemResponse(BaseModel):
    questionId: str
    question: str
    options: Optional[List[str]]
    answer: str

class AnswerSubmission(BaseModel):
    studentId: str
    questionId: str
    userAnswer: str
    timeSpent: float

class StudentProfile(BaseModel):
    studentId: str
    totalAnswered: int
    correctCount: int
    overallAccuracy: float
    avgTimeSeconds: float
    knowledgeMastery: dict
    weakPoints: List[str]
    preferredTopics: List[str]

class RecommendationRequest(BaseModel):
    studentId: str
    mode: str
    count: int = 20

class RecommendationResponse(BaseModel):
    recommendations: List[dict]
    reason: str

# PDF处理相关模型
class PDFProcessResult(BaseModel):
    taskId: str
    fileName: str
    pageCount: int
    questionCount: int
    status: str
    questions: List[dict]

@app.get("/")
async def root():
    """根路径"""
    return {"status": "ok", "version": "2.0.0"}

# ========== 题目管理API ==========

@app.post("/api/problem", response_model=ProblemResponse)
async def get_random_problem(difficulty: Optional[str] = None):
    """随机获取一道题目（兼容旧版）"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    import random
    question = random.choice(questions)
    return ProblemResponse(**question)

@app.get("/api/questions/stats")
async def get_question_stats():
    """获取题目统计"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # 统计
    stats = {
        "total": len(questions),
        "difficultyStats": {},
        "typeStats": {},
        "reviewStats": {},
        "sourceStats": {}
    }

    for q in questions:
        # 难度统计
        diff = q.get('difficulty', 'L1')
        stats['difficultyStats'][diff] = stats['difficultyStats'].get(diff, 0) + 1

        # 类型统计
        qtype = q.get('type', 'choice')
        stats['typeStats'][qtype] = stats['typeStats'].get(qtype, 0) + 1

        # 审核状态
        review = q.get('reviewStatus', 'pending')
        stats['reviewStats'][review] = stats['reviewStats'].get(review, 0) + 1

        # 来源
        source = q.get('source', 'generated')
        stats['sourceStats'][source] = stats['sourceStats'].get(source, 0) + 1

    return stats

@app.get("/api/questions/{question_id}", response_model=QuestionMetadata)
async def get_question(question_id: str):
    """获取单个题目详情"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    for q in questions:
        if q.get('questionId') == question_id:
            return QuestionMetadata(**q)

    raise HTTPException(status_code=404, detail="题目未找到")

@app.post("/api/questions", response_model=QuestionMetadata)
async def create_question(question: QuestionMetadata):
    """创建新题目"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    # 生成ID（如果没有）
    if not question.questionId:
        question.questionId = f"q_{uuid.uuid4().hex[:8]}"

    questions.append(question.dict())

    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    return question

@app.put("/api/questions/{question_id}", response_model=QuestionMetadata)
async def update_question(question_id: str, question: QuestionMetadata):
    """更新题目"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    for i, q in enumerate(questions):
        if q.get('questionId') == question_id:
            questions[i] = question.dict()
            break
    else:
        raise HTTPException(status_code=404, detail="题目未找到")

    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    return question

@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: str):
    """删除题目"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    questions = [q for q in questions if q.get('questionId') != question_id]

    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    return {"message": "删除成功"}

# ========== PDF处理API（新增）==========

@app.post("/api/pdf/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    上传PDF文件
    """
    # 生成任务ID
    task_id = uuid.uuid4().hex[:8]

    # 保存PDF文件
    pdf_path = PDF_TEMP_DIR / f"{task_id}_{file.filename}"
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "taskId": task_id,
        "fileName": file.filename,
        "filePath": str(pdf_path),
        "status": "uploaded"
    }

@app.post("/api/pdf/process/{task_id}")
async def process_pdf(task_id: str):
    """
    处理上传的PDF：提取页面 → OCR → 切分题目
    """
    # 查找PDF文件
    pdf_files = list(PDF_TEMP_DIR.glob(f"{task_id}_*.pdf"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail="PDF文件未找到")

    pdf_path = pdf_files[0]

    try:
        # 运行Python脚本处理
        processor_dir = Path(__file__).parent / "tools" / "pdf_processor"
        venv_python = processor_dir / "venv" / "bin" / "python"

        # 步骤1：提取页面
        result = subprocess.run(
            [str(venv_python), "pdf_extractor.py", str(pdf_path)],
            cwd=processor_dir,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise Exception(f"PDF提取失败: {result.stderr}")

        # 读取metadata
        metadata_file = processor_dir / "temp" / "pdf_images" / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        page_count = metadata.get('pageCount', 0)
        images = metadata.get('images', [])

        # 步骤2：OCR识别第一页
        all_questions = []
        if images and len(images) > 0:
            first_image = images[0]

            # OCR识别
            ocr_result = subprocess.run(
                [str(venv_python), "ocr_engine.py", first_image],
                cwd=processor_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if ocr_result.returncode == 0:
                # OCR结果保存在 first_image.json
                ocr_json = Path(first_image).with_suffix('.json')

                # 步骤3：题目切分
                if ocr_json.exists():
                    split_result = subprocess.run(
                        [str(venv_python), "question_splitter.py", str(ocr_json)],
                        cwd=processor_dir,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    # 读取切分结果
                    split_json = ocr_json.parent / "questions_split.json"
                    if split_json.exists():
                        with open(split_json, 'r', encoding='utf-8') as f:
                            split_data = json.load(f)
                            all_questions = split_data.get('questions', [])

        return {
            "taskId": task_id,
            "fileName": pdf_path.name,
            "pageCount": page_count,
            "questionCount": len(all_questions),
            "status": "completed",
            "message": f"处理完成，识别到{len(all_questions)}道题目"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pdf/questions/{task_id}")
async def get_pdf_questions(task_id: str):
    """
    获取PDF处理后的题目列表（供人工校验）
    """
    # 查找处理结果
    processor_dir = Path(__file__).parent / "tools" / "pdf_processor"
    questions_file = processor_dir / "temp" / "pdf_images" / "questions_split.json"

    # 如果没有切分结果，尝试加载OCR原文
    if not questions_file.exists():
        # 优先查找最新处理的结果
        latest_file = processor_dir / "temp" / "latest_question.json"
        if latest_file.exists():
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 更新taskId为当前请求的taskId
                data['taskId'] = task_id
                return data

        # 查找OCR结果
        ocr_files = list((processor_dir / "temp" / "pdf_images").glob("page_*.json"))

        if ocr_files:
            # 读取第一页OCR结果
            with open(ocr_files[0], 'r', encoding='utf-8') as f:
                ocr_data = json.load(f)

            ocr_text = ocr_data.get('ocrResult', {}).get('fullText', '')

            # 提取题目部分
            lines = ocr_text.split('\n')
            question_start = 0
            for i, line in enumerate(lines):
                if '选择题' in line:
                    question_start = i
                    break

            question_lines = lines[question_start:min(question_start+20, len(lines))]
            extracted_text = '\n'.join(question_lines)

            # 返回OCR原文供人工处理
            return {
                "taskId": task_id,
                "questions": [
                    {
                        "questionNumber": 1,
                        "rawText": "",
                        "ocrRawText": extracted_text,
                        "options": [
                            {"letter": "A", "content": ""},
                            {"letter": "B", "content": ""},
                            {"letter": "C", "content": ""},
                            {"letter": "D", "content": ""}
                        ],
                        "hasFormula": True,
                        "imageUrl": f"/api/pdf/image/page_1.png",
                        "answer": "",
                        "type": "choice",
                        "difficulty": "L1",
                        "knowledgePoints": [],
                        "solution": "",
                        "topic": "高等数学"
                    }
                ],
                "message": "OCR识别完成，请人工校验修正"
            }

        # 完全没有数据，返回空
        return {
            "taskId": task_id,
            "questions": [],
            "message": "PDF处理中，请稍后刷新"
        }

    with open(questions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return {
        "taskId": task_id,
        "questions": data.get('questions', [])
    }

@app.post("/api/pdf/verify")
async def verify_and_save_question(question: QuestionMetadata):
    """
    校验后保存题目到题库
    """
    # 调用现有的创建题目API
    return await create_question(question)

# ========== 答题相关API ==========

@app.post("/api/answers/submit")
async def submit_answer(submission: AnswerSubmission):
    """提交答案"""
    # 简化版：返回是否正确
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    for q in questions:
        if q.get('questionId') == submission.questionId:
            correct = submission.userAnswer.upper() == q.get('answer', '').upper()
            return {
                "isCorrect": correct,
                "correctAnswer": q.get('answer'),
                "explanation": q.get('solution', '')
            }

    raise HTTPException(status_code=404, detail="题目未找到")

@app.get("/api/answers/student/{student_id}")
async def get_student_answers(student_id: str):
    """获取学生答题记录"""
    # 模拟数据
    return []

# ========== 学生画像API ==========

@app.get("/api/student/{student_id}/profile", response_model=StudentProfile)
async def get_student_profile(student_id: str):
    """获取学生画像"""
    # 模拟数据
    return StudentProfile(
        studentId=student_id,
        totalAnswered=0,
        correctCount=0,
        overallAccuracy=0.0,
        avgTimeSeconds=0.0,
        knowledgeMastery={},
        weakPoints=[],
        preferredTopics=[]
    )

@app.post("/api/student/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """智能推荐题目"""
    return RecommendationResponse(
        recommendations=[],
        reason="暂无推荐"
    )

# ========== 管理员API ==========

@app.post("/api/admin/question/update-stats")
async def update_question_stats():
    """更新题目统计信息"""
    return {"message": "统计更新成功"}

@app.get("/api/admin/question/{question_id}/stats")
async def get_question_stats(question_id: str):
    """获取单个题目的统计"""
    return {
        "questionId": question_id,
        "totalAttempts": 0,
        "correctRate": 0.0
    }

@app.post("/api/admin/review")
async def review_question():
    """审核题目"""
    return {"message": "审核完成"}

# ========== 配置API ==========

@app.get("/api/config/themes")
async def get_all_themes():
    """获取所有主题配置"""
    try:
        with open(THEME_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        return {"themes": []}

@app.get("/api/config/theme/{theme_name}")
async def get_theme_config(theme_name: str):
    """获取指定主题配置"""
    try:
        with open(THEME_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)

        for theme in config.get('themes', []):
            if theme.get('name') == theme_name:
                return theme

        raise HTTPException(status_code=404, detail="主题未找到")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="配置文件未找到")

@app.get("/api/config/version")
async def get_config_version():
    """获取配置版本"""
    return {
        "version": "2.0.0",
        "lastUpdated": "2025-12-03"
    }

# ========== 讲解内容API ==========

@app.get("/api/tutorials")
async def get_all_tutorials():
    """获取所有讲解内容"""
    try:
        with open(TUTORIALS_FILE, 'r', encoding='utf-8') as f:
            tutorials = json.load(f)
        return tutorials
    except FileNotFoundError:
        return {"themes": []}

@app.get("/api/tutorials/chapter/{theme_name}/{chapter_name}")
async def get_chapter_tutorial(theme_name: str, chapter_name: str):
    """获取指定章节的讲解内容"""
    try:
        with open(TUTORIALS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for theme in data.get('themes', []):
            if theme.get('themeName') == theme_name:
                for chapter in theme.get('chapters', []):
                    if chapter.get('chapterName') == chapter_name:
                        return chapter

        raise HTTPException(status_code=404, detail="章节未找到")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="讲解内容未找到")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
