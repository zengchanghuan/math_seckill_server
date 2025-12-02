from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import ProblemRequest, ProblemResponse, GradeRequest, GradeResponse
from models import CreateInstanceRequest, CreateInstanceResponse, Question
from core.problem_generator import generate_problem
from core.grading import grade_problem
from core.instance_manager import get_instance_manager
from core.question_bank import get_question_bank

app = FastAPI(title="Math Seckill CAS Backend")

# 允许本地 Flutter 调试访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/api/problem", response_model=ProblemResponse)
async def create_problem(request: ProblemRequest) -> ProblemResponse:
    data = generate_problem(
        request.topic,
        request.difficulty,
        chapter=request.chapter,
        section=request.section,
        problem_type=request.type
    )
    return ProblemResponse(**data)


@app.post("/api/grade", response_model=GradeResponse)
async def grade_answer(request: GradeRequest) -> GradeResponse:
    """
    判分接口
    
    接收用户答案，返回判分结果
    """
    is_correct, explanation = grade_problem(
        problem_type=request.problemType,
        user_answer=request.userAnswer,
        correct_answer=request.correctAnswer,
        answer_type=request.answerType,
        correct_answer_expr=request.correctAnswerExpr
    )
    
    return GradeResponse(
        isCorrect=is_correct,
        explanation=explanation
    )


@app.post("/api/instance/create", response_model=CreateInstanceResponse)
async def create_training_instance(request: CreateInstanceRequest) -> CreateInstanceResponse:
    """
    创建训练实例
    
    根据用户配置，从题库中选题并创建训练实例
    """
    instance_manager = get_instance_manager()
    
    try:
        instance, questions = instance_manager.create_instance(request)
        
        return CreateInstanceResponse(
            instance=instance,
            questions=questions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建实例失败: {str(e)}")


@app.get("/api/instance/{instance_id}")
async def get_training_instance(instance_id: str):
    """
    获取训练实例及其题目
    """
    instance_manager = get_instance_manager()
    question_bank = get_question_bank()
    
    instance = instance_manager.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="实例不存在")
    
    # 获取所有题目
    all_question_ids = []
    for section in instance.sections:
        all_question_ids.extend(section.questionIds)
    
    questions = []
    for qid in all_question_ids:
        q = question_bank.get_question_by_id(qid)
        if q:
            questions.append(q)
    
    return {
        "instance": instance,
        "questions": questions
    }



