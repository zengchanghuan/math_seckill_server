from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import ProblemRequest, ProblemResponse, GradeRequest, GradeResponse
from core.problem_generator import generate_problem
from core.grading import grade_problem

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



