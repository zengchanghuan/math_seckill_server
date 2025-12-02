from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import ProblemRequest, ProblemResponse
from core.problem_generator import generate_problem

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
    data = generate_problem(request.topic, request.difficulty)
    return ProblemResponse(**data)



