from pydantic import BaseModel
from typing import List, Literal


class ProblemRequest(BaseModel):
    topic: str = "导数基础"
    difficulty: Literal["L1", "L2", "L3"] = "L1"  # 更新为新难度体系
    chapter: str | None = None  # 章节，例如 "第1章 三角函数"
    section: str | None = None  # 节，例如 "§1.1 三角函数的概念"
    type: Literal["choice", "fill", "solution"] | None = None  # 题型，可选


class ProblemResponse(BaseModel):
    id: str
    topic: str
    difficulty: Literal["L1", "L2", "L3"]  # 更新为新难度体系
    type: Literal["choice", "fill", "solution"]  # 题型：选择题/填空题/解答题
    question: str
    answer: str
    solution: str
    options: List[str]  # 选择题必填，其他题型为空列表
    tags: List[str] = []
    chapter: str | None = None
    section: str | None = None
    answerType: Literal["integer", "float", "expr"] | None = None  # 填空题和解答题使用
    answerExpr: str | None = None  # SymPy表达式字符串，用于判分


class GradeRequest(BaseModel):
    """判分请求"""
    problemId: str
    userAnswer: str
    problemType: Literal["choice", "fill", "solution"]
    answerType: Literal["integer", "float", "expr"] | None = None
    correctAnswer: str  # 正确答案
    correctAnswerExpr: str | None = None  # 正确答案的SymPy表达式


class GradeResponse(BaseModel):
    """判分响应"""
    isCorrect: bool
    explanation: str | None = None



