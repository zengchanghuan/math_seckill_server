from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

from schemas import (
    ProblemRequest, ProblemResponse,
    QuestionMetadata, AnswerSubmission, AnswerRecord,
    QualityStatsUpdate, StudentProfile,
    RecommendationRequest, RecommendationResponse,
    ReviewRequest
)
from core.problem_generator import generate_problem
from core.question_bank import question_bank
from core.answer_tracker import answer_tracker
from core.recommender import ProblemRecommender

app = FastAPI(title="Math Seckill CAS Backend")

# 允许本地 Flutter 调试访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化推荐器
recommender = ProblemRecommender(question_bank, answer_tracker)


# ========== 基础接口 ==========

@app.get("/")
async def root():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/api/problem", response_model=ProblemResponse)
async def create_problem(request: ProblemRequest) -> ProblemResponse:
    """生成题目（保持向后兼容）"""
    data = generate_problem(request.topic, request.difficulty)
    return ProblemResponse(**data)


# ========== 题库管理接口 ==========

@app.get("/api/questions/stats")
async def get_question_stats():
    """获取题库统计信息"""
    return question_bank.get_statistics()


@app.get("/api/questions/{question_id}", response_model=QuestionMetadata)
async def get_question(question_id: str):
    """获取单个题目"""
    question = question_bank.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question


@app.post("/api/questions", response_model=QuestionMetadata)
async def create_question(question: QuestionMetadata):
    """创建题目"""
    try:
        return question_bank.add(question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/questions/{question_id}", response_model=QuestionMetadata)
async def update_question(question_id: str, question: QuestionMetadata):
    """更新题目"""
    if question_id != question.questionId:
        raise HTTPException(status_code=400, detail="题目ID不匹配")
    
    try:
        return question_bank.update(question)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: str):
    """删除题目"""
    success = question_bank.delete(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"success": True}


# ========== 作答记录接口 ==========

@app.post("/api/answers/submit")
async def submit_answer(submission: AnswerSubmission):
    """提交答案"""
    # 创建作答记录
    record = AnswerRecord(
        recordId=str(uuid.uuid4()),
        studentId=submission.studentId,
        questionId=submission.questionId,
        userAnswer=submission.userAnswer,
        isCorrect=False,  # 需要调用判分逻辑
        timeSpent=submission.timeSpent,
        answeredAt=datetime.now()
    )
    
    # TODO: 这里应该调用判分逻辑，暂时先标记为False
    # 可以集成之前的grading.py
    
    answer_tracker.add_record(record)
    
    return {
        "success": True,
        "recordId": record.recordId,
        "isCorrect": record.isCorrect
    }


@app.get("/api/answers/student/{student_id}")
async def get_student_answers(student_id: str):
    """获取学生的所有作答记录"""
    records = answer_tracker.get_student_records(student_id)
    return {"total": len(records), "records": records}


# ========== 质量统计接口 ==========

@app.post("/api/admin/question/update-stats")
async def update_question_stats(update: QualityStatsUpdate):
    """更新题目质量统计"""
    try:
        question_bank.update_quality_stats(update.questionId, update.stats)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/admin/question/{question_id}/stats")
async def get_question_stats_detail(question_id: str):
    """获取题目质量统计"""
    stats = answer_tracker.calculate_question_stats(question_id)
    return stats


# ========== 学生画像接口 ==========

@app.get("/api/student/{student_id}/profile", response_model=StudentProfile)
async def get_student_profile(student_id: str):
    """获取学生能力画像"""
    profile = answer_tracker.calculate_student_profile(student_id, question_bank)
    return profile


# ========== 个性化推荐接口 ==========

@app.post("/api/student/recommend", response_model=RecommendationResponse)
async def recommend_problems(request: RecommendationRequest):
    """个性化推荐题目"""
    problems, reason = recommender.recommend(
        student_id=request.studentId,
        mode=request.mode,
        count=request.count
    )
    
    return RecommendationResponse(
        questions=problems,
        recommendationReason=reason
    )


# ========== 审核接口 ==========

@app.post("/api/admin/review")
async def review_question(review: ReviewRequest):
    """审核题目"""
    question = question_bank.get(review.questionId)
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    question.reviewStatus = review.status
    question.reviewerId = review.reviewerId
    question.reviewComment = review.comment
    
    question_bank.update(question)
    
    return {"success": True}



